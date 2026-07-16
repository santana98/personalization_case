from typing import Callable

import pytest

from src.features.affinity_processor import AffinityProcessor
from src.features.exceptions import UserAffinityNotFoundError


class TestPrimaryCriterionTotalInteractions:
    def test_category_with_more_interactions_wins(
        self,
        product_row: Callable[..., dict],
        event_row: Callable[..., dict],
        build_affinity_processor: Callable[[list[dict], list[dict]], AffinityProcessor],
    ) -> None:
        products = [
            product_row("p_beauty", "beauty"),
            product_row("p_books", "books"),
        ]

        events = [
            # beauty: 2 interactions
            event_row("user_1", "p_beauty", "view"),
            event_row("user_1", "p_beauty", "click"),
            # books: 5 interactions
            event_row("user_1", "p_books", "view"),
            event_row("user_1", "p_books", "click"),
            event_row("user_1", "p_books", "click"),
            event_row("user_1", "p_books", "add_to_cart"),
            event_row("user_1", "p_books", "add_to_cart"),
        ]

        affinity_processor = build_affinity_processor(products, events)

        assert affinity_processor.get_user_affinity("user_1") == "books"


class TestTieBreakByPurchase:
    def test_interactions_tied_purchase_decides(
        self,
        product_row: Callable[..., dict],
        event_row: Callable[..., dict],
        build_affinity_processor: Callable[[list[dict], list[dict]], AffinityProcessor],
    ) -> None:
        products = [
            product_row("p_beauty", "beauty"),
            product_row("p_books", "books"),
        ]

        events = [
            # beauty: 3 interactions, 1 purchase
            event_row("user_1", "p_beauty", "view"),
            event_row("user_1", "p_beauty", "click"),
            event_row("user_1", "p_beauty", "purchase"),
            # books: 3 interactions, 0 purchase
            event_row("user_1", "p_books", "view"),
            event_row("user_1", "p_books", "click"),
            event_row("user_1", "p_books", "add_to_cart"),
        ]

        affinity_processor = build_affinity_processor(products, events)

        assert affinity_processor.get_user_affinity("user_1") == "beauty"


class TestTieBreakByAddToCart:
    def test_interactions_and_purchase_tied_add_to_cart_decides(
        self,
        product_row: Callable[..., dict],
        event_row: Callable[..., dict],
        build_affinity_processor: Callable[[list[dict], list[dict]], AffinityProcessor],
    ) -> None:
        products = [
            product_row("p_beauty", "beauty"),
            product_row("p_books", "books"),
        ]

        events = [
            # beauty: 1 interaction, 0 purchase, 1 add_to_cart
            event_row("user_1", "p_beauty", "add_to_cart"),
            # books: 1 interaction, 0 purchase, 0 add_to_cart (1 click)
            event_row("user_1", "p_books", "click"),
        ]

        affinity_processor = build_affinity_processor(products, events)

        assert affinity_processor.get_user_affinity("user_1") == "beauty"


class TestTieBreakByClick:
    def test_previous_levels_tied_click_decides(
        self,
        product_row: Callable[..., dict],
        event_row: Callable[..., dict],
        build_affinity_processor: Callable[[list[dict], list[dict]], AffinityProcessor],
    ) -> None:
        products = [
            product_row("p_beauty", "beauty"),
            product_row("p_books", "books"),
        ]

        events = [
            # beauty: 1 interaction, 0 purchase, 0 add_to_cart, 1 click
            event_row("user_1", "p_beauty", "click"),
            # books: 1 interaction, 0 purchase, 0 add_to_cart, 0 click (1 view)
            event_row("user_1", "p_books", "view"),
        ]

        affinity_processor = build_affinity_processor(products, events)

        assert affinity_processor.get_user_affinity("user_1") == "beauty"


class TestFinalAlphabeticalTieBreak:
    def test_all_levels_tied_alphabetical_order_wins(
        self,
        product_row: Callable[..., dict],
        event_row: Callable[..., dict],
        build_affinity_processor: Callable[[list[dict], list[dict]], AffinityProcessor],
    ) -> None:
        products = [
            product_row("p_books", "books"),
            product_row("p_beauty", "beauty"),
        ]

        events = [
            # beauty and books are tied on every criterion: 1 view each
            event_row("user_1", "p_books", "view"),
            event_row("user_1", "p_beauty", "view"),
        ]

        affinity_processor = build_affinity_processor(products, events)

        # "beauty" < "books" alphabetically
        assert affinity_processor.get_user_affinity("user_1") == "beauty"


class TestUserWithoutComputedAffinity:
    def test_unknown_user_raises_a_specific_error(
        self,
        product_row: Callable[..., dict],
        event_row: Callable[..., dict],
        build_affinity_processor: Callable[[list[dict], list[dict]], AffinityProcessor],
    ) -> None:
        products = [product_row("p_beauty", "beauty")]

        events = [event_row("user_1", "p_beauty", "view")]

        affinity_processor = build_affinity_processor(products, events)

        with pytest.raises(UserAffinityNotFoundError):
            affinity_processor.get_user_affinity("nonexistent_user")
