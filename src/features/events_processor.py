from dataclasses import dataclass
from collections import defaultdict

import pandas as pd

from src.core.logging import app_logger

logger = app_logger.getChild("features.events_processor")


@dataclass(frozen=True, slots=True)
class EventCounters:
    view: int = 0
    click: int = 0
    add_to_cart: int = 0
    purchase: int = 0

    @property
    def total(self) -> int:
        return self.view + self.click + self.add_to_cart + self.purchase


class EventsProcessor:
    """
    Responsible for aggregating user events
    and providing optimized structures for querying.

    Internal structure:

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
            "Initializing EventsProcessor.  events=%d",
            len(events_df),
        )

        self._events_by_user_product = self._build_events_index(events_df)

        total_users = len(self._events_by_user_product)

        total_relations = sum(
            len(products) for products in self._events_by_user_product.values()
        )

        logger.info(
            ("EventsProcessor initialized. users=%d user_product_relations=%d"),
            total_users,
            total_relations,
        )

    @staticmethod
    def _build_events_index(
        events_df: pd.DataFrame,
    ) -> dict[str, dict[str, EventCounters]]:
        """
        Builds the structure:

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
            accumulator[row.user_id][row.product_id][row.event_type] += 1

        result: dict[str, dict[str, EventCounters]] = {}

        for user_id, products in accumulator.items():
            result[user_id] = {}

            for product_id, counters in products.items():
                result[user_id][product_id] = EventCounters(
                    view=counters["view"],
                    click=counters["click"],
                    add_to_cart=counters["add_to_cart"],
                    purchase=counters["purchase"],
                )

        return result

    def get_event_counters(
        self,
        user_id: str,
        product_id: str,
    ) -> EventCounters:
        """
        Returns the detailed counters
        for a user and product.

        If there is no history,
        returns zeroed counters.
        """

        return self._events_by_user_product.get(user_id, {}).get(
            product_id, EventCounters()
        )

    def get_interactions(
        self,
        user_id: str,
        product_id: str,
    ) -> int:
        """
        Returns the total number of interactions
        the user has had with the product.
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
        Returns all products
        the user has history with.
        """

        return self._events_by_user_product.get(
            user_id,
            {},
        )

    def get_known_user_ids(
        self,
    ) -> set[str]:
        """
      Returns all known users.        """

        return set(self._events_by_user_product.keys())
