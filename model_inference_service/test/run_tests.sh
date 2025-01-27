#!/bin/bash
set -a  # automatically export all variables
source .env
set +a

ENV_DIR=./env

# Now you can use env variables like:
echo "Using ENV dir: $ENV_DIR"
echo "Using model dir: $MODEL_DIR"
echo "Using other env var: $MODEL_URI"

# Run unit tests first
python -m pytest test/test_main.py -v

echo "If Unit tests passed, running load tests..."

# If unit tests pass, run load tests
if [ $? -eq 0 ]; then
    echo "Unit tests passed, running load tests..."
    apt-get update && apt-get install curl -y
    curl -X POST http://model_inference:8080/predict -H "Content-Type: application/json" -d '["Test sentence"]'
    python test/load_test.py
else
    echo "Unit tests failed, skipping load tests"
    exit 1
fi 

cat run_tests.sh