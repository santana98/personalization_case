from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    products_path: str = Field(
        default="data/products.csv",
        alias="PRODUCTS_PATH",
    )
    events_path: str = Field(
        default="data/events.csv",
        alias="EVENTS_PATH",
    )
    model_path: str = Field(
        default="src/model/artifacts/model.pkl",
        alias="MODEL_PATH",
    )
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )
    recommendation_top_k: int = Field(
        default=4,
        alias="RECOMMENDATION_TOP_K",
    )


settings = Settings()
