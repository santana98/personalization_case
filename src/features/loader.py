from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from src.core.logging import app_logger
from src.features.exceptions import DatasetValidationError
from src.features.schemas import EVENT_SCHEMA, PRODUCT_SCHEMA


logger = app_logger.getChild("features.loader")


VALID_EVENT_TYPES = {"view", "click", "add_to_cart", "purchase"}


@dataclass(slots=True)
class RawDatasets:
    products_df: pd.DataFrame
    events_df: pd.DataFrame


class DataLoader:
    def __init__(
        self,
        products_path: str,
        events_path: str,
    ) -> None:
        self.products_path = products_path
        self.events_path = events_path

    def load(self) -> RawDatasets:
        logger.info("Starting dataset loading.")

        products_df = self._load_products()
        events_df = self._load_events()

        self._validate_product_references(
            products_df=products_df,
            events_df=events_df,
        )

        logger.info(
            "Datasets loaded successfully. products=%d events=%d",
            len(products_df),
            len(events_df),
        )

        return RawDatasets(
            products_df=products_df,
            events_df=events_df,
        )

    def _load_products(self) -> pd.DataFrame:
        logger.info(
            "Loading products dataset: '%s'.",
            self.products_path,
        )

        df = self._read_csv(self.products_path)

        self._validate_required_columns(
            dataset_name="products",
            df=df,
            required_columns=PRODUCT_SCHEMA.required_columns,
        )

        self._validate_non_null_columns(
            dataset_name="products",
            df=df,
            columns=PRODUCT_SCHEMA.required_columns,
        )

        self._cast_products_types(df)

        self._validate_unique_product_ids(df)

        return df

    def _load_events(self) -> pd.DataFrame:
        logger.info(
            "Loading events dataset: '%s'.",
            self.events_path,
        )

        df = self._read_csv(self.events_path)

        self._validate_required_columns(
            dataset_name="events",
            df=df,
            required_columns=EVENT_SCHEMA.required_columns,
        )

        self._validate_non_null_columns(
            dataset_name="events",
            df=df,
            columns=EVENT_SCHEMA.required_columns,
        )

        self._cast_events_types(df)

        self._validate_event_types(df)

        return df

    @staticmethod
    def _read_csv(path: str) -> pd.DataFrame:
        file_path = Path(path)

        if not file_path.exists():
            logger.error(
                "Dataset file not found: '%s'.",
                path,
            )
            raise FileNotFoundError(f"Dataset file not found: {path}")

        try:
            return pd.read_csv(file_path)
        except Exception as exc:
            logger.exception(
                "Failed to read dataset: '%s'.",
                path,
            )
            raise DatasetValidationError(f"Failed to read dataset: {path}") from exc

    @staticmethod
    def _validate_required_columns(
        dataset_name: str,
        df: pd.DataFrame,
        required_columns: set[str],
    ) -> None:
        missing_columns = required_columns - set(df.columns)

        if missing_columns:
            logger.error(
                "%s dataset validation failed. Missing columns: %s",
                dataset_name,
                sorted(missing_columns),
            )
            raise DatasetValidationError(
                f"{dataset_name} dataset with missing columns: "
                f"{sorted(missing_columns)}"
            )

    @staticmethod
    def _validate_non_null_columns(
        dataset_name: str,
        df: pd.DataFrame,
        columns: set[str],
    ) -> None:
        null_columns = [column for column in columns if df[column].isna().any()]

        if null_columns:
            logger.error(
                "%s dataset contains null values in columns: %s",
                dataset_name,
                sorted(null_columns),
            )
            raise DatasetValidationError(
                f"{dataset_name} dataset with null values "
                f"nas colunas: {sorted(null_columns)}"
            )

    @staticmethod
    def _cast_products_types(df: pd.DataFrame) -> None:
        try:
            df["product_id"] = df["product_id"].astype(str)
            df["category"] = df["category"].astype(str)
            df["price"] = df["price"].astype(float)
            df["avg_rating"] = df["avg_rating"].astype(float)
            df["popularity_score"] = df["popularity_score"].astype(float)
        except Exception as exc:
            logger.exception("Failed to cast products dataset types")
            raise DatasetValidationError(
                "Invalid data types found in the products dataset."
            ) from exc

    @staticmethod
    def _cast_events_types(df: pd.DataFrame) -> None:
        try:
            df["user_id"] = df["user_id"].astype(str)
            df["product_id"] = df["product_id"].astype(str)
            df["event_type"] = df["event_type"].astype(str)

            df["timestamp"] = pd.to_datetime(
                df["timestamp"],
                errors="raise",
            )
        except Exception as exc:
            logger.exception("Failed to cast events dataset types.")
            raise DatasetValidationError(
                "Invalid data types found in the events dataset."
            ) from exc

    @staticmethod
    def _validate_unique_product_ids(
        df: pd.DataFrame,
    ) -> None:
        duplicated = df["product_id"].duplicated()

        if duplicated.any():
            duplicated_ids = df.loc[duplicated, "product_id"].unique().tolist()

            logger.error(
                "Duplicate product_id values found: %s",
                duplicated_ids,
            )

            raise DatasetValidationError("Duplicate product_id values found.")

    @staticmethod
    def _validate_event_types(
        df: pd.DataFrame,
    ) -> None:
        invalid_event_types = set(df["event_type"].unique()) - VALID_EVENT_TYPES

        if invalid_event_types:
            logger.error(
                "Invalid event types found: %s",
                sorted(invalid_event_types),
            )

            raise DatasetValidationError(
                f"Invalid event types found {sorted(invalid_event_types)}"
            )

    @staticmethod
    def _validate_product_references(
        products_df: pd.DataFrame,
        events_df: pd.DataFrame,
    ) -> None:
        invalid_products = set(events_df["product_id"].unique()) - set(
            products_df["product_id"].unique()
        )

        if invalid_products:
            logger.error(
                "The events dataset references unknown products: %s",
                sorted(invalid_products),
            )

            raise DatasetValidationError(
                "The events dataset contains references to unknown products."
            )
