#!/bin/bash
set -e

echo "--- Running Ruff ---"
ruff check pymicmac/

echo "--- Running Mypy ---"
mypy pymicmac/

echo "--- Running Bandit ---"
bandit -r pymicmac/

echo "--- Running Lizard (CCN < 10, Lines < 80) ---"
lizard -l python -C 10 -L 80 pymicmac/

echo "--- Running Tests with Coverage ---"
python3 -m pytest
