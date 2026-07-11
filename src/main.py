import uvicorn
from fastapi import FastAPI

from src.api.routes import health, recommendations

app = FastAPI(title='recommendations')


app.include_router(health.router)
app.include_router(recommendations.router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)