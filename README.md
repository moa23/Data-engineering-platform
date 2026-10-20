## Features

- **Data ingestion:** Extracts historical stock market data using Python and `yfinance`.
- **Medallion architecture:** Organizes data into Bronze, Silver, and Gold layers.
- **Data cleaning and validation:** Uses pandas to handle missing values, duplicate records, and invalid price or volume values.
- **Analytics with DuckDB and SQL:** Calculates:
  - Daily price changes
  - Daily percentage returns
  - 20-day moving averages
  - 20-day rolling volatility
- **SQL analytics:** Identifies the 10 best and 10 worst trading days by daily percentage return.
- **Data quality reporting:** Generates a CSV report to help assess the quality of the processed data.
- **Automated testing:** Uses pytest to validate pipeline functionality.
- **CI/CD:** Runs automated tests through GitHub Actions on pushes and pull requests to `main`.
- **Scheduled execution:** Runs the data pipeline automatically on weekdays, with support for manual execution.
- **Cloud storage integration:** Uploads Gold-layer analytics and data quality reports to Google Cloud Storage.
- **Secure cloud authentication:** Uses Workload Identity Federation to authenticate GitHub Actions with Google Cloud without storing a service account key.
- **Logging:** Uses structured logging to help monitor pipeline execution and troubleshoot errors.

## Cloud Storage Output

The pipeline uploads its processed outputs to Google Cloud Storage:

- `gold/daily/stock_analytics_<timestamp>.csv`
- `gold/daily/data_quality_report_<timestamp>.csv`

Timestamped filenames preserve outputs from individual pipeline runs.

## SQL Analytics

The SQL queries are available in `sql/analytics.sql` and run against the Gold-layer analytics dataset, `data/gold/stock_analytics.csv`.

The queries identify the 10 highest and 10 lowest daily percentage returns using DuckDB SQL, demonstrating filtering, sorting, and analytical querying.

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
│       ├── tests.yml
│       └── daily-pipeline.yml
├── requirements.txt
└── README.md
```
