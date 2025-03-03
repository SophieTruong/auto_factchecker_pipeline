import os
from dotenv import load_dotenv
import json
import requests

from datetime import datetime

from url_builder import URLBuilder
from utils import (
    is_valid_datetime, 
    is_article_after_timestamp, 
    get_timestamp, 
    get_meta_value,
    logger, 
    aiohttp_get,
    aiohttp_json
)
from factchecked_data import GoogleCustomSearchEngine
from typing import List, Optional

load_dotenv()

CSE_ID = {
    "factcheckorg": os.getenv("CSE_ID_FCO"),
    "fullfact": os.getenv("CSE_ID_FF"),
    "snopes": os.getenv("CSE_ID_Snopes"),
}

def get_url(query:str, se_key=None, se_id=None):

    builder = URLBuilder()

    # .add_param("sort", "") = sort by Relevance
    url = builder.set_scheme("https") \
                .set_authority("www.googleapis.com") \
                .set_path("customsearch/v1") \
                .add_param("key",se_key) \
                .add_param("cx",se_id) \
                .add_param("q",query) \
                .add_param("sort", "") \
                .build()
    
    return url

def get_json_response(url, timestamp: datetime, source: str) -> List[GoogleCustomSearchEngine]:
    
    try:
        response = requests.get(url)

        # response_json = json.loads(response.text)
        response_json = response.json()
        
        response_items = response_json.get("items", [])
        
        if not response_items:
            return []  
        
        else:
            return filter_google_cse_results(response_items, timestamp, source)
            
    except Exception as err:
        
        logger.error(f"Error when parsing response json: {err}")
        
        return []

def filter_google_cse_results(
    response_items: List[dict], 
    timestamp: datetime, 
    source: str = "Google Custom Search Engine"
    ) -> List[GoogleCustomSearchEngine]:
    
    # Process items
    response_data = []
    
    for item in response_items:
        
        article_published_time = get_meta_value(item, "article:published_time")
        
        article_modified_time = get_meta_value(item, "article:modified_time")
        
        # Skip if article is too new
        if any(
            is_article_after_timestamp(time, timestamp) 
            for time in [article_published_time, article_modified_time]
            if is_valid_datetime(time)
        ):
            continue
        
        cse_result = GoogleCustomSearchEngine(
            title = item["title"],
            source = source,
            author = get_meta_value(item, "author"),
            snippet = item["snippet"],
            link = item["link"],
            article_published_time = article_published_time,
            article_modified_time = article_modified_time
        )
        
        response_data.append(cse_result)
    
    return response_data


async def get_cse_search_results(
    query: str, 
    source: str,
    timestamp: Optional[str] = None
    ) -> List[GoogleCustomSearchEngine]:
    try:
        
        if source not in CSE_ID.keys():
            raise ValueError(f"Invalid source: {source}, Source must be one of the following: {CSE_ID.keys()}")
        
        timestamp = get_timestamp(timestamp)
        
        logger.info(f"Getting {source} search results for {query} at {timestamp}")

        cse_api_key = os.getenv("CSE_API_KEY")
        
        cse_id = CSE_ID[source]
        
        url = get_url(query, cse_api_key, cse_id)     
        logger.info(f"URL: {url}")   
        
        # response = get_json_response(url, timestamp, source)
        response = await aiohttp_get(url)
        
        if type(response) == dict and response.get("error"):
            return []
        
        response_json = await aiohttp_json(response)
        
        logger.info(f"Raw response from {source}: {response_json}")
        
        response_items = response_json.get("items", [])
        
        if not response_items:
            return []  
        
        filtered_results =  filter_google_cse_results(response_items, timestamp, source)
        
        return filtered_results
            
    except Exception as e:
        
        logger.info(f"Error getting {source} search results for {query}: {e}")
        
        return []