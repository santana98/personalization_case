import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.routes.recommendations import router
from src.core.settings import settings


@pytest.fixture
def client(
    monkeypatch: pytest.MonkeyPatch,
) -> TestClient:
    monkeypatch.setattr(
        settings,
        "recommendation_top_k",
        2,
    )

    app = FastAPI()

    app.include_router(router)

    app.state.recommendations_by_user = {}
    app.state.popular_products = ()

    return TestClient(app)
