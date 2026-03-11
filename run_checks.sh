#!/bin/bash
set -e
echo "Running Ruff..."
ruff check app/
echo "Running MyPy..."
mypy app/
