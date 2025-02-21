from typing import Optional
from fastapi import FastAPI, status, HTTPException

import sys
print(f"sys.path: {sys.path}") 

from database.db_client import create_connection
from model import SearchInput, SearchResponse
from services import SemanticSearchService
# Create Milvus connection
conn = create_connection()
    
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.post(
    "/semantic_search",
    response_model=SearchResponse,
    responses={
        200: {"description": "Successfully"},
        400: {"description": "Bad request"},
        500: {"description": "Internal server error"}
    },
    status_code=status.HTTP_200_OK
)
async def semantic_search(
    search_input: SearchInput,
    ) -> Optional[SearchResponse]:
    semantic_search_service = SemanticSearchService()
    search_response = await semantic_search_service.semantic_search(search_input)
    return search_response