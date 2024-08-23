import os
import time 
import traceback

import logging
logger = logging.getLogger(__name__)

import pandas as pd 
import numpy as np
import numpy.typing as npt

from sentence_transformers import SentenceTransformer

from psycopg2._psycopg import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import text, insert

from postgres import engine, Base, SessionLocal
from utils import get_datetimeobj
from models import TextEmbedding, N_DIM
from crud import insert_embeddings

## TODO: use arguments
DATAPATH = "./data"
FILENAME = "politifact_factcheck_data.json"
MODEL = 'msmarco-distilbert-base-dot-prod-v3'

# Text embedding
model = SentenceTransformer(MODEL,
                            cache_folder='./sentence-transformer-model')

def main():
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', filename='./logging/vector_database_seeding.log', level=logging.DEBUG)
    logger.info('Started')
        
    # Encode data into vector embedding
    df = pd.read_json(os.path.join(DATAPATH, FILENAME), lines=True)

    # Encode the data
    start = time.time()

    encoded_data = model.encode(
        df.statement.tolist(),
    )

    end = time.time()
    
    logger.info(f"elapsed time to encode data: {end - start}")
    
    logger.info(f"shape of encoded_data: {encoded_data.shape}")
    
    # Convert JSON data into DB model data
    df.rename(columns={
        "statement": "text",
        "verdict": "label",
        "statement_source": "source"
    }, inplace=True)
    
    df["statement_date"] = df["statement_date"].apply(get_datetimeobj)
    df["factcheck_date"] = df["factcheck_date"].apply(get_datetimeobj)
    
    data = df.to_dict(orient="records")
    
    logger.info(f"Length of seeding data: {len(data)}")

    # PostgreSQL functions
    logger.info(f"Postgresql engine: {engine}")

    # drop all existing table
    Base.metadata.drop_all(engine)
    
    session = SessionLocal()
    logger.info(f"Postgresql session: {session}")
    
    # create table
    Base.metadata.create_all(engine)
    
    # Insert embeddings to database
    start = time.time()
    
    insert_success = insert_embeddings(session, data, encoded_data)
    
    end = time.time()
    
    logger.info(f"Insert successed == {insert_success}")
    logger.info(f"elapsed time to insert vector embedding data: {end - start}")

    # Update the ID columns so the the id_sequence is point at the last id of the newly greated table
    statement = text("""BEGIN;
                LOCK TABLE text_embeddings IN EXCLUSIVE MODE;
                SELECT setval('text_embeddings_id_seq', COALESCE((SELECT MAX(id)+1 FROM text_embeddings),1),FALSE); 
                COMMIT;"""
                )
    try:
        session.execute(statement)
        session.commit()
    except Exception as err:
        traceback.print_exc()
        session.rollback()  
    finally:
        session.close()
    logger.info('Finished')
    

if __name__ == "__main__":
    main()