#!/bin/sh

# Playwright path fix
export PLAYWRIGHT_BROWSERS_PATH=/app/ms-playwright
export PLAYWRIGHT_CHROMIUM_ARGS="--no-sandbox --disable-dev-shm-usage"

# Install Chromium (safe even if already installed)
playwright install chromium || true

# Start FastAPI
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
