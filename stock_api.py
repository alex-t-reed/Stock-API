"""
stock_api.py — Fetch real-time stock prices by scraping Yahoo Finance,
with CNN Markets as a fallback.
"""

from __future__ import annotations

import re

import requests
from bs4 import BeautifulSoup

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/91.0.4472.114 Safari/537.36"
    )
}


def get_stock_price(symbol: str) -> float:
    """Return the current price for *symbol*, or raise if unavailable.

    Scraping order:
      1. Yahoo Finance (CSS selector)
      2. Yahoo Finance (JSON regex fallback)
      3. CNN Markets  (CSS selector)
      4. CNN Markets  (JSON regex fallback)

    Args:
        symbol: Ticker symbol, e.g. ``"AAPL"``.

    Returns:
        Current stock price as a ``float``.

    Raises:
        ValueError: If *symbol* is empty.
        RuntimeError: If the price cannot be determined from any source.
    """
    if not symbol:
        raise ValueError("symbol must not be empty")

    price = _try_yahoo(symbol) or _try_cnn(symbol)
    if price is not None:
        return price

    raise RuntimeError(f"Could not fetch price for symbol: {symbol!r}")


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _get(url: str) -> requests.Response | None:
    """GET *url* and return the response, or ``None`` on non-200 status."""
    response = requests.get(url, headers=_HEADERS, timeout=10)
    return response if response.ok else None


def _parse_float(text: str) -> float | None:
    """Strip commas/dollar-signs from *text* and coerce to float, or ``None``."""
    try:
        return float(text.replace(",", "").replace("$", ""))
    except (ValueError, AttributeError):
        return None


def _try_yahoo(symbol: str) -> float | None:
    response = _get(f"https://finance.yahoo.com/quote/{symbol}/")
    if response is None:
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # Primary: container CSS selector
    container = soup.select_one("div.container.yf-16vvaki")
    if container and (span := container.find("span")):
        if (price := _parse_float(span.text)) is not None:
            return price

    # Fallback: embedded JSON
    if match := re.search(r'"currentPrice":\{"raw":([0-9.]+),', response.text):
        return _parse_float(match.group(1))

    return None


def _try_cnn(symbol: str) -> float | None:
    response = _get(f"https://www.cnn.com/markets/stocks/{symbol}")
    if response is None:
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # Primary: price div
    if price_div := soup.select_one("div.price-2tP9m2.cnn-pcl-kld3m4"):
        if (price := _parse_float(price_div.text)) is not None:
            return price

    # Fallback: embedded JSON
    if match := re.search(r'"price":\s*"([0-9.,]+)"', response.text):
        return _parse_float(match.group(1))

    return None


__all__ = ["get_stock_price"]
