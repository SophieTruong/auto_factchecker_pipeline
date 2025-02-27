import fastapi
from model import SearchInput, SearchResponse, SingleSearchResult
from politifact import get_politifact_search_results
# from faktabaari import get_faktabaari_search_results
from google_cse import get_cse_search_results
from translator import translate_claim

import time
app = fastapi.FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.post("/search", response_model=SearchResponse)
def search(search_input: SearchInput):
    
    start_time = time.time()
    
    responses = []
    for claim in search_input.claims:
        print(f"Original Claim: {claim}")
        
        english_claim = translate_claim(claim.claim, "en")
        print(f"Translated claim: {english_claim}")

        result_dict = {
            "politifact": get_politifact_search_results(english_claim, claim.timestamp),
            "factcheck.org": get_cse_search_results(english_claim, "factcheckorg", claim.timestamp),
            "fullfact": get_cse_search_results(english_claim, "fullfact", claim.timestamp),
            "snopes": get_cse_search_results(english_claim, "snopes", claim.timestamp),
        }
        
        responses.append(SingleSearchResult(claim=claim.claim, response=result_dict))
    
    end_time = time.time()
    print(f"Time taken: {end_time - start_time} seconds")
    
    return SearchResponse(results=responses)
