import requests
import json
from dateutil import parser
import datetime

import spacy

from url_builder import URLBuilder
from factchecked_data import FaktaBaari

def get_url():
    builder = URLBuilder()

    url = builder.set_scheme("https") \
                .set_authority("faktabaari.fi/") \
                .set_path("search.json") \
                .build()
            
    return url

def get_json_response(url) -> list[FaktaBaari] | None:
    response_data = None
    
    try:
        response = requests.get(url)
        response_json = json.loads(response.text)
        for res in response_json:
            res["date"] = parser.parse(res["date"])
        response_data = [FaktaBaari(**x) for x in response_json]

    except Exception as err:
        print(f"Error when parsing response json: {err}")
    
    return response_data

def keyword_search(query: str, data: list[FaktaBaari], nlp: spacy.lang) -> list[FaktaBaari]:
    query_search_result = []
    
    for res in data:
        doc = nlp(res["title"])
        lemmatized_doc = [token.lemma_ for token in doc]
        
        query_doc = nlp(query)
        lemmatized_query_doc = [token.lemma_ for token in query_doc]
        
        if any(x in lemmatized_doc for x in lemmatized_query_doc):
            query_search_result.append(res)
        
    # Datetime sort: Show the most relevant search result using timestamp
    sorted_query_search_result = sorted(query_search_result, key=lambda t: t["date"], reverse=True)

    return sorted_query_search_result

def main():
    # Set up spacy and load lemmatizer pipeline
    nlp = spacy.load("fi_core_news_sm", disable=['ner', 'parser'])
    lemmatizer = nlp.get_pipe("lemmatizer")
    
    url = get_url()
    
    json_response = get_json_response(url)
    
    # This function is problematic because the delay increase when the amount of response data increase
    start = datetime.datetime.now()
    
    query = "Kamala Harris will win US election 2024"
    search_res = keyword_search(query, json_response, nlp)
    end = datetime.datetime.now()
    for res in search_res:
        print(res)
        print("-" * 100)
    
    print(f"Elipsed time of keyword_search = {end-start}")
    
if __name__ == "__main__":
    main()