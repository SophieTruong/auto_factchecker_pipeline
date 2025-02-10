"""
Metric table storing metadata and metrics
Columns:
- model_id: UUID
- start_date: datetime
- end_date: datetime
- f1_score: float
- f1_micro: float      
- f1_macro: float
- f1_weighted: float
- precision: float
- recall: float
- accuracy: float
"""

import uuid
from sqlalchemy import Column, Float, DateTime, UUID
from datetime import datetime

from database.sqlite import Base

class Metric(Base):
    __tablename__ = "metrics"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    model_id = Column(UUID)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    f1_score = Column(Float)
    f1_micro = Column(Float)
    f1_macro = Column(Float)
    f1_weighted = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    accuracy = Column(Float)