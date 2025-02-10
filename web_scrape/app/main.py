import fastapi
from model import SearchInput, SearchResponse, SingleSearchResult
from fullfact import get_fullfact_search_results
from politifact import get_politifact_search_results
from faktabaari import get_faktabaari_search_results
from factcheckorg import get_factcheckorg_search_results
from translator import translate_claim

app = fastapi.FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.post("/search", response_model=SearchResponse)
def search(search_input: SearchInput):
    responses = []
    for claim in search_input.claims:
        result_dict = {
            # "faktabaari": get_faktabaari_search_results(translate_claim(claim, "fi")), # FaktaBaari: query in Finnish
            "politifact": get_politifact_search_results(translate_claim(claim, "en")), # PoliticFactData: query in English
            "factcheck.org": get_factcheckorg_search_results(translate_claim(claim, "en")), # FactCheckOrg: query in English
            "fullfact": get_fullfact_search_results(translate_claim(claim, "en")) # FullFact
        }
        
        responses.append(SingleSearchResult(claim=claim, response=result_dict))
    return SearchResponse(results=responses)
