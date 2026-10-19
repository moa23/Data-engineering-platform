## Features

- Ingests historical stock market data using Python and `yfinance`.
- Stores raw data in a Bronze layer.
- Cleans and validates data in a Silver layer using pandas.
- Removes missing values, duplicate records, and invalid price or volume records.
- Uses DuckDB and SQL window functions to calculate:
  - Daily price changes
  - Daily percentage returns
  - 20-day moving averages
  - 20-day rolling volatility
- Includes SQL analytics to identify the 10 best and 10 worst trading days by daily percentage return.
- Generates a CSV data quality report.
- Includes automated tests with pytest.
- Uses structured logging to help monitor pipeline execution.
- Runs automated tests through GitHub Actions on pushes and pull requests to `main`.

## SQL Analytics

The SQL queries are available in `sql/analytics.sql` and run against the Gold dataset, `data/gold/stock_analytics.csv`.

The queries identify the 10 highest and 10 lowest daily percentage returns, demonstrating filtering, sorting, and analytical querying with DuckDB SQL.

## Project Structure

```text
data-engineering-platform/
├── data/
│   ├── bronze/
│   ├── silver/
│   └── gold/
├── src/
│   ├── ingestion/
│   │   └── extract.py
│   ├── transformation/
│   │   ├── transform.py
│   │   ├── gold.py
│   │   └── quality_report.py
│   └── pipeline.py
├── sql/
│   └── analytics.sql
├── tests/
│   └── test_pipeline.py
├── .github/
│   └── workflows/
│       └── tests.yml
├── requirements.txt
└── README.md
```
