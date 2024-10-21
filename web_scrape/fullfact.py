import os
from dotenv import load_dotenv
import json
import requests

from url_builder import URLBuilder
from utils import get_meta_value
from factchecked_data import FullFact

load_dotenv()

def get_url(query:str, se_key=None, se_id=None):

    builder = URLBuilder()

    url = builder.set_scheme("https") \
                .set_authority("www.googleapis.com") \
                .set_path("customsearch/v1") \
                .add_param("key",se_key) \
                .add_param("cx",se_id) \
                .add_param("q",query) \
                .build()
    
    return url

def get_json_response(url) -> list[FullFact]:
    
    response_data = []
    
    try:
        response = requests.get(url)
        response_json = json.loads(response.text)
        response_items = response_json.get("items")
        if response_items and len(response_items) > 0:
            for item in response_items:
                factcheck_result = FullFact(
                    title = item["title"],
                    source = "FullFact",
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

def main():
    query = "Ukraine"
    cse_api_key = os.getenv("CSE_API_KEY")
    cse_id = os.getenv("CSE_ID_FF")
    
    url = get_url(query, cse_api_key, cse_id)
    response = get_json_response(url)
    
    for r in response:
        print(r)
        print("_" * 100)
        print("\n")
        
if __name__ == "__main__":
    main()