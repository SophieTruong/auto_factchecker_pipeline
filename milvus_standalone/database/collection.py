from pymilvus import (
    FieldSchema, 
    CollectionSchema, 
    DataType,
    Collection,
)

from uuid import UUID
from datetime import datetime

# Vector parameters
# _DIM = 768 # Suitable for dot-product models such as msmarco-distilbert-base-dot-prod-v3 
_DIM = 384 # Suitable for normalize_embedding models such as msmarco-MiniLM-L6-cos-v5: https://huggingface.co/sentence-transformers/msmarco-MiniLM-L6-cos-v5

# Create a collection
def create_collection(
    name: str, 
    id_field: UUID, 
    vector_field: str, 
    text_field: str, 
    label_field: str, 
    source_field: str, 
    url_field: str, 
    timestamp_field: datetime, 
    shard_num: int = 2
    ):
    """
    Create a collection with the given name and fields.
    Parameters:
        name: str, name of the collection
        id_field: str, name of the id field
        vector_field: str, name of the vector field
        text_field: str, name of the text field
        label_field: str, name of the label field
        source_field: str, name of the source field
        url_field: str, name of the url field
        timestamp_field: str, name of the timestamp field
        shard_num: int, number of shards
    """
    field1 = FieldSchema(name=id_field, dtype=DataType.INT64, description="UUID", is_primary=True)
    field2 = FieldSchema(name=vector_field, dtype=DataType.FLOAT_VECTOR, description="float vector", dim=_DIM,
                         is_primary=False)
    field3 = FieldSchema(name=text_field, dtype=DataType.VARCHAR, description="text", max_length=65535,
                         is_primary=False, truncate_length=10000)
    field4 = FieldSchema(name=label_field, dtype=DataType.VARCHAR, description="label", max_length=50,
                         is_primary=False)
    field5 = FieldSchema(name=source_field, dtype=DataType.VARCHAR, description="source", max_length=100,
                         is_primary=False)
    field6 = FieldSchema(name=url_field, dtype=DataType.VARCHAR, description="factcheck_analysis_link", max_length=500,
                         is_primary=False)
    field7 = FieldSchema(name=timestamp_field, dtype=DataType.INT64, description="timestamp", max_length=20,
                         is_primary=False)
    
    schema = CollectionSchema(
        fields=[field1, field2, field3, field4, field5, field6, field7], 
        description="collection description",
        # auto_id=True,
        # enable_dynamic_field=True
        )
    
    collection = Collection(
        name=name, 
        data=None, 
        schema=schema,
        shard_num=shard_num,
        properties={"collection.ttl.seconds": 15}
        )
    print("\ncollection created:", name)
    return collection

def get_collection(name: str):
    return Collection(name)