from pydantic import BaseModel

class SearchInput(BaseModel):
    claim: str