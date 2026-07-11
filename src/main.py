import uvicorn
from fastapi import FastAPI

from src.api.routes import health, recommendations

from src.core.middleware import logging_middleware

app = FastAPI(title='recommendations')

app.middleware("http")(logging_middleware)

app.include_router(health.router)
app.include_router(recommendations.router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)