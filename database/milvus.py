import time 
import datetime
import json

import pandas as pd

from sentence_transformers import SentenceTransformer
from pymilvus import (
    connections,
    FieldSchema, CollectionSchema, DataType,
    Collection,
    utility
)

_HOST = 'localhost'
_PORT = '19530'

# Const names
_COLLECTION_NAME = 'text_embeddings'
_ID_FIELD_NAME = 'id'
_VECTOR_FIELD_NAME = 'embedding'
_TEXT_FIELD_NAME = 'text'
_LABEL_FIELD_NAME = 'label'
_SOURCE_NAME = 'source'
_STATEMENT_DATE = 'statement_date'
_FACTCHECK_URL = 'factcheck_analysis_link'
_FACTCHECK_DATE = 'factcheck_date'

# Vector parameters
_DIM = 768
_INDEX_FILE_SIZE = 32  # max file size of stored index

# Index parameters
_METRIC_TYPE = 'L2'
_INDEX_TYPE = 'IVF_FLAT'
_NLIST = 1024
_NPROBE = 16
_TOPK = 3

MODEL = 'msmarco-distilbert-base-dot-prod-v3'

model = SentenceTransformer(MODEL,
                            cache_folder='./sentence-transformer-model')

# Create a Milvus connection
def create_connection():
    print(f"\nCreate connection...")
    connections.connect(host=_HOST, port=_PORT)
    print(f"\nList connections:")
    print(connections.list_connections())

# Create a collection
def create_collection(
    name, id_field, vector_field, text_field, label_field, source_field, url_field, statement_date, factcheck_date
    ):
    field1 = FieldSchema(name=id_field, dtype=DataType.INT64, description="int64", is_primary=True)
    field2 = FieldSchema(name=vector_field, dtype=DataType.FLOAT_VECTOR, description="float vector", dim=_DIM,
                         is_primary=False)
    field3 = FieldSchema(name=text_field, dtype=DataType.VARCHAR, description="text", max_length=4000,
                         is_primary=False)
    field4 = FieldSchema(name=label_field, dtype=DataType.VARCHAR, description="label", max_length=50,
                         is_primary=False)
    field5 = FieldSchema(name=source_field, dtype=DataType.VARCHAR, description="source", max_length=100,
                         is_primary=False)
    field6 = FieldSchema(name=url_field, dtype=DataType.VARCHAR, description="factcheck_analysis_link", max_length=500,
                         is_primary=False)
    field7 = FieldSchema(name=statement_date, dtype=DataType.INT64, description="statement_date", is_primary=False)
    field8 = FieldSchema(name=factcheck_date, dtype=DataType.INT64, description="factcheck_date", is_primary=False)
    schema = CollectionSchema(
        fields=[field1, field2, field3, field4, field5, field6, field7, field8], 
        description="collection description"
        )
    collection = Collection(name=name, data=None, schema=schema, properties={"collection.ttl.seconds": 15})
    print("\ncollection created:", name)
    return collection

def has_collection(name):
    return utility.has_collection(name)

# Drop a collection in Milvus
def drop_collection(name):
    collection = Collection(name)
    collection.drop()
    print("\nDrop collection: {}".format(name))

# List all collections in Milvus
def list_collections():
    print("\nlist collections:")
    print(utility.list_collections())

def insert(collection, data):
    collection.insert(data)
    return data[1]

def get_entity_num(collection):
    print("\nThe number of entity:")
    print(collection.num_entities)

def create_index(collection, filed_name):
    index_param = {
        "index_type": _INDEX_TYPE,
        "params": {"nlist": _NLIST},
        "metric_type": _METRIC_TYPE}
    collection.create_index(filed_name, index_param)
    print("\nCreated index:\n{}".format(collection.index().params))

def drop_index(collection):
    collection.drop_index()
    print("\nDrop index sucessfully")


def load_collection(collection):
    collection.load()


def release_collection(collection):
    collection.release()

def search(collection, vector_field, search_vectors):
    search_param = {
        "data": search_vectors,
        "anns_field": vector_field,
        "param": {"metric_type": _METRIC_TYPE, "params": {"nprobe": _NPROBE}},
        "limit": _TOPK,
        "output_fields": ["text", "label", "source", "statement_date", "factcheck_date"]
        }
    results = collection.search(**search_param)
    ret = []
    for i, result in enumerate(results):
        # print("\nSearch result for {}th vector: ".format(i))
        query_result = []
        for j, res in enumerate(result):
            res_dict = res.to_dict()
            try:
                res_dict["entity"]["statement_date"] = datetime.datetime.strptime(str(res.entity.get('statement_date')),"%m%d%Y").date()
                res_dict["entity"]["factcheck_date"] = datetime.datetime.strptime(str(res.entity.get('factcheck_date')),"%m%d%Y").date()
            except Exception as error:
                print(f"Error when trying to convert date int to datetime obj: {error}" )
                print(f"Current date int: {res_dict["entity"]["statement_date"]} AND {res_dict["entity"]["factcheck_date"]}")
            query_result.append(res_dict)
            print(f"Top {i}: {res_dict}")
    
        ret.append(query_result)
    # print("*" * 100)
    # print(ret)
    # print("*" * 100)

def set_properties(collection):
    collection.set_properties(properties={"collection.ttl.seconds": 1800})


def main():
    # create a connection
    create_connection()

    # drop collection if the collection exists
    if has_collection(_COLLECTION_NAME):
        drop_collection(_COLLECTION_NAME)

    # create collection
    collection = create_collection(
        _COLLECTION_NAME, 
        _ID_FIELD_NAME, _VECTOR_FIELD_NAME, _TEXT_FIELD_NAME, _LABEL_FIELD_NAME, _SOURCE_NAME, _FACTCHECK_URL,
        _STATEMENT_DATE, _FACTCHECK_DATE
        )

    # alter ttl properties of collection level
    set_properties(collection)

    # show collections
    list_collections()

    # insert 10000 vectors with 128 dimension
    df = pd.read_json("./data/politifact_factcheck_data.json", lines=True)
    docs = df.statement.values[:10000]
    labels = df.verdict.values[:10000]
    sources = df.statement_source.values[:10000]
    urls = df.factcheck_analysis_link.values[:10000]
    statement_dates = df.statement_date.apply(lambda x: int(datetime.datetime.strptime(x,"%m/%d/%Y").strftime("%m%d%Y"))).values[:10000]
    factcheck_dates = df.factcheck_date.apply(lambda x: int(datetime.datetime.strptime(x,"%m/%d/%Y").strftime("%m%d%Y"))).values[:10000]
    docs_embeddings = model.encode(docs)
    data = [
        {
            "id": i, 
            "embedding": docs_embeddings[i], 
            "text": docs[i], 
            "label": labels[i],
            "source": sources[i],
            "factcheck_analysis_link": urls[i],
            "statement_date": statement_dates[i],
            "factcheck_date": factcheck_dates[i],
            }
        for i in range(len(docs))
    ]
    # print("Data has", len(data), "entities, each with fields: ", data[0].keys())
    # print("Vector dim:", len(data[0]["embedding"]))
    
    vectors = insert(collection, data)

    collection.flush()
    # get the number of entities
    get_entity_num(collection)

    # create index
    create_index(collection, _VECTOR_FIELD_NAME)

    # load data to memory
    load_collection(collection)

    query=["Covid-19 originates from a Wuhan lab"]
    query_vectors = model.encode(query)

    # search
    search(collection, _VECTOR_FIELD_NAME, query_vectors)

    data = pd.read_csv("./data/politifact.csv")
    
    query_arr = data.sources_quote.values

    test_range = [1, 
                  10, 
                  100, 
                  1000, 10000, 
                  ]
    
    semantic_search_stats = {}
    
    for i, max_range in enumerate(test_range):
        inner_dict = {}
        
        print (f'{"*" * 20}\n')
        
        query = query_arr[0:max_range]
        inner_dict["batch_size"] = len(query)
        
        # Encode the data
        start = time.time()

        query_embedding = model.encode(
            query
        )

        end = time.time()

        print(f"elapsed time to encode data: {int(end - start)}")
        print(f"shape of query_embedding: {query_embedding}")

        inner_dict["transformer_encoding"] = {
            "start_time": start,
            "end_time": end,
            "duration": end - start
        }

        # Semantic search
        start = time.time()

        for j in range(len(query_embedding)):
            search(collection, _VECTOR_FIELD_NAME, [query_embedding[j]])

        end = time.time()
        print(f"elapsed time for semantic search: {int(end - start)}")
        
        inner_dict["db_semantic_search"] = {
            "start_time": start,
            "end_time": end,
            "duration": end - start,
        }
        
        print (f'{"*" * 20}\n')
        
        semantic_search_stats[i] = inner_dict
    
    print(f"semantic_search_stats:\n {semantic_search_stats}")
    
    with open("test_milvus.json", "w") as f:
        json.dump(semantic_search_stats, f)

    # release memory
    release_collection(collection)

    # drop collection index
    drop_index(collection)

    # drop collection
    drop_collection(_COLLECTION_NAME)


if __name__ == '__main__':
    main()
