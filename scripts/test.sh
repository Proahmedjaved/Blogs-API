#!/bin/bash

# Run tests with coverage
PYTHONPATH=$PWD TESTING=True uv run pytest \
    --cov=app \
    --cov-report=term-missing \
    --cov-report=html \
    --cov-report=xml \
    --cov-fail-under=80 \
    -v 