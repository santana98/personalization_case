from typing import Callable

import pytest

from src.features.domain import Product
from src.features.product_processor import ProductProcessor
from src.features.recommendation_builder import RecommendationBuilder


@pytest.fixture
def products(product_row: Callable[..., dict]) -> list[dict]:
    return [
        product_row(
            "p_010",
            "beauty",
            price=89.90,
            avg_rating=4.6,
            popularity_score=0.81,
        ),
        product_row(
            "p_020",
            "books",
            price=39.90,
            avg_rating=4.2,
            popularity_score=0.55,
        ),
    ]


@pytest.fixture
def events(event_row: Callable[..., dict]) -> list[dict]:
    return [
        # user_1 interacts 3x with p_010 (view + click + purchase)
        event_row("user_1", "p_010", "view"),
        event_row("user_1", "p_010", "click"),
        event_row("user_1", "p_010", "purchase"),
    ]


@pytest.fixture
def product_processor(
    build_product_processor: Callable[[list[dict]], ProductProcessor],
    products: list[dict],
) -> ProductProcessor:
    return build_product_processor(products)


@pytest.fixture
def builder(
    build_recommendation_builder: Callable[[list[dict], list[dict]], RecommendationBuilder],
    products: list[dict],
    events: list[dict],
) -> RecommendationBuilder:
    return build_recommendation_builder(products, events)


@pytest.fixture
def beauty_product(product_processor: ProductProcessor) -> Product:
    return product_processor.get_product("p_010")


@pytest.fixture
def books_product(product_processor: ProductProcessor) -> Product:
    return product_processor.get_product("p_020")


class TestInteractions:
    def test_sums_all_events_for_the_user_product_pair(
        self,
        builder: RecommendationBuilder,
        beauty_product: Product,
    ) -> None:
        feature_vector = builder._create_feature_vector(
            user_id="user_1",
            user_affinity="beauty",
            product=beauty_product,
        )

        # view + click + purchase = 3
        assert feature_vector["interactions"] == 3

    def test_is_zero_when_user_has_no_history_with_the_product(
        self,
        builder: RecommendationBuilder,
        books_product: Product,
    ) -> None:
        feature_vector = builder._create_feature_vector(
            user_id="user_1",
            user_affinity="beauty",
            product=books_product,
        )

        assert feature_vector["interactions"] == 0

    def test_is_zero_for_a_completely_unknown_user(
        self,
        builder: RecommendationBuilder,
        beauty_product: Product,
    ) -> None:
        feature_vector = builder._create_feature_vector(
            user_id="nonexistent_user",
            user_affinity="beauty",
            product=beauty_product,
        )

        assert feature_vector["interactions"] == 0


class TestProductAttributes:
    def test_price_reflects_the_correct_product(
        self,
        builder: RecommendationBuilder,
        beauty_product: Product,
    ) -> None:
        feature_vector = builder._create_feature_vector(
            user_id="user_1",
            user_affinity="beauty",
            product=beauty_product,
        )

        assert feature_vector["price"] == 89.90

    def test_avg_rating_reflects_the_correct_product(
        self,
        builder: RecommendationBuilder,
        beauty_product: Product,
    ) -> None:
        feature_vector = builder._create_feature_vector(
            user_id="user_1",
            user_affinity="beauty",
            product=beauty_product,
        )

        assert feature_vector["avg_rating"] == 4.6

    def test_popularity_score_reflects_the_correct_product(
        self,
        builder: RecommendationBuilder,
        beauty_product: Product,
    ) -> None:
        feature_vector = builder._create_feature_vector(
            user_id="user_1",
            user_affinity="beauty",
            product=beauty_product,
        )

        assert feature_vector["popularity_score"] == 0.81


class TestUserAffinityMatch:
    def test_is_1_when_product_category_matches_user_affinity(
        self,
        builder: RecommendationBuilder,
        beauty_product: Product,
    ) -> None:
        feature_vector = builder._create_feature_vector(
            user_id="user_1",
            user_affinity="beauty",
            product=beauty_product,
        )

        assert feature_vector["user_affinity_match"] == 1

    def test_is_0_when_product_category_differs_from_user_affinity(
        self,
        builder: RecommendationBuilder,
        beauty_product: Product,
    ) -> None:
        feature_vector = builder._create_feature_vector(
            user_id="user_1",
            user_affinity="books",
            product=beauty_product,
        )

        assert feature_vector["user_affinity_match"] == 0

    def test_is_0_when_user_has_no_computed_affinity(
        self,
        builder: RecommendationBuilder,
        beauty_product: Product,
    ) -> None:
        feature_vector = builder._create_feature_vector(
            user_id="user_without_affinity",
            user_affinity=None,
            product=beauty_product,
        )

        assert feature_vector["user_affinity_match"] == 0


class TestPayloadContract:
    def test_payload_contains_exactly_the_features_expected_by_the_model(
        self,
        builder: RecommendationBuilder,
        beauty_product: Product,
    ) -> None:
        feature_vector = builder._create_feature_vector(
            user_id="user_1",
            user_affinity="beauty",
            product=beauty_product,
        )

        assert set(feature_vector.keys()) == {
            "interactions",
            "price",
            "avg_rating",
            "popularity_score",
            "user_affinity_match",
        }