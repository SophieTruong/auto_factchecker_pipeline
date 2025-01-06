from pydantic import BaseModel, ConfigDict, Field

class ClaimInput(BaseModel):
    """
    Input model for the claim detection service.
    """
    model_config = ConfigDict(str_strip_whitespace=True)
    text: str = Field(min_length=1, description="The text of the claim")
