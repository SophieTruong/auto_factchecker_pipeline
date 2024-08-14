"""
This file defines custom data model classes using SQLAlchemy ORM for interacting with a PostgreSQL database. It incorporates the `pgvector` library to provide vector-based capabilities, which can be used in conjunction with
standard relational database operations."""

from sqlalchemy import Column, Integer, String, Date, text
from sqlalchemy.orm import mapped_column
from sqlalchemy.types import DateTime

from pgvector.sqlalchemy import Vector

from postgres import Base
from utils import utcnow

N_DIM = 768

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
