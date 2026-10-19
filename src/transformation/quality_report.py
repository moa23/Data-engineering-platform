
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SILVER_FILE = PROJECT_ROOT / "data" / "silver" / "stock_prices.csv"
REPORT_DIR = PROJECT_ROOT / "data" / "gold"


def build_quality_report() -> Path:
    """Generate a quality report for the Silver dataset."""
    if not SILVER_FILE.exists():
        raise FileNotFoundError(
            f"Silver data not found: {SILVER_FILE}"
        )

    data = pd.read_csv(SILVER_FILE)

    required_columns = [
        "ticker", "Date", "Open", "High",
        "Low", "Close", "Volume",
    ]

    missing_columns = set(required_columns) - set(data.columns)
    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    missing_values = int(data[required_columns].isna().sum().sum())
    duplicate_rows = int(
        data.duplicated(subset=["ticker", "Date"]).sum()
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

    report = pd.DataFrame(
        [
            {"metric": "total_rows", "value": len(data)},
            {"metric": "missing_values", "value": missing_values},
            {"metric": "duplicate_rows", "value": duplicate_rows},
            {"metric": "invalid_price_rows", "value": int(invalid_prices.sum())},
        ]
    )

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = REPORT_DIR / "data_quality_report.csv"
    report.to_csv(output_path, index=False)

    print(report.to_string(index=False))
    print(f"\nQuality report saved to: {output_path}")

    return output_path


if __name__ == "__main__":
    build_quality_report()
