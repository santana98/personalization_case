from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from src.api.routes import health, recommendations
from src.core.middleware import log_requests
from src.model.model_loader import load_model


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_model()
    yield


app = FastAPI(title="Recommendations", lifespan=lifespan)

app.middleware("http")(log_requests)
app.include_router(health.router)
app.include_router(recommendations.router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
