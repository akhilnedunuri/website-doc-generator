#!/bin/bash
pip install playwright
playwright install chromium
uvicorn app.main:app --host 0.0.0.0 --port $PORT
