from pydantic import BaseModel


class ProductRecommendationResponse(
    BaseModel,
):
    product_id: str
    score: float


class RecommendationsResponse(
    BaseModel,
):
    user_id: str
    cold_start: bool
    products: list[ProductRecommendationResponse]
