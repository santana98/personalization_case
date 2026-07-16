from time import perf_counter

from src.core.logging import app_logger
from src.features.affinity_processor import (
    AffinityProcessor,
)
from src.features.events_processor import (
    EventsProcessor,
)
from src.features.product_processor import (
    ProductProcessor,
)

from src.model.predict import predict_score
from src.features.domain import Recommendation, Product

logger = app_logger.getChild("features.recommendation_builder")


class RecommendationBuilder:
    """
    Responsável por construir a base final
    de recomendações em memória.

    Estrutura produzida:

    {
        user_id: (
            Recommendation(...),
            Recommendation(...),
        )
    }

    Ordenação:

    1. score DESC
    2. popularity_score DESC
    3. price DESC
    4. product_id ASC
    """

    def __init__(
        self,
        product_processor: ProductProcessor,
        events_processor: EventsProcessor,
        affinity_processor: AffinityProcessor,
    ) -> None:
        self._product_processor = product_processor

        self._events_processor = events_processor

        self._affinity_processor = affinity_processor

    def build(
        self,
    ) -> dict[str, tuple[Recommendation, ...]]:
        logger.info("Iniciando construção da base de recomendações.")

        started_at = perf_counter()

        recommendations_by_user = {}

        user_ids = self._events_processor.get_known_user_ids()

        products = self._product_processor.get_all_products()

        total_predictions = 0

        for user_id in user_ids:
            user_affinity = self._affinity_processor.get_user_affinity(user_id)

            recommendations = []

            for product in products:
                feature_vector = self._create_feature_vector(
                    user_id=user_id,
                    user_affinity=user_affinity,
                    product=product,
                )

                score = predict_score(feature_vector)

                recommendations.append(
                    (
                        product,
                        Recommendation(
                            product_id=product.product_id,
                            score=float(score),
                        ),
                    )
                )

                total_predictions += 1

            recommendations.sort(
                key=lambda item: (
                    -item[1].score,
                    -item[0].popularity_score,
                    -item[0].price,
                    item[0].product_id,
                ),
            )

            recommendations_by_user[user_id] = tuple(
                recommendation for _, recommendation in recommendations
            )

        elapsed_seconds = perf_counter() - started_at

        throughput = total_predictions / elapsed_seconds if elapsed_seconds > 0 else 0

        logger.info(
            (
                "Base de recomendações construída. "
                "users=%d predictions=%d "
                "elapsed_seconds=%.3f "
                "predictions_per_second=%.2f"
            ),
            len(recommendations_by_user),
            total_predictions,
            elapsed_seconds,
            throughput,
        )

        return recommendations_by_user

    def _create_feature_vector(
        self,
        user_id: str,
        user_affinity: str,
        product: Product,
    ) -> dict[str, int | float]:
        interactions = self._events_processor.get_interactions(
            user_id=user_id,
            product_id=product.product_id,
        )

        affinity_match = int(product.category == user_affinity)

        return {
            "interactions": interactions,
            "price": product.price,
            "avg_rating": product.avg_rating,
            "popularity_score": (product.popularity_score),
            "user_affinity_match": (affinity_match),
        }
