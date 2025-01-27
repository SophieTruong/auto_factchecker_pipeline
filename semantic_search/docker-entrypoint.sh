#!/bin/bash
set -e

# Wait for Milvus to be ready
python database/seed.py --test 1

# Start the main application
exec uvicorn main:app --host 0.0.0.0 --port 8091 --log-level debug 