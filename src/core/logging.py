import logging
import sys
import json
from datetime import datetime


class JsonFormatter(logging.Formatter):
    def format(self, record):

        log_record = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "module": record.name,
            "level": record.levelname.lower(),
            "message": record.getMessage(),
        }
        if hasattr(record, "path"):
            log_record["path"] = record.path
        if hasattr(record, "method"):
            log_record["method"] = record.method
        if hasattr(record, "status_code"):
            log_record["status_code"] = record.status_code
        if hasattr(record, "latency_ms"):
            log_record["latency_ms"] = record.latency_ms
        if hasattr(record, "request_id"):
            log_record["request_id"] = record.request_id
        if hasattr(record, "user_id"):
            log_record["user_id"] = record.user_id
        if hasattr(record, "cold_start"):
            log_record["cold_start"] = record.cold_start
        return json.dumps(log_record)


app_logger = logging.getLogger("recommendation-api")
app_logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JsonFormatter())
app_logger.handlers = []
app_logger.addHandler(handler)


def log_request(record):
    """
    Exemplo de helper para log de requisição.
    `record` é esperado ser um LogRecord com atributos extras
    (p.ex. adicionados via logger.info(msg, extra={...})).
    """
    app_logger.handle(record)


def log_error(message, **kwargs):
    app_logger.error(message, extra=kwargs)
