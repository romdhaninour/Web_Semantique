#!/bin/bash
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
rm -f backend/data/working_graph.ttl
python backend/data/generate_seed.py
