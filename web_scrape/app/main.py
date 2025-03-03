import fastapi

from model import Claim, WebScrapResult

from politifact import get_politifact_search_results
# from faktabaari import get_faktabaari_search_results
from google_cse import get_cse_search_results
from translator import translate_claim

from concurrent_search import concurrent_search

from utils import logger

import time

app = fastapi.FastAPI()

@app.post("/search", response_model=WebScrapResult)
async def search(search_input: Claim):
        return WebScrapResult(
        claim=search_input.claim, 
        response=await concurrent_search(search_input)
        )