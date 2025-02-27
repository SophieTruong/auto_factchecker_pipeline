"""
Reusable helper functions
"""
from typing import Optional, Dict, List
from dateutil import parser
from datetime import datetime
from factchecked_data import GoogleCustomSearchEngine

def get_json_value(key, json_data):
    if key in json_data.keys():
        return json_data[key]
    return None

def get_meta_value(json_data, key):
    pagemap = get_json_value("pagemap", json_data)
    metatags = None if not pagemap else get_json_value("metatags", pagemap)
    meta_value = None if not metatags else get_json_value(key, metatags[0])
    if ("time" in key) and (meta_value is not None):
        meta_value = parser.parse(meta_value)
    return meta_value 

def get_timestamp(timestamp: Optional[str] = None) -> datetime:
    try:
        if not timestamp:
            return datetime.now()
        return parser.parse(timestamp)
    except (ValueError, TypeError) as e:
        print(f"Error parsing timestamp '{timestamp}': {e}")
        return datetime.now()
    
def is_valid_datetime(time_value: any) -> bool:
    """Validate if value is a datetime object"""
    return isinstance(time_value, datetime)

def is_article_after_timestamp(article_time: Optional[datetime], timestamp: datetime) -> bool:
    """Check if article time is after timestamp"""
    return bool(article_time and article_time.timestamp() > timestamp.timestamp())
