import time
from uuid import uuid4
from fastapi import Request
from src.core.logging import app_logger

logger = app_logger.getChild("middleware")


async def log_requests(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid4()))
    request.state.request_id = request_id

    start_time = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception as e:
        latency_ms = int((time.perf_counter() - start_time) * 1000)
        logger.error(
            "Unhandled exception",
            extra={
                "path": request.url.path,
                "method": request.method,
                "status_code": 500,
                "latency_ms": latency_ms,
                "request_id": request_id,
                "exception": str(e),
            },
        )
        raise

    latency_ms = int((time.perf_counter() - start_time) * 1000)
    logger.info(
        "Request completed",
        extra={
            "path": request.url.path,
            "method": request.method,
            "status_code": response.status_code,
            "latency_ms": latency_ms,
            "request_id": request_id,
        },
    )
    return response
