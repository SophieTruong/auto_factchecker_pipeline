import fastapi

from model import Claim, WebScrapResult

from concurrent_search import concurrent_search

from utils import logger

app = fastapi.FastAPI()

@app.post("/search", response_model=WebScrapResult)
async def search(search_input: Claim):
    logger.info(f"Received search request for claim: {search_input.claim}")
    return WebScrapResult(
        claim=search_input.claim, 
        response=await concurrent_search(search_input)
    )