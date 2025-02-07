from collections import defaultdict
from dateutil import parser
import re

import requests
from bs4 import BeautifulSoup

from url_builder import URLBuilder
from factchecked_data import PoliticFactData
from typing import List

VERDICT_DICT = {
    'meter-true': 'true', 
    'meter-mostly-true': 'mostly true', 
    'meter-half-true': 'half true', 
    'meter-mostly-false': 'mostly false', 
    'meter-false': 'false', 
    'tom_ruling_pof': 'pants on fire'
}
DATE_PATTERN = re.compile("(?:January|Jan|February|Feb|March|Mar|April|Apr|May|June|Jun|July|Jul|August|Aug|September|Sep|October|Oct|November|Nov|December|Dec)\s\d{1,2}\,\s\d{4}")

def get_url(query:str):

    builder = URLBuilder()

    url = builder.set_scheme("https") \
                .set_authority("www.politifact.com/") \
                .set_path("search/") \
                .add_param("q",query) \
                .build()
    
    return url

def get_html_content(url):
    
    return requests.get(url)

def parse_html_content(req_response: requests.Response) -> List[PoliticFactData]:
    """
    This function parses PoliticalFact content following this path https://www.politifact.com/search/?q=<query>
    This path contains more relevant result w.r.t the search query. 
    More fact-check article can be found from https://www.politifact.com/search/factcheck/?page=<page_number>&q=<query>
    """
    soup = BeautifulSoup(req_response.content, 'html.parser')
    # print(soup.prettify())
    
    ret = []

    for section in soup.find_all('div', 'o-platform__inner'):
        
        if "Fact-checks" in section.find("h2").get_text():
                
            for divs in section.find_all('div', 'o-listease__item'):
                
                factchecked_data = {}
                
                # Get statement_originator
                author = divs.find_all('div', 'c-textgroup__author')
                for a in author:
                    statement_originator, statement_date = list(map(lambda x: x.strip(),a.text.split("stated on ")))
                    factchecked_data["statement_originator"] = statement_originator
                    factchecked_data["statement_date"] = parser.parse(
                        re.findall(DATE_PATTERN, statement_date)[0]
                        )
                    factchecked_data["statement_source"] = statement_date.split("in ")[-1][:-1]
                    
                # Get statement and factcheck_url
                title = divs.find_all('div', 'c-textgroup__title')
                for t in title:
                    factchecked_data["statement"] = t.get_text().strip()
                    factchecked_data["factcheck_analysis_link"] = "www.politifact.com" + t.find("a").get("href")
                    
                # Get factcheck_author and factcheck_date
                meta = divs.find_all('div', 'c-textgroup__meta')
                for m in meta:
                    factcheck_author, factcheck_date = m.get_text().split("•")
                    factchecked_data["factchecker"] = factcheck_author.split("By ")[-1].strip()
                    factchecked_data["factcheck_date"] = parser.parse(re.findall(DATE_PATTERN, factcheck_date)[0])
                
                # Get media (verdict image)
                meta = divs.find_all('img', 'c-image__original')
                verdict_img_url = meta[0].get('src')
                potential_verdict = verdict_img_url.split("/")
                for v in potential_verdict:
                    if v in VERDICT_DICT.keys():
                        factchecked_data["verdict"] = VERDICT_DICT[v]
                        
                ret.append(PoliticFactData(**factchecked_data))
    return ret

def get_politifact_search_results(query: str) -> List[PoliticFactData]:
    
    print(f"Getting Politifact search results for {query}")
    
    url = get_url(query = query)
    
    response = get_html_content(url)
    
    factchecked_data = parse_html_content(response)
    
    print(factchecked_data)
    
    return factchecked_data