
from pathlib import Path

import duckdb


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SILVER_FILE = PROJECT_ROOT / "data" / "silver" / "stock_prices.csv"
GOLD_DIR = PROJECT_ROOT / "data" / "gold"


def build_gold_dataset() -> Path:
    """Create an analytics-ready stock dataset using SQL."""
    if not SILVER_FILE.exists():
        raise FileNotFoundError(
            f"Silver data not found: {SILVER_FILE}"
        )

    GOLD_DIR.mkdir(parents=True, exist_ok=True)
    output_path = GOLD_DIR / "stock_analytics.csv"

    con = duckdb.connect(":memory:")

    try:
        query = """
            WITH daily AS (
                SELECT
                    ticker,
                    CAST("Date" AS TIMESTAMPTZ) AS trade_timestamp,
                    CAST("Date" AS DATE) AS trade_date,
                    "Open" AS open_price,
                    "High" AS high_price,
                    "Low" AS low_price,
                    "Close" AS close_price,
                    Volume AS volume
                FROM read_csv_auto(?)
            ),
            returns AS (
                SELECT
                    *,
                    close_price - LAG(close_price) OVER (
                        PARTITION BY ticker
                        ORDER BY trade_timestamp
                    ) AS price_change,
                    100.0 * (
                        close_price / NULLIF(
                            LAG(close_price) OVER (
                                PARTITION BY ticker
                                ORDER BY trade_timestamp
                            ),
                            0
                        ) - 1
                    ) AS daily_return_pct
                FROM daily
            ),
            metrics AS (
                SELECT
                    *,
                    AVG(close_price) OVER (
                        PARTITION BY ticker
                        ORDER BY trade_timestamp
                        ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
                    ) AS moving_avg_20d,
                    STDDEV_SAMP(daily_return_pct) OVER (
                        PARTITION BY ticker
                        ORDER BY trade_timestamp
                        ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
                    ) AS volatility_20d
                FROM returns
            )
            SELECT
                ticker,
                trade_date,
                open_price,
                high_price,
                low_price,
                close_price,
                volume,
                price_change,
                daily_return_pct,
                moving_avg_20d,
                volatility_20d
            FROM metrics
            ORDER BY ticker, trade_timestamp
        """

        result = con.execute(
            query, [str(SILVER_FILE)]
        ).df()

        result.to_csv(output_path, index=False)

    finally:
        con.close()

    print(f"Gold dataset saved to: {output_path}")
    return output_path


if __name__ == "__main__":
    build_gold_dataset()
