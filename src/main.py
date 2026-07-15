from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from src.api.routes import health, recommendations
from src.core.middleware import log_requests
from src.model.model_loader import load_model
from src.core.settings import settings
from src.features.loader import DataLoader
from src.features.product_processor import ProductProcessor
from src.features.events_processor import EventsProcessor
from src.features.affinity_processor import AffinityProcessor
from src.features.recommendation_builder import RecommendationBuilder


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_model(model_path=settings.model_path)
    loader = DataLoader(
        products_path=settings.products_path,
        events_path=settings.events_path,
    )
    datasets = loader.load()

    product_processor = ProductProcessor(products_df=datasets.products_df)

    events_processor = EventsProcessor(events_df=datasets.events_df)

    affinity_processor = AffinityProcessor(
        product_processor=product_processor,
        events_processor=events_processor,
    )

    recommendation_builder = RecommendationBuilder(
        product_processor=product_processor,
        events_processor=events_processor,
        affinity_processor=affinity_processor,
    )

    app.state.popular_products = product_processor.get_popular_products()

    app.state.recommendations_by_user = recommendation_builder.build()

    yield


app = FastAPI(title="Recommendations", lifespan=lifespan)

app.middleware("http")(log_requests)
app.include_router(health.router)
app.include_router(recommendations.router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
