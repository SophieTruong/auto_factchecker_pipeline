from fastapi import FastAPI

from translator import translate_claim

import sys
print(f"sys.path: {sys.path}") 

from database.queries import (
    search, 
    release_collection, 
    list_collections,
    set_properties
)
from database.db_client import model, create_connection
from database.collection import create_collection

# Const names
_COLLECTION_NAME = 'text_embeddings'
_ID_FIELD_NAME = 'id'
_VECTOR_FIELD_NAME = 'embedding'
_TEXT_FIELD_NAME = 'text'
_LABEL_FIELD_NAME = 'label'
_SOURCE_NAME = 'source'
_URL = 'url'
_TIMESTAMP = 'timestamp'

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.post("/semantic_search")
async def semantic_search(search_input: dict):
    print(f"Received claim: {search_input.values()}")
    translated_claim = translate_claim(search_input['claim'])
    print(f"Translated claim: {translated_claim}")
    
    query = [translated_claim]
    query_vectors = model.encode(query)

    # Create Milvus connection
    conn = create_connection()
    
    #create collection
    collection = create_collection(
        _COLLECTION_NAME, # has
        _ID_FIELD_NAME, # has
        _VECTOR_FIELD_NAME, # has
        _TEXT_FIELD_NAME, # has
        _LABEL_FIELD_NAME, 
        _SOURCE_NAME, # can computer
        _URL,
        _TIMESTAMP,
        )
    
    collection.load()
    
    # alter ttl properties of collection level
    set_properties(collection)

    # show collections
    list_collections()

    # search
    ret = search(collection, _VECTOR_FIELD_NAME, query_vectors)
    
    release_collection(collection)

    return {"ret": f"{ret}"}