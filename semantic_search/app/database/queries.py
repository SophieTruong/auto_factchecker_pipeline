from pymilvus import Collection, utility
from datetime import datetime

# Index parameters
_METRIC_TYPE = 'L2'
_INDEX_TYPE = 'IVF_FLAT'
_NLIST = 1024
_NPROBE = 16
_TOPK = 3

# Check if a collection exists in Milvus
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

# Insert data into a collection
def insert(collection, data):
    collection.insert(data)
    return data[1]

# Get the number of entities in a collection
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

# Search for similar vectors in a collection
def search(collection, vector_field, search_vectors):
    search_param = {
        "data": search_vectors,
        "anns_field": vector_field,
        "param": {"metric_type": _METRIC_TYPE, "params": {"nprobe": _NPROBE}},
        "limit": _TOPK,
        "output_fields": ["text", "label", "source", "timestamp"]
        }
    results = collection.search(**search_param)
    print(f"Result = {results}")
    print(f"Result type = {type(results)}")
    ret = []
    for i, result in enumerate(results):
        # print("\nSearch result for {}th vector: ".format(i))
        query_result = []
        for j, res in enumerate(result):
            res_dict = res.to_dict()
            query_result.append(res_dict)
            print(f"Top {i}: {res_dict}")
    
        ret.append(query_result)
    return ret

# Set properties for a collection
def set_properties(collection):
    collection.set_properties(properties={"collection.ttl.seconds": 1800})
