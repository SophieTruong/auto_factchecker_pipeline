import argparse
from datetime import datetime

import pandas as pd

from pymilvus import utility

from db_client import create_connection, sentence_transformer_ef
from collection import create_collection, get_collection
from queries import (   
    has_collection, 
    drop_collection, 
    list_collections,
    insert,
    get_entity_num,
    create_index,
    drop_index,
    load_collection,
    release_collection,
    search,
    set_properties
)

from seed_data_processing import merge_all_data

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
print(f"Logger: {logger}")

# Const names
_COLLECTION_NAME = 'text_embeddings'
_ID_FIELD_NAME = 'id'
_VECTOR_FIELD_NAME = 'embedding'
_TEXT_FIELD_NAME = 'text'
_LABEL_FIELD_NAME = 'label'
_SOURCE_NAME = 'source'
_URL = 'url'
_CREATED_AT = 'created_at'

parser = argparse.ArgumentParser()
parser.add_argument("--test", type=str)
args = parser.parse_args()

def _create_and_insert_collection():
    #create collection
    collection = create_collection(
        _COLLECTION_NAME, # has
        _ID_FIELD_NAME, # has
        _VECTOR_FIELD_NAME, # has
        _TEXT_FIELD_NAME, # has
        _LABEL_FIELD_NAME, 
        _SOURCE_NAME, # can computer
        _URL,
        _CREATED_AT,
        )
    
    create_index(collection, _VECTOR_FIELD_NAME)
    
    # alter ttl properties of collection level
    set_properties(collection)

    # show collections
    list_collections()

    # Merge all data  
    df = merge_all_data(test=args.test == "1")
    print("Finished merging data")
    
    # Get text docs
    docs = df.text.values
    
    truncate_docs = [doc[:65535] for doc in docs]
    
    # Embed docs
    print("Embedding docs...") 
    docs_embeddings = sentence_transformer_ef.encode_documents(docs)
        
    labels = df.label.values
    
    sources = df.source.values
    
    urls = df.url.values
    
    created_ats = [utility.mkts_from_datetime(created_at) for created_at in df.created_at.values]
    
    print("Dim:", sentence_transformer_ef.dim, docs_embeddings[0].shape)
    
    data = [
        {
            "id": i, 
            "embedding": docs_embeddings[i], 
            "text": truncate_docs[i], 
            "label": labels[i],
            "source": sources[i],
            "url": urls[i],
            "created_at": created_ats[i],
            }
        for i in range(len(truncate_docs))
    ]
    
    vectors = insert(collection, data)

    collection.flush()
    get_entity_num(collection)
    return collection
    
def main():
    # Create Milvus connection
    logger.info("Creating connection...")
    create_connection()
    
    # Drop collection if exists
    if has_collection(_COLLECTION_NAME):
        drop_collection(_COLLECTION_NAME)
    _create_and_insert_collection()
            
    logger.info("Collection created and inserted...")

    ## Test 
    collection = get_collection(_COLLECTION_NAME)
    
    load_collection(collection)
    
    queries=["Covid-19 originates from a Wuhan lab"]
    query_embeddings = sentence_transformer_ef.encode_queries(queries)


    ### search
    search(collection, _VECTOR_FIELD_NAME, query_embeddings)
    
    release_collection(collection)

if __name__ == "__main__":
    main()