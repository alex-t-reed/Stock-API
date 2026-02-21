"""
app.py — Stock Price REST API built with FastAPI.

Endpoints:
  GET  /stocks/{symbol}          → single stock price
  GET  /stocks?symbols=A,B,C     → batch prices
"""

from __future__ import annotations

import asyncio
import time
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from stock_api import get_stock_price


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Stock API starting up…")
    yield
    print("Stock API shutting down…")


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Stock Price API",
    description="Fetches real-time stock prices via Yahoo Finance / CNN Markets.",
    version="1.0.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class PriceResponse(BaseModel):
    symbol: str
    price: float
    currency: str = "USD"
    fetched_at: float  # Unix timestamp


class BatchPriceResponse(BaseModel):
    results: list[PriceResponse]
    errors: dict[str, str]  # symbol → error message


class HealthResponse(BaseModel):
    status: str


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health", response_model=HealthResponse, tags=["Meta"])
async def health() -> HealthResponse:
    """Simple liveness check."""
    return HealthResponse(status="ok")


@app.get("/stocks/{symbol}", response_model=PriceResponse, tags=["Stocks"])
async def get_price(symbol: str) -> PriceResponse:
    """Return the current price for a single *symbol*, e.g. ``AAPL``.

    - **symbol**: Ticker symbol (case-insensitive)
    """
    symbol = symbol.upper()
    try:
        price = await asyncio.to_thread(get_stock_price, symbol)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return PriceResponse(symbol=symbol, price=price, fetched_at=time.time())


@app.get("/stocks", response_model=BatchPriceResponse, tags=["Stocks"])
async def get_prices_batch(
    symbols: Annotated[
        str,
        Query(description="Comma-separated ticker symbols, e.g. ``AAPL,GOOGL,TSLA``"),
    ],
) -> BatchPriceResponse:
    """Return prices for multiple symbols in one call.

    Fetches all symbols concurrently — much faster than sequential requests.
    Symbols that fail are collected in ``errors`` rather than aborting the
    whole batch.
    """
    tickers = [s.strip().upper() for s in symbols.split(",") if s.strip()]
    if not tickers:
        raise HTTPException(status_code=400, detail="No symbols provided.")

    results: list[PriceResponse] = []
    errors: dict[str, str] = {}

    async def fetch(symbol: str) -> None:
        try:
            price = await asyncio.to_thread(get_stock_price, symbol)
            results.append(PriceResponse(symbol=symbol, price=price, fetched_at=time.time()))
        except (ValueError, RuntimeError) as exc:
            errors[symbol] = str(exc)

    await asyncio.gather(*[fetch(ticker) for ticker in tickers])

    return BatchPriceResponse(results=sorted(results, key=lambda r: r.symbol), errors=errors)
