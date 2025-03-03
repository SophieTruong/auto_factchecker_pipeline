"""
Reusable helper functions
"""
from typing import Optional, Dict, List
from dateutil import parser
from datetime import datetime
import aiohttp
import json
import logging
import sys
logger = logging.getLogger(__name__)
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

# Test log
logger.info("Logger initialized for web scraper service")

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

async def aiohttp_get(url: str):
    """
    Util function to make a GET request to a given URL with proper error handling
    
    Args:
        url (str): URL to make the GET request to
        
    Returns:
        Dict: Response from the GET request
        
    Raises:
        RequestException: If the request fails
    """    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.request("GET", url) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"{url} request failed: {error_text}")
                    return {"error": f"Failed to fetch from {url}."}
                
                return await response.text()
                
    except aiohttp.ClientError as e:
        logger.error(f"{url} connection error: {e}")
        return {"error": f"Failed to connect to {url}: {str(e)}"}
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse {url} response: {e}")
        return {"error": f"Invalid response from {url}"}
        
    except Exception as e:
        logger.error(f"Unexpected error fetching from {url}: {e}")
        return {"error": f"Unexpected error: {str(e)}"}
    
async def aiohttp_json(txt: str, loads=json.loads):
    return loads(txt)