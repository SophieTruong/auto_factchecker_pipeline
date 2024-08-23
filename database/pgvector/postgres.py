"""
Create instances of SQLAlchemy engine, session, and base classes
"""

import os
from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine, Index
from sqlalchemy.orm import sessionmaker, declarative_base

host=os.getenv("POSTGRES_SERVER") if os.getenv("TEST_ENV") == "False" else "localhost"
port=os.getenv("POSTGRES_PORT")
database=os.getenv("POSTGRES_DB")
username=os.getenv("POSTGRES_USER")
password=os.getenv("POSTGRES_PASSWORD")

POSTGRES_URL=f"postgresql://{username}:{password}@{host}:{port}/{database}"

engine = create_engine(POSTGRES_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()