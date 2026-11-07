# Stock Price REST API

A lightweight REST API built with **FastAPI** that fetches real-time stock prices
by scraping Yahoo Finance, with CNN Markets as a fallback. This is a Python/FastAPI learning project demonstrating API routes, response schemas, validation, and concurrent I/O.

---

## Setup

```bash
pip install -r requirements.txt
```

## Running the server

```bash
uvicorn app:app --reload
```

The API will be available at `http://localhost:8000`.

---

## Endpoints

### `GET /health`
Liveness check.

```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

---

### `GET /stocks/{symbol}`
Fetch the current price for a single ticker.

```bash
curl http://localhost:8000/stocks/AAPL
```

```json
{
  "symbol": "AAPL",
  "price": 189.42,
  "currency": "USD",
  "fetched_at": 1713900000.123
}
```

**Error responses:**
| Status | Reason |
|--------|--------|
| `400`  | Empty or invalid symbol format |
| `404`  | Price could not be fetched (symbol unknown or scraping failed) |

---

### `GET /stocks?symbols=A,B,C`
Fetch prices for multiple tickers in one concurrent request.

```bash
curl "http://localhost:8000/stocks?symbols=AAPL,GOOGL,TSLA"
```

```json
{
  "results": [
    {"symbol": "AAPL",  "price": 189.42, "currency": "USD", "fetched_at": 1713900000.1},
    {"symbol": "GOOGL", "price": 174.11, "currency": "USD", "fetched_at": 1713900000.2},
    {"symbol": "TSLA",  "price": 162.50, "currency": "USD", "fetched_at": 1713900000.3}
  ],
  "errors": {}
}
```

Failed symbols appear in `errors` rather than aborting the whole batch:

```json
{
  "results": [{"symbol": "AAPL", "price": 189.42, ...}],
  "errors": {"BADTICKER": "Could not fetch price for symbol: 'BADTICKER'"}
}
```

---

## Interactive Docs

FastAPI ships with auto-generated docs at:
- **Swagger UI** → `http://localhost:8000/docs`
- **ReDoc**       → `http://localhost:8000/redoc`

---

## Running Tests

```bash
python -m unittest test_stock_api.py
```

---

## Project Structure

```
.
├── app.py            # FastAPI application & routes
├── stock_api.py      # Scraping logic
├── test_stock_api.py # Unit tests
├── requirements.txt
└── README.md
```

## Scope and limitations

Upstream page changes, rate limits, and network failures can break scraping. Returned prices are not guaranteed to be current or suitable for trading. The timestamp indicates when this API fetched a result, not when an exchange published it. This prototype does not include production authentication, rate limiting, or persistent caching. Run the development server locally.

## About and contact

Created by [Alex Reed](https://www.linkedin.com/in/alextreed/). Explore my [portfolio](https://alex-t-reed.github.io/) for project context and career interests. Professional inquiries are welcome through LinkedIn.

## What I learned

I practiced separating retrieval logic from API routes, validating inputs, defining response schemas, and handling failures without losing an entire batch. The project also illustrates the maintenance tradeoff of depending on scraped third-party pages.
