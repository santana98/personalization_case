from pydantic import BaseModel


class Recomendations(BaseModel):
    product: str
    purchase_propensity_score: float
    affinity_user: int


class ResponseRecommendations(BaseModel):
    user_id: str
    products_recommendations: list[Recomendations]
