
import os
from pathlib import Path

from google.cloud import storage


def upload_file_to_gcs(
    local_path: str,
    bucket_name: str,
    destination_blob_name: str,
) -> str:
    """Upload a local file to Google Cloud Storage."""
    file_path = Path(local_path)

    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {local_path}")

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(str(file_path))

    return f"gs://{bucket_name}/{destination_blob_name}"


def upload_pipeline_outputs() -> list[str]:
    """Upload Gold-layer outputs when the bucket is configured."""
    bucket_name = os.getenv("GCS_BUCKET_NAME")

    if not bucket_name:
        raise ValueError("Set the GCS_BUCKET_NAME environment variable.")

    files = [
        ("data/gold/stock_analytics.csv", "gold/stock_analytics.csv"),
        ("data/gold/data_quality_report.csv", "gold/data_quality_report.csv"),
    ]

    uploaded_files = []

    for local_path, destination in files:
        uploaded_files.append(
            upload_file_to_gcs(local_path, bucket_name, destination)
        )

    return uploaded_files
