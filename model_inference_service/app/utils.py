import yaml
from datetime import datetime

import logging
import sys

# Configure logger
logger = logging.getLogger("model_inference_service")

logger.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Console handler (prints to stdout)
console_handler = logging.StreamHandler(sys.stdout)

console_handler.setFormatter(formatter)

logger.addHandler(console_handler)

# Prevent logging from propagating to the root logger
logger.propagate = False

logger.info("Logger initialized for model inference service")

def load_yaml_file(file_path: str) -> dict:
    with open(file_path, 'r') as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)
    return data

def parse_datetime(date_str: str) -> datetime:
    creation_ts = datetime.fromtimestamp(int(date_str) / 1000)
    return creation_ts.strftime("%Y-%m-%d %H:%M:%S")