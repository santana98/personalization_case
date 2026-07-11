from http import HTTPStatus
from fastapi import APIRouter

router = APIRouter()

@router.get('/health', status_code=HTTPStatus.OK)
def health():
    return {"status": "ok"}