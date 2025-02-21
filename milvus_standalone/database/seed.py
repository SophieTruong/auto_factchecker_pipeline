import argparse
import os
import dotenv

dotenv.load_dotenv(dotenv.find_dotenv())

import pandas as pd
from datetime import datetime
from db_client import create_connection, model
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

# Const names
_COLLECTION_NAME = 'text_embeddings'
_ID_FIELD_NAME = 'id'
_VECTOR_FIELD_NAME = 'embedding'
_TEXT_FIELD_NAME = 'text'
_LABEL_FIELD_NAME = 'label'
_SOURCE_NAME = 'source'
_URL = 'url'
_TIMESTAMP = 'timestamp'

DATA_DIR = os.getenv("DATA_DIR")
METADATA_DIR = os.getenv("METADATA_DIR")
print(f"DATA_DIR: {DATA_DIR}")
print(f"METADATA_DIR: {METADATA_DIR}")


parser = argparse.ArgumentParser()
parser.add_argument("--test", type=str)
args = parser.parse_args()

def get_data(file_name):
    data_fn = os.path.join(DATA_DIR, file_name)
    metadata_fn = os.path.join(METADATA_DIR, file_name)
    data_df = pd.read_csv(data_fn) # id, author, text
    metadata_df = pd.read_csv(metadata_fn) # id, author, text
    df = pd.merge(data_df, metadata_df, on='id')
    return df

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
        _TIMESTAMP,
        )
    
    create_index(collection, _VECTOR_FIELD_NAME)
    
    # alter ttl properties of collection level
    set_properties(collection)

    # show collections
    list_collections()

    # Get data  
    file_names = os.listdir(DATA_DIR)
    filtered_file_names = [fn for fn in file_names if (fn.endswith(".csv") and fn != "test.csv")]
    if args.test == "1":
        fn = filtered_file_names[0]
        df = get_data(fn)
        print(df.head())
        print(df.columns)
        
    else:
        dfs = []
        for fn in filtered_file_names:
            df = get_data(fn)
            dfs.append(df)
        df = pd.concat(dfs)
        print(df.head())
    
    docs = df.text.values
    labels = ["Nan" for _ in range(len(docs))]
    sources = df.source.values
    urls = df.url.values
    timestamps = [datetime.now().strftime("%Y-%m-%d %H:%M:%S") for _ in range(len(docs))]
    docs_embeddings = model.encode(docs)
    
    data = [
        {
            "id": i, 
            "embedding": docs_embeddings[i], 
            "text": docs[i], 
            "label": labels[i],
            "source": sources[i],
            "url": urls[i],
            "timestamp": timestamps[i],
            }
        for i in range(len(docs))
    ]
    
    vectors = insert(collection, data)

    collection.flush()
    get_entity_num(collection)
    return collection
    
def main():
    # Create Milvus connection
    print(f"Creating connection...")
    create_connection()
    
    # Drop collection if exists
    if has_collection(_COLLECTION_NAME):
        collection = get_collection(_COLLECTION_NAME)
        print(f"collection found: {collection}")
        if collection.is_empty:
            drop_collection(_COLLECTION_NAME)
            _create_and_insert_collection()
    else:
        _create_and_insert_collection()
            
    print(f"Collection created and inserted...")

    ## Test 
    collection = get_collection(_COLLECTION_NAME)
    
    load_collection(collection)
    
    query=["Covid-19 originates from a Wuhan lab"]
    query_vectors = model.encode(query)

    ### search
    search(collection, _VECTOR_FIELD_NAME, query_vectors)
    
    release_collection(collection)

if __name__ == "__main__":
    main()