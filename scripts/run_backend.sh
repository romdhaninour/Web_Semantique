#!/bin/bash
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
