import pytest
from fastapi.testclient import TestClient

from src.core.settings import settings
from src.main import app


KNOWN_USER_ID = "u_0350"

UNKNOWN_USER_ID = "user_definitely_not_in_the_dataset"


@pytest.fixture(scope="module")
def client():
    # Using TestClient as a context manager triggers the real
    # `lifespan` defined in src.main -- the full startup sequence runs
    # exactly as it would in production.
    with TestClient(app) as test_client:
        yield test_client

@pytest.mark.integration
class TestHealthEndpoint:
    def test_health_check_returns_ok(self, client: TestClient) -> None:
        response = client.get("/health")

        assert response.status_code == 200

        body = response.json()

        assert body["status"] == "OK"
        assert "version" in body

@pytest.mark.integration
class TestKnownUserRecommendations:
    def test_returns_recommendations_built_from_real_data_and_model(
        self,
        client: TestClient,
    ) -> None:
        response = client.get(f"/recommendations/{KNOWN_USER_ID}")

        assert response.status_code == 200

        body = response.json()

        assert body["user_id"] == KNOWN_USER_ID
        assert body["cold_start"] is False

        products = body["products"]

        assert 0 < len(products) <= settings.recommendation_top_k

        for product in products:
            assert isinstance(product["product_id"], str)
            assert isinstance(product["score"], float)
            # Real model output: a probability, not a placeholder.
            assert 0.0 <= product["score"] <= 1.0

    def test_recommendations_are_sorted_by_score_descending(
        self,
        client: TestClient,
    ) -> None:
        response = client.get(f"/recommendations/{KNOWN_USER_ID}")

        scores = [item["score"] for item in response.json()["products"]]

        assert scores == sorted(scores, reverse=True)

@pytest.mark.integration
class TestUnknownUserColdStart:
    def test_falls_back_to_popular_products(
        self,
        client: TestClient,
    ) -> None:
        response = client.get(f"/recommendations/{UNKNOWN_USER_ID}")

        assert response.status_code == 200

        body = response.json()

        assert body["user_id"] == UNKNOWN_USER_ID
        assert body["cold_start"] is True

        products = body["products"]

        assert 0 < len(products) <= settings.recommendation_top_k

        # Cold start products carry no personalized score.
        for product in products:
            assert product["score"] == 0.0
