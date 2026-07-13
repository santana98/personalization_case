from dataclasses import dataclass


@dataclass(frozen=True)
class DatasetSchema:
    required_columns: set[str]


PRODUCT_SCHEMA = DatasetSchema(
    required_columns={
        "product_id",
        "category",
        "price",
        "avg_rating",
        "popularity_score",
    }
)

EVENT_SCHEMA = DatasetSchema(
    required_columns={
        "user_id",
        "product_id",
        "event_type",
        "timestamp",
    }
)
