#!/bin/bash

DOCKER_BUILDKIT=1

# Set directory paths
MODEL_DIR=/Users/sophietruong1992/Desktop/Master_thesis/auto_factchecker_pipeline/model_training_service/mlruns
HF_HOME=/Users/sophietruong1992/.cache/huggingface
CONDA_ENVS=/Users/sophietruong1992/conda_docker_volume/envs
CONDA_PKGS=/Users/sophietruong1992/conda_docker_volume/pkgs

# Create directories if they don't exist
mkdir -p "$MODEL_DIR"
mkdir -p "$CONDA_ENVS"
mkdir -p "$CONDA_PKGS"

# Build the Docker image
DOCKER_BUILDKIT=1 docker build \
  --secret id=env_file,src=.env \
  -t myapp .

# Run the container with volume mounts
docker run \
    -v "$MODEL_DIR:/app/mlruns" \
    -v "$CONDA_ENVS:/opt/anaconda/envs" \
    -v "$CONDA_PKGS:/opt/anaconda/pkgs" \
    -v "$HF_HOME:/root/.cache/huggingface" \
    --env-file .env \
    myapp 