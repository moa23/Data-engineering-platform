
import pandas as pd
import pytest

from src.ingestion import extract


def test_extract_stock_data_saves_csv(tmp_path, monkeypatch):
    sample_data = pd.DataFrame(
        {
            "Open": [150.0, 152.0],
            "High": [155.0, 156.0],
            "Low": [149.0, 151.0],
            "Close": [153.0, 154.0],
            "Volume": [1000, 1200],
        },
        index=pd.to_datetime(
            ["2025-01-02", "2025-01-03"]
        ),
    )
    sample_data.index.name = "Date"

    class FakeTicker:
        def __init__(self, ticker):
            self.ticker = ticker

        def history(self, period, auto_adjust):
            return sample_data

    monkeypatch.setattr(extract.yf, "Ticker", FakeTicker)
    monkeypatch.setattr(extract, "BRONZE_DIR", tmp_path)

    output_path = extract.extract_stock_data("AAPL", "1y")

    assert output_path.exists()

    result = pd.read_csv(output_path)

    assert len(result) == 2
    assert result["ticker"].tolist() == ["AAPL", "AAPL"]
    assert "Close" in result.columns


def test_extract_stock_data_raises_on_empty_data(
    tmp_path, monkeypatch
):
    class FakeTicker:
        def __init__(self, ticker):
            pass

        def history(self, period, auto_adjust):
            return pd.DataFrame()

    monkeypatch.setattr(extract.yf, "Ticker", FakeTicker)
    monkeypatch.setattr(extract, "BRONZE_DIR", tmp_path)

    with pytest.raises(ValueError, match="No stock data"):
        extract.extract_stock_data("INVALID", "1y")

from src.transformation import transform


def test_transform_stock_data_cleans_and_sorts_data(
    tmp_path, monkeypatch
):
    input_path = tmp_path / "raw.csv"
    output_dir = tmp_path / "silver"

    raw_data = pd.DataFrame(
        {
            "ticker": ["AAPL", "AAPL", "AAPL", "AAPL"],
            "Date": [
                "2025-01-03",
                "2025-01-02",
                "2025-01-02",
                "2025-01-04",
            ],
            "Open": [153.0, 150.0, 150.0, -1.0],
            "High": [156.0, 155.0, 155.0, 160.0],
            "Low": [151.0, 149.0, 149.0, 150.0],
            "Close": [154.0, 153.0, 153.0, 155.0],
            "Volume": [1200, 1000, 1000, 1500],
        }
    )
    raw_data.to_csv(input_path, index=False)

    monkeypatch.setattr(transform, "SILVER_DIR", output_dir)

    output_path = transform.transform_stock_data(input_path)
    result = pd.read_csv(output_path)

    assert len(result) == 2
    assert result["Date"].is_monotonic_increasing
    assert result["Date"].is_unique
    assert (result["Open"] > 0).all()
    assert (result["High"] >= result["Low"]).all()


def test_transform_stock_data_rejects_missing_columns(tmp_path):
    input_path = tmp_path / "incomplete.csv"
    pd.DataFrame({"ticker": ["AAPL"], "Close": [150.0]}).to_csv(
        input_path, index=False
    )

    with pytest.raises(ValueError, match="Missing required columns"):
        transform.transform_stock_data(input_path)

from src.transformation import gold


def test_build_gold_dataset_calculates_metrics(
    tmp_path, monkeypatch
):
    silver_file = tmp_path / "stock_prices.csv"
    gold_dir = tmp_path / "gold"

    sample_data = pd.DataFrame(
        {
            "ticker": ["AAPL", "AAPL", "AAPL"],
            "Date": [
                "2025-01-02 00:00:00-05:00",
                "2025-01-03 00:00:00-05:00",
                "2025-01-06 00:00:00-05:00",
            ],
            "Open": [100.0, 110.0, 105.0],
            "High": [105.0, 115.0, 108.0],
            "Low": [98.0, 109.0, 103.0],
            "Close": [100.0, 110.0, 105.0],
            "Volume": [1000, 1200, 900],
        }
    )
    sample_data.to_csv(silver_file, index=False)

    monkeypatch.setattr(gold, "SILVER_FILE", silver_file)
    monkeypatch.setattr(gold, "GOLD_DIR", gold_dir)

    output_path = gold.build_gold_dataset()
    result = pd.read_csv(output_path)

    assert len(result) == 3
    assert result["ticker"].tolist() == ["AAPL"] * 3

    assert pd.isna(result.loc[0, "daily_return_pct"])
    assert result.loc[1, "daily_return_pct"] == pytest.approx(10.0)
    assert result.loc[2, "daily_return_pct"] == pytest.approx(
        -100.0 * (1 - 105.0 / 110.0)
    )

    assert result.loc[1, "price_change"] == pytest.approx(10.0)
    assert result.loc[2, "price_change"] == pytest.approx(-5.0)

    assert result.loc[2, "moving_avg_20d"] == pytest.approx(
        105.0
    )

def test_transform_stock_data_removes_invalid_prices(
    tmp_path, monkeypatch
):
    input_file = tmp_path / "raw_stock_data.csv"
    silver_dir = tmp_path / "silver"

    sample_data = pd.DataFrame(
        {
            "ticker": ["AAPL", "AAPL", "AAPL"],
            "Date": [
                "2025-01-02",
                "2025-01-03",
                "2025-01-06",
            ],
            "Open": [100.0, 100.0, 100.0],
            "High": [105.0, 95.0, 105.0],
            "Low": [98.0, 90.0, 98.0],
            "Close": [102.0, 100.0, 102.0],
            "Volume": [1000, 1200, -1],
        }
    )
    sample_data.to_csv(input_file, index=False)

    monkeypatch.setattr(transform, "SILVER_DIR", silver_dir)

    output_path = transform.transform_stock_data(input_file)
    result = pd.read_csv(output_path)

    assert len(result) == 1
    assert result.iloc[0]["Date"].startswith("2025-01-02")

def test_build_gold_dataset_raises_when_silver_file_missing(
    tmp_path, monkeypatch
):
    missing_file = tmp_path / "missing_stock_prices.csv"
    gold_dir = tmp_path / "gold"

    monkeypatch.setattr(gold, "SILVER_FILE", missing_file)
    monkeypatch.setattr(gold, "GOLD_DIR", gold_dir)

    with pytest.raises(FileNotFoundError, match="Silver data not found"):
        gold.build_gold_dataset()

from src.transformation import quality_report


def test_build_quality_report_creates_report(
    tmp_path, monkeypatch
):
    silver_file = tmp_path / "stock_prices.csv"
    report_dir = tmp_path / "gold"

    sample_data = pd.DataFrame(
        {
            "ticker": ["AAPL", "AAPL"],
            "Date": ["2025-01-02", "2025-01-03"],
            "Open": [100.0, 110.0],
            "High": [105.0, 115.0],
            "Low": [98.0, 109.0],
            "Close": [102.0, 112.0],
            "Volume": [1000, 1200],
        }
    )
    sample_data.to_csv(silver_file, index=False)

    monkeypatch.setattr(
        quality_report, "SILVER_FILE", silver_file
    )
    monkeypatch.setattr(
        quality_report, "REPORT_DIR", report_dir
    )

    output_path = quality_report.build_quality_report()
    result = pd.read_csv(output_path)

    metrics = dict(zip(result["metric"], result["value"]))

    assert metrics["total_rows"] == 2
    assert metrics["missing_values"] == 0
    assert metrics["duplicate_rows"] == 0
    assert metrics["invalid_price_rows"] == 0
    assert output_path.exists()
