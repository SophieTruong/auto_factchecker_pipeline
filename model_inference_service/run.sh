# Load environment variables from .env file
set -a  # automatically export all variables
source .env
set +a

ENV_DIR=./env

# Now you can use env variables like:
echo "Using ENV dir: $ENV_DIR"
echo "Using model dir: $MODEL_DIR"
echo "Using other env var: $MODEL_URI"

docker container prune -f
docker build -t inference_service .
docker run -v "$MODEL_DIR:/app/mlruns" -p 8080:8080 -t inference_service