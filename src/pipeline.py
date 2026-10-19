
import logging

from src.ingestion.extract import extract_stock_data
from src.transformation.transform import transform_stock_data
from src.transformation.gold import build_gold_dataset
from src.transformation.quality_report import build_quality_report


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


def run_pipeline():
    logger.info("Starting data pipeline")

    try:
        logger.info("Step 1/3: Extracting data")
        extract_stock_data()

        logger.info("Step 2/3: Transforming data")
        transform_stock_data()

        logger.info("Step 3/3: Building Gold dataset")
        build_gold_dataset()
        
        logger.info("Step 4/4: Generating data quality report")
        build_quality_report()

        logger.info("Pipeline completed successfully")

    except Exception:
        logger.exception("Pipeline failed")
        raise


if __name__ == "__main__":
    run_pipeline()
