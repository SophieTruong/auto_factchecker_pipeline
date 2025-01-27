import yaml
from datetime import datetime

def load_yaml_file(file_path: str) -> dict:
    with open(file_path, 'r') as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)
    return data

def parse_datetime(date_str: str) -> datetime:
    creation_ts = datetime.fromtimestamp(int(date_str) / 1000)
    return creation_ts