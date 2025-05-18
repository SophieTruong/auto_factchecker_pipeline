from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

from .utils import get_utcnow

class AnnotationSessionBase(BaseModel):
    pass

class AnnotationSessionCreate(AnnotationSessionBase):
    pass

class AnnotationSession(AnnotationSessionBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime = Field(default_factory=get_utcnow, description="Timestamp of creation")
    updated_at: datetime = Field(default_factory=get_utcnow, description="Timestamp of last update")
