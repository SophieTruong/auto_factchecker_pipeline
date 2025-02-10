"""
Create instances of SQLAlchemy engine, session, and base classes
"""

import os
from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Load environment variables
load_dotenv()

# Database connection configuration
is_test_env = os.getenv("TEST_ENV") == "True"
DB_CONFIG = {
    "host": os.getenv("POSTGRES_SERVER") if not is_test_env else os.getenv("POSTGRES_TEST_SERVER"),
    "port": os.getenv("POSTGRES_PORT") if not is_test_env else os.getenv("POSTGRES_TEST_PORT"),
    "database": os.getenv("POSTGRES_DB") if not is_test_env else os.getenv("POSTGRES_TEST_DB"),
    "username": os.getenv("POSTGRES_USER") if not is_test_env else os.getenv("POSTGRES_TEST_USER"),
    "password": os.getenv("POSTGRES_PASSWORD") if not is_test_env else os.getenv("POSTGRES_TEST_PASSWORD")
}

# Construct database URL
POSTGRES_URL = "postgresql://{username}:{password}@{host}:{port}/{database}".format(**DB_CONFIG)
print(f"POSTGRES_URL: {POSTGRES_URL}")

# Create SQLAlchemy engine
engine = create_engine(POSTGRES_URL)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Create declarative base class for models
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

