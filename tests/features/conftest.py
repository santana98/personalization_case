from typing import Callable

import pandas as pd
import pytest

from src.features.affinity_processor import AffinityProcessor
from src.features.events_processor import EventsProcessor
from src.features.product_processor import ProductProcessor
from src.features.recommendation_builder import RecommendationBuilder


@pytest.fixture
def product_row() -> Callable[..., dict]:
    """
    Factory for a single row of the products dataset.

    Usage:
        product_row("p_010", "beauty", price=89.90, avg_rating=4.6, popularity_score=0.81)
    """

    def _factory(
        product_id: str,
        category: str,
        price: float = 10.0,
        avg_rating: float = 4.0,
        popularity_score: float = 0.5,
    ) -> dict:
        return {
            "product_id": product_id,
            "category": category,
            "price": price,
            "avg_rating": avg_rating,
            "popularity_score": popularity_score,
        }

    return _factory


@pytest.fixture
def event_row() -> Callable[..., dict]:
    """
    Factory for a single row of the events dataset.

    Usage:
        event_row("user_1", "p_010", "purchase")
    """

    def _factory(
        user_id: str,
        product_id: str,
        event_type: str,
        timestamp: str = "2026-01-01",
    ) -> dict:
        return {
            "user_id": user_id,
            "product_id": product_id,
            "event_type": event_type,
            "timestamp": timestamp,
        }

    return _factory


@pytest.fixture
def build_product_processor() -> Callable[[list[dict]], ProductProcessor]:
    """Builds a ProductProcessor from a list of product rows (dicts)."""

    def _factory(product_rows: list[dict]) -> ProductProcessor:
        return ProductProcessor(pd.DataFrame(product_rows))

    return _factory


@pytest.fixture
def build_events_processor() -> Callable[[list[dict]], EventsProcessor]:
    """Builds an EventsProcessor from a list of event rows (dicts)."""

    def _factory(event_rows: list[dict]) -> EventsProcessor:
        return EventsProcessor(pd.DataFrame(event_rows))

    return _factory


@pytest.fixture
def build_affinity_processor(
    build_product_processor: Callable[[list[dict]], ProductProcessor],
    build_events_processor: Callable[[list[dict]], EventsProcessor],
) -> Callable[[list[dict], list[dict]], AffinityProcessor]:
    """Builds an AffinityProcessor from product rows and event rows."""

    def _factory(
        product_rows: list[dict],
        event_rows: list[dict],
    ) -> AffinityProcessor:
        product_processor = build_product_processor(product_rows)

        events_processor = build_events_processor(event_rows)

        return AffinityProcessor(
            product_processor=product_processor,
            events_processor=events_processor,
        )

    return _factory


@pytest.fixture
def build_recommendation_builder(
    build_product_processor: Callable[[list[dict]], ProductProcessor],
    build_events_processor: Callable[[list[dict]], EventsProcessor],
) -> Callable[[list[dict], list[dict]], RecommendationBuilder]:
    """
    Builds a fully wired RecommendationBuilder from product rows and
    event rows (ProductProcessor -> EventsProcessor -> AffinityProcessor
    -> RecommendationBuilder).
    """

    def _factory(
        product_rows: list[dict],
        event_rows: list[dict],
    ) -> RecommendationBuilder:
        product_processor = build_product_processor(product_rows)

        events_processor = build_events_processor(event_rows)

        affinity_processor = AffinityProcessor(
            product_processor=product_processor,
            events_processor=events_processor,
        )

        return RecommendationBuilder(
            product_processor=product_processor,
            events_processor=events_processor,
            affinity_processor=affinity_processor,
        )

    return _factory
