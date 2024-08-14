from datetime import datetime

from pydantic import BaseModel
from typing import Optional

class Input(BaseModel):
    text: str

class TextEmbeddingBase(BaseModel):
    text: str = ""
    source: str | None = None
    label: str | None = None
    statement_date: datetime | None = None
    factcheck_date: datetime | None = None
    factcheck_analysis_link: str | None = None

class TextEmbeddingCreate(TextEmbeddingBase):
    pass

class TextEmbedding(TextEmbeddingBase):
    id: int
    created_at: datetime = None
    updated_at: datetime = None
    
    class Config:
        from_attributes = True