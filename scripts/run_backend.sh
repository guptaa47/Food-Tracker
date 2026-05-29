#!/usr/bin/env bash
set -e # exit on any error

API_KEY=$(pass usda/api-key)


docker compose -f docker/compose.yaml run \
    --rm \
    -e API_KEY="$API_KEY" \
    ml \
    python3 src/backend/main.py
