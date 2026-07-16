#!/usr/bin/env bash
# Entrypoint for the Recommendation API.
#
# Instrumentation is fully opt-in and controlled by ENABLE_OTEL:
#
#   ENABLE_OTEL=false (default)  -> plain `uvicorn`, no tracing overhead.
#   ENABLE_OTEL=true              -> the process is wrapped with
#                                    `opentelemetry-instrument`, which
#                                    auto-instruments FastAPI/Starlette
#                                    and exports traces via OTLP.
#
# This mirrors the reference pattern: instrumentation is just a choice
# of run command, not a different build or a code branch in the app.

set -euo pipefail

APP_HOST="${APP_HOST:-0.0.0.0}"
APP_PORT="${APP_PORT:-8080}"
ENABLE_OTEL="${ENABLE_OTEL:-false}"

if [ "${ENABLE_OTEL}" = "true" ]; then
    export OTEL_SERVICE_NAME="${OTEL_SERVICE_NAME:-recommendation_api}"
    export OTEL_EXPORTER_OTLP_ENDPOINT="${OTEL_EXPORTER_OTLP_ENDPOINT:-http://otel:4317}"
    export OTEL_TRACES_EXPORTER="${OTEL_TRACES_EXPORTER:-otlp}"
    export OTEL_METRICS_EXPORTER="${OTEL_METRICS_EXPORTER:-otlp}"
    export OTEL_LOGS_EXPORTER="${OTEL_LOGS_EXPORTER:-none}"

    echo "[entrypoint] OpenTelemetry instrumentation ENABLED"
    echo "[entrypoint] service_name=${OTEL_SERVICE_NAME} otlp_endpoint=${OTEL_EXPORTER_OTLP_ENDPOINT}"

    exec opentelemetry-instrument \
        uvicorn src.main:app --host "${APP_HOST}" --port "${APP_PORT}"
else
    echo "[entrypoint] OpenTelemetry instrumentation disabled (set ENABLE_OTEL=true to enable)"

    exec uvicorn src.main:app --host "${APP_HOST}" --port "${APP_PORT}"
fi
