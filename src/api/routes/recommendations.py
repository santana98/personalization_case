from fastapi import APIRouter, Request

from src.core.schemas import ResponseRecommendations

router = APIRouter()


@router.get("/recommendations/{user_id}")
def recommendations(user_id: str, request: Request):

    user_recommendations = ResponseRecommendations(
        user_id=user_id,
        products_recommendations=[
            {"product": "0001", "purchase_propensity_score": 0.8, "affinity_user": 1},
            {"product": "0002", "purchase_propensity_score": 0.4, "affinity_user": 0},
        ],
    )

    return user_recommendations
