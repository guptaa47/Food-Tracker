#!/usr/bin/env bash
set -e # exit on any error

API_KEY=$(pass usda/api-key)

docker compose -f docker/compose.yaml run \
    --rm \
    -e API_KEY="$API_KEY" \
    -e PYTHONPATH=/workspace/src \
    -p 8501:8501 \
    ml \
    streamlit run src/frontend/app.py --server.address=0.0.0.0
