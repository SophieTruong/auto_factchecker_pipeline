import os
from dotenv import load_dotenv
import json
import requests

from utils import get_meta_value
from url_builder import URLBuilder
from factchecked_data import FactCheckOrg
from typing import List

load_dotenv()

def get_url(query:str, se_key=None, se_id=None):

    builder = URLBuilder()

    url = builder.set_scheme("https") \
                .set_authority("www.googleapis.com/") \
                .set_path("customsearch/v1") \
                .add_param("key",se_key) \
                .add_param("cx",se_id) \
                .add_param("q",query) \
                .build()
    
    return url

def get_json_response(url) -> List[FactCheckOrg]:
    
    response_data = []
    
    try:
        response = requests.get(url)
        print(f"Response from FactCheckOrg: {response.text}")
        response_json = json.loads(response.text)
        response_items = response_json.get("items")
        if response_items is not None and len(response_items) > 0:
            for item in response_items:
                factcheck_result = FactCheckOrg(
                    title = item["title"],
                    source = "FactCheck.org",
                    author = get_meta_value(item, "author"),
                    snippet = item["snippet"],
                    link = item["link"],
                    article_published_time = get_meta_value(item, "article:published_time"),
                    article_modified_time = get_meta_value(item, "article:modified_time")
                )
                response_data.append(factcheck_result)
            
    except Exception as err:
        print(f"Error when parsing response json: {err}")
    
    return response_data

def get_factcheckorg_search_results(query: str) -> List[FactCheckOrg]:
    try:
        print(f"Getting FactCheckOrg search results for {query}")
        cse_api_key = os.getenv("CSE_API_KEY")
        cse_id = os.getenv("CSE_ID_FCO")
        
        url = get_url(query, cse_api_key, cse_id)
    
        response = get_json_response(url)
        
        return response
    except Exception as e:
        print(f"Error getting FactCheckOrg search results for {query}: {e}")
        return []