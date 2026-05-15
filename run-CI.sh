#!/bin/bash
set -e

echo "Running Ruff..."
ruff check .

echo "Running Bandit..."
bandit -r pymicmac/

echo "Running Lizard (CCN < 10, Lines < 60)..."
lizard -L 60 -C 10 pymicmac/

echo "Running Pytest with Coverage..."
pytest --cov=pymicmac --cov-fail-under=80 tests/
