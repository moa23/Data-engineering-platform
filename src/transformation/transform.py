
from pathlib import Path

import pandas as pd
import logging

logger = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
BRONZE_DIR = PROJECT_ROOT / "data" / "bronze"
SILVER_DIR = PROJECT_ROOT / "data" / "silver"

REQUIRED_COLUMNS = [
    "ticker",
    "Date",
    "Open",
    "High",
    "Low",
    "Close",
    "Volume",
]



def transform_stock_data(
    input_path: Path | None = None,
) -> Path:
    """Validate and clean raw stock data into the Silver layer."""
    if input_path is None:
        input_path = BRONZE_DIR / "aapl_historical.csv"

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    data = pd.read_csv(input_path)
    rows_read = len(data)
    logger.info("Read %s rows from Bronze", rows_read)

    missing_columns = set(REQUIRED_COLUMNS) - set(data.columns)
    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    data = data[REQUIRED_COLUMNS].copy()

    data["Date"] = pd.to_datetime(
        data["Date"], errors="coerce", utc=True
    )

    numeric_columns = ["Open", "High", "Low", "Close", "Volume"]
    for column in numeric_columns:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    before_dropna = len(data)
    data = data.dropna(subset=REQUIRED_COLUMNS)
    logger.info(
        "Removed %s rows with missing or invalid required values",
        before_dropna - len(data),
    )

    before_duplicates = len(data)
    data = data.drop_duplicates(subset=["ticker", "Date"])
    logger.info(
        "Removed %s duplicate rows",
        before_duplicates - len(data),
    )

    invalid_prices = (
        (data[["Open", "High", "Low", "Close"]] <= 0).any(axis=1)
        | (data["Volume"] < 0)
        | (data["High"] < data["Low"])
        | (data["High"] < data["Open"])
        | (data["High"] < data["Close"])
        | (data["Low"] > data["Open"])
        | (data["Low"] > data["Close"])
    )

    invalid_count = int(invalid_prices.sum())
    data = data.loc[~invalid_prices].copy()

    logger.info(
        "Removed %s rows with invalid prices or volume",
        invalid_count,
    )

    data = data.sort_values(
        ["ticker", "Date"]
    ).reset_index(drop=True)

    SILVER_DIR.mkdir(parents=True, exist_ok=True)
    output_path = SILVER_DIR / "stock_prices.csv"
    data.to_csv(output_path, index=False)

    logger.info(
        "Silver layer complete: %s of %s rows retained",
        len(data),
        rows_read,
    )
    logger.info("Saved Silver data to %s", output_path)

    return output_path



if __name__ == "__main__":
    transform_stock_data()
