import numpy as np
import numpy.typing as npt
import traceback

from sqlalchemy.orm import Session
from sqlalchemy import insert, delete, update

from psycopg2._psycopg import IntegrityError

import models

def get_text(db: Session, id:int) -> models.TextEmbedding | None:
    '''
    Retrieve the text embedding instance from the database for the given ID.
    '''
    return db.query(models.TextEmbedding).filter(models.TextEmbedding.id == id).first()

# TODO: test how fast this approach is comparing to this https://docs.sqlalchemy.org/en/14/orm/persistence_techniques.html#using-postgresql-on-conflict-with-returning-to-return-upserted-orm-objects
def get_texts_by_embeddings(
    db: Session,
    query_embedding: npt.ArrayLike, 
    k:int=5
    ):
    '''
    Retrieve of k-nearest text embedding instances (e.g., top k most similar text embeddings) of the given embedding vector from the database.
    '''
    similarity_threshold = 0.7
    query = db.query(models.TextEmbedding, models.TextEmbedding.embedding.cosine_distance(query_embedding) \
                .label("distance")) \
                .filter(models.TextEmbedding.embedding.max_inner_product(query_embedding) < similarity_threshold) \
                .order_by("distance") \
                .limit(k) \
                .all()
    return query

def insert_embedding(db: Session, input: dict, embedding:npt.ArrayLike):
    '''
    Insert ONE fact-checked content to the database
    '''
    new_embedding = models.TextEmbedding(
        **input,
        embedding=embedding
        )
    
    try:
        db.add(new_embedding)
        db.commit()
        db.refresh(new_embedding)
    except Exception as err:
        traceback.print_exc()
        db.rollback()  
    
    return new_embedding

def insert_embeddings(db: Session, inputs:list[dict], embeddings:list[npt.ArrayLike]):
    # Bulk insert: https://docs.sqlalchemy.org/en/20/orm/queryguide/dml.html#orm-bulk-insert-statements
    '''
    Insert MULTIPLE fact-checked contents to the database
    '''
    data = [
        {
            **inputs[i], 
            "embedding": embeddings[i]
        } 
        for i in range(len(inputs))
    ]
    
    try:
        test_embeddings_ids = db.scalars(
            insert(models.TextEmbedding).returning(models.TextEmbedding.id, sort_by_parameter_order=True),
            data
        )
        db.commit()
    except Exception as err:
        traceback.print_exc()
        db.rollback()  
    
    for test_embeddings_id, input_record in zip(test_embeddings_ids, data):
        input_record["id"] = test_embeddings_id
        input_record.pop("embedding",None)
        
    return data

def update_embedding(db: Session, id:int, updating_data):
    '''
    Update a text_embedding instance with matched id
    '''
    try:
        stmt = db.scalars(update(models.TextEmbedding)
                .where(models.TextEmbedding.id == id)
                .values(updating_data)
                .returning(models.TextEmbedding)
                )
        db.commit()
    
    except Exception as err:
        traceback.print_exc()
        db.rollback()  
    
    return stmt.all()
        
def delete_embedding(db: Session, id:int):
    '''
    Delete a text_embedding instance with matched id
    '''
    try:
        stmt = db.scalars(delete(models.TextEmbedding)
                .where(models.TextEmbedding.id == id)
                .returning(models.TextEmbedding.id)
                )
        db.commit()
    
    except Exception as err:
        traceback.print_exc()
        db.rollback()  
    
    return stmt.all()

def get_claim_by_id(db: Session, id:int) -> models.Claim | None:
    '''
    Retrieve the text embedding instance from the database for the given ID.
    '''
    return db.query(models.Claim).filter(models.Claim.id == id).first()

def insert_claims(db: Session, inputs:list[dict]):
    # Bulk insert: https://docs.sqlalchemy.org/en/20/orm/queryguide/dml.html#orm-bulk-insert-statements
    '''
    Insert MULTIPLE fact-checked contents to the database
    '''
    data = inputs
    
    try:
        test_embeddings_ids = db.scalars(
            insert(models.Claim).returning(models.Claim.id, sort_by_parameter_order=True),
            data
        )
        db.commit()
    except Exception as err:
        traceback.print_exc()
        db.rollback()  
    
    for test_embeddings_id, input_record in zip(test_embeddings_ids, data):
        input_record["id"] = test_embeddings_id
        input_record.pop("embedding",None)
        
    return data