from fastapi.testclient import TestClient

from src.features.domain import (
    Product,
    Recommendation,
)


def test_should_return_recommendations_for_known_user(
    client: TestClient,
) -> None:
    client.app.state.recommendations_by_user = {
        "u_0001": (
            Recommendation(
                product_id="p_010",
                score=0.91,
            ),
            Recommendation(
                product_id="p_020",
                score=0.87,
            ),
            Recommendation(
                product_id="p_030",
                score=0.81,
            ),
        )
    }

    response = client.get("/recommendations/u_0001")

    assert response.status_code == 200

    payload = response.json()

    assert payload["user_id"] == "u_0001"

    assert payload["cold_start"] is False

    assert payload["products"] == [
        {
            "product_id": "p_010",
            "score": 0.91,
        },
        {
            "product_id": "p_020",
            "score": 0.87,
        },
    ]


def test_should_return_popular_products_for_unknown_user(
    client: TestClient,
) -> None:
    client.app.state.popular_products = (
        Product(
            product_id="p_001",
            category="books",
            price=10.0,
            avg_rating=4.9,
            popularity_score=0.95,
        ),
        Product(
            product_id="p_002",
            category="electronics",
            price=20.0,
            avg_rating=4.8,
            popularity_score=0.90,
        ),
        Product(
            product_id="p_003",
            category="beauty",
            price=30.0,
            avg_rating=4.7,
            popularity_score=0.85,
        ),
    )

    response = client.get("/recommendations/unknown_user")

    assert response.status_code == 200

    payload = response.json()

    assert payload["user_id"] == "unknown_user"

    assert payload["cold_start"] is True

    assert payload["products"] == [
        {
            "product_id": "p_001",
            "score": 0.0,
        },
        {
            "product_id": "p_002",
            "score": 0.0,
        },
    ]


def test_should_respect_recommendation_top_k(
    client: TestClient,
) -> None:
    client.app.state.recommendations_by_user = {
        "u_0001": (
            Recommendation("p_001", 0.95),
            Recommendation("p_002", 0.90),
            Recommendation("p_003", 0.85),
            Recommendation("p_004", 0.80),
            Recommendation("P05", 0.75),
        )
    }

    response = client.get("/recommendations/u_0001")

    assert response.status_code == 200

    payload = response.json()

    assert len(payload["products"]) == 2

    assert payload["products"][0] == {
        "product_id": "p_001",
        "score": 0.95,
    }

    assert payload["products"][1] == {
        "product_id": "p_002",
        "score": 0.90,
    }
