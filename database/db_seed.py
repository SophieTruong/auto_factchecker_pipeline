import os
from datetime import datetime
import time 
import traceback

import logging
logger = logging.getLogger(__name__)

import pandas as pd 
import numpy as np
import numpy.typing as npt

from sentence_transformers import SentenceTransformer

import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, Date, text
from sqlalchemy.orm import Session, sessionmaker,mapped_column, declarative_base
from sqlalchemy.sql import expression
from sqlalchemy.types import DateTime
from sqlalchemy.ext.compiler import compiles

from pgvector.sqlalchemy import Vector
from psycopg2._psycopg import IntegrityError


## TODO: use arguments
MODEL = 'msmarco-distilbert-base-dot-prod-v3'
DATAPATH = "./data"
FILENAME = "politifact_factcheck_data.json"

Base = declarative_base()
N_DIM = 768

## Source for database timestamp: https://stackoverflow.com/questions/13370317/sqlalchemy-default-datetime
class utcnow(expression.FunctionElement):
    type = DateTime()
    inherit_cache = True

@compiles(utcnow, 'postgresql')
def pg_utcnow(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"

def get_datetimeobj(datetimestr):
    try:
        return datetime.strptime(datetimestr, '%m/%d/%Y')

    except Exception as e:
        print(f"Error converting datetimestr: {e}")
        return None
    
class TextEmbedding(Base):
    __tablename__ = 'text_embeddings'
    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(String)
    embedding = mapped_column(Vector(N_DIM))
    label = Column(String)
    source = Column(String, nullable=True)
    statement_date = Column(Date, nullable=True)
    factcheck_date = Column(Date, nullable=True)
    factcheck_analysis_link = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=utcnow())
    updated_at = Column(DateTime(timezone=True), server_default=utcnow(), onupdate=utcnow())
    
    def __str__(self):
        output = ''
        for c in self.__table__.columns:
            if c != "embedding":
                output += '{}: {}\n'.format(c.name, getattr(self, c.name))
        return output


def table_exists(engine,name):
    """ 
    Check if table exist. Source:  https://stackoverflow.com/questions/64861610/easily-check-if-table-exists-with-python-sqlalchemy-on-an-sql-database
    """
    ins = sqlalchemy.inspect(engine)
    ret =ins.dialect.has_table(engine.connect(),name)
    print('Table "{}" exists: {}'.format(name, ret))
    return ret


def insert_embeddings(db: Session, embeddings):
    for embedding in embeddings:
        new_embedding = TextEmbedding(
            text=embedding["text"], 
            embedding=embedding["embedding"],
            label=embedding["label"],
            source=embedding["source"],
            statement_date=embedding["statement_date"],
            factcheck_date=embedding["factcheck_date"],
            factcheck_analysis_link=embedding["factcheck_analysis_link"]
            
            )
        db.add(new_embedding)
    try:
        db.commit()
    except IntegrityError as err:
        traceback.print_exc()
        db.rollback()            

def main():
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', filename='vector_database_seeding.log', level=logging.DEBUG)
    logger.info('Started')

    # Encode data into vector embedding
    df = pd.read_json(os.path.join(DATAPATH, FILENAME), lines=True)

    # Connect to PostgreSQL
    engine = create_engine('postgresql://vector:password@db:5432/vectordb')

    # Create a session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # drop all existing table
    Base.metadata.drop_all(engine)
    
    # create table
    Base.metadata.create_all(engine)

    # Text embedding
    model = SentenceTransformer(MODEL, cache_folder='sentence-transformer-model')

    # Encode the data
    start = time.time()

    # Timed code
    encoded_data = model.encode(
        df.statement.tolist(),
    )
    

    end = time.time()

    logger.info(f"elapsed time to encode data: {end - start}")
    
    logger.info(f"shape of encoded_data: {encoded_data.shape}")
    
    data = [
        {
            "id": i, 
            "embedding": encoded_data[i], 
            "text": df.at[i, 'statement'],
            "label": df.at[i, 'verdict'],
            "source": df.at[i,'statement_source'],
            "statement_date": get_datetimeobj(df.at[i,"statement_date"]),
            "factcheck_date": get_datetimeobj(df.at[i,"factcheck_date"]),
            "factcheck_analysis_link": df.at[i,"factcheck_analysis_link"]
        }
        for i in range(len(encoded_data))
    ]
    logger.info(f"Length of seeding data: {len(data)}")

    # Insert embeddings to database
    start = time.time()
    
    insert_embeddings(session, data)
    
    end = time.time()
    
    logger.info(f"elapsed time to insert vector embedding data: {end - start}")

    # Update the ID columns so the the id_sequence is point at the last id of the newly greated table
    statement = text("""BEGIN;
                LOCK TABLE text_embeddings IN EXCLUSIVE MODE;
                SELECT setval('text_embeddings_id_seq', COALESCE((SELECT MAX(id)+1 FROM text_embeddings),1),FALSE); 
                COMMIT;"""
                )

    with engine.connect() as conn:
        conn.execute(statement)
        
    logger.info('Finished')

if __name__ == "__main__":
    main()