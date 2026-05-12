#!/bin/bash
set -e
echo "Running Ruff..."
./run-CI-ruff.sh
echo "Running Lizard..."
./run-CI-lizard.sh
echo "Running Mypy..."
./run-CI-mypy.sh
echo "Running Tests..."
./run-CI-tests.sh
