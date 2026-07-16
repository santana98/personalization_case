from fastapi import APIRouter, Request
from opentelemetry.trace import get_tracer


from src.api.routes.schemas import (
    RecommendationsResponse,
    ProductRecommendationResponse,
)
from src.core.settings import settings
from src.core.logging import app_logger

logger = app_logger.getChild("api.recommendations")

tracer = get_tracer("api.recommendations")

router = APIRouter()


@router.get("/recommendations/{user_id}", response_model=RecommendationsResponse)
def get_recommendations(
    user_id: str,
    request: Request,
) -> RecommendationsResponse:

    recommendations_by_user = request.app.state.recommendations_by_user

    popular_products = request.app.state.popular_products

    recommendations = recommendations_by_user.get(user_id)

    if recommendations is not None:
        with tracer.start_as_current_span("known_user_recommendations"):
            products = [
                ProductRecommendationResponse(
                    product_id=item.product_id,
                    score=item.score,
                )
                for item in recommendations[: settings.recommendation_top_k]
            ]

            logger.info(
                ("Recommendations returned. user_id=%s cold_start=false products=%d"),
                user_id,
                len(products),
            )

            return RecommendationsResponse(
                user_id=user_id,
                cold_start=False,
                products=products,
            )
    with tracer.start_as_current_span("cold_start_recommendations"):
        products = [
            ProductRecommendationResponse(
                product_id=product.product_id,
                score=0.0,
            )
            for product in popular_products[: settings.recommendation_top_k]
        ]

        logger.info(
            ("Cold start recommendations returned. user_id=%s products=%d"),
            user_id,
            len(products),
        )

        return RecommendationsResponse(
            user_id=user_id,
            cold_start=True,
            products=products,
        )
