#!/bin/bash

PORT=${PORT:-8000}

if [ "$1" = "test" ]; then
    uv sync
    /app/.venv/bin/pytest
else
    /app/.venv/bin/fastapi run app/app.py --port $PORT --host "0.0.0.0"
fi