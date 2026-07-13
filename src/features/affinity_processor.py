from collections import defaultdict
from dataclasses import dataclass

from src.core.logging import app_logger
from src.features.events_processor import (
    EventsProcessor,
)
from src.features.exceptions import (
    UserAffinityNotFoundError,
)
from src.features.product_processor import (
    ProductProcessor,
)

logger = app_logger.getChild("features.affinity_processor")


@dataclass(slots=True)
class CategoryAffinity:
    interactions: int = 0

    purchase: int = 0
    add_to_cart: int = 0
    click: int = 0
    view: int = 0

    def ranking_key(
        self,
    ) -> tuple[int, int, int, int, int]:
        """
        Ordem de prioridade:

        interactions
        purchase
        add_to_cart
        click
        view
        """

        return (
            self.interactions,
            self.purchase,
            self.add_to_cart,
            self.click,
            self.view,
        )


class AffinityProcessor:
    """
    Determina a categoria de maior afinidade
    de cada usuário.

    Regras:

    1. Maior número de interações.
    2. Desempate por:
        purchase >
        add_to_cart >
        click >
        view
    3. Persistindo empate:
        ordem alfabética da categoria.
    """

    def __init__(
        self,
        product_processor: ProductProcessor,
        events_processor: EventsProcessor,
    ) -> None:
        logger.info("Inicializando AffinityProcessor.")

        self._user_affinities = self._build_user_affinities(
            product_processor=product_processor,
            events_processor=events_processor,
        )

        logger.info(
            ("AffinityProcessor inicializado. users=%d"),
            len(self._user_affinities),
        )

    def _build_user_affinities(
        self,
        product_processor: ProductProcessor,
        events_processor: EventsProcessor,
    ) -> dict[str, str]:
        user_affinities: dict[str, str] = {}

        for user_id in events_processor.get_known_user_ids():
            category_scores = defaultdict(CategoryAffinity)

            user_products = events_processor.get_user_products(user_id)

            for (
                product_id,
                counters,
            ) in user_products.items():
                product = product_processor.get_product(product_id)

                affinity = category_scores[product.category]

                affinity.interactions += counters.total

                affinity.purchase += counters.purchase

                affinity.add_to_cart += counters.add_to_cart

                affinity.click += counters.click

                affinity.view += counters.view

            winner_category = self._select_winner_category(category_scores)

            user_affinities[user_id] = winner_category

        return user_affinities

    @staticmethod
    def _select_winner_category(
        category_scores: dict[
            str,
            CategoryAffinity,
        ],
    ) -> str:
        winner_category = None
        winner_affinity = None

        for (
            category,
            affinity,
        ) in category_scores.items():
            if winner_affinity is None:
                winner_category = category
                winner_affinity = affinity
                continue

            current_key = affinity.ranking_key()

            winner_key = winner_affinity.ranking_key()

            if current_key > winner_key:
                winner_category = category
                winner_affinity = affinity
                continue

            if current_key == winner_key and category < winner_category:
                winner_category = category
                winner_affinity = affinity

        return winner_category

    def get_user_affinity(
        self,
        user_id: str,
    ) -> str:
        try:
            return self._user_affinities[user_id]

        except KeyError as exc:
            logger.warning(
                "Affinity not found for user",
                extra={
                    "user_id": user_id,
                },
            )

            raise UserAffinityNotFoundError(user_id) from exc

    def get_known_user_ids(
        self,
    ) -> set[str]:
        return set(self._user_affinities.keys())
