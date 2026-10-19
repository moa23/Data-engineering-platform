
from pathlib import Path

import pandas as pd
import yfinance as yf



PROJECT_ROOT = Path(__file__).resolve().parents[2]
BRONZE_DIR = PROJECT_ROOT / "data" / "bronze"


def extract_stock_data(
    ticker: str = "AAPL",
    period: str = "1y",
) -> Path:
    """Download historical stock data and save it to the Bronze layer."""
    BRONZE_DIR.mkdir(parents=True, exist_ok=True)

    stock = yf.Ticker(ticker)
    data = stock.history(period=period, auto_adjust=False)

    if data.empty:
        raise ValueError(f"No stock data returned for ticker: {ticker}")

    data = data.reset_index()
    data.insert(0, "ticker", ticker)

    output_path = BRONZE_DIR / f"{ticker.lower()}_historical.csv"
    data.to_csv(output_path, index=False)

    print(f"Extracted {len(data)} rows for {ticker}")
    print(f"Saved raw data to: {output_path}")

    return output_path


if __name__ == "__main__":
    extract_stock_data()
