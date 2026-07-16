from http import HTTPStatus
from fastapi import APIRouter

from src.core.version import APP_VERSION

router = APIRouter()


@router.get("/health", status_code=HTTPStatus.OK)
def health():
    return {
        "status": "OK",
        "version": APP_VERSION,
    }
