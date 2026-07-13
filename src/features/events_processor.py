from dataclasses import dataclass
from collections import defaultdict

import pandas as pd

from src.core.logging import app_logger

logger = app_logger.getChild(
    "features.events_processor"
)


@dataclass(frozen=True, slots=True)
class EventCounters:
    view: int = 0
    click: int = 0
    add_to_cart: int = 0
    purchase: int = 0

    @property
    def total(self) -> int:
        return (
            self.view
            + self.click
            + self.add_to_cart
            + self.purchase
        )


class EventsProcessor:
    """
    Responsável por agregar eventos de usuários
    e disponibilizar estruturas otimizadas para consulta.

    Estrutura interna:

    {
        user_id: {
            product_id: EventCounters
        }
    }
    """

    def __init__(
        self,
        events_df: pd.DataFrame,
    ) -> None:
        logger.info(
            "Inicializando EventsProcessor. events=%d",
            len(events_df),
        )

        self._events_by_user_product = (
            self._build_events_index(events_df)
        )

        total_users = len(
            self._events_by_user_product
        )

        total_relations = sum(
            len(products)
            for products in self._events_by_user_product.values()
        )

        logger.info(
            (
                "EventsProcessor inicializado. "
                "users=%d user_product_relations=%d"
            ),
            total_users,
            total_relations,
        )

    @staticmethod
    def _build_events_index(
        events_df: pd.DataFrame,
    ) -> dict[str, dict[str, EventCounters]]:
        """
        Constrói a estrutura:

        {
            user_id: {
                product_id: EventCounters
            }
        }
        """

        accumulator = defaultdict(
            lambda: defaultdict(
                lambda: {
                    "view": 0,
                    "click": 0,
                    "add_to_cart": 0,
                    "purchase": 0,
                }
            )
        )

        for row in events_df.itertuples(index=False):
            accumulator[
                row.user_id
            ][
                row.product_id
            ][
                row.event_type
            ] += 1

        result: dict[
            str,
            dict[str, EventCounters]
        ] = {}

        for user_id, products in accumulator.items():
            result[user_id] = {}

            for product_id, counters in products.items():
                result[user_id][product_id] = (
                    EventCounters(
                        view=counters["view"],
                        click=counters["click"],
                        add_to_cart=counters["add_to_cart"],
                        purchase=counters["purchase"],
                    )
                )

        return result

    def get_event_counters(
        self,
        user_id: str,
        product_id: str,
    ) -> EventCounters:
        """
        Retorna os contadores detalhados
        para um usuário e produto.

        Caso não exista histórico,
        retorna contadores zerados.
        """

        return (
            self._events_by_user_product
            .get(user_id, {})
            .get(product_id, EventCounters())
        )

    def get_interactions(
        self,
        user_id: str,
        product_id: str,
    ) -> int:
        """
        Retorna o total de interações
        do usuário com o produto.
        """

        return self.get_event_counters(
            user_id=user_id,
            product_id=product_id,
        ).total

    def get_user_products(
        self,
        user_id: str,
    ) -> dict[str, EventCounters]:
        """
        Retorna todos os produtos
        com os quais o usuário possui histórico.
        """

        return self._events_by_user_product.get(
            user_id,
            {},
        )

    def get_known_user_ids(
        self,
    ) -> set[str]:
        """
        Retorna todos os usuários conhecidos.
        """

        return set(
            self._events_by_user_product.keys()
        )