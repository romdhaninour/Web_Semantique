#!/bin/bash
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
pytest backend/tests/test_backend.py -q
cd frontend
npm run build
