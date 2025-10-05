from pydantic import BaseModel, Field

class AskRequest(BaseModel):
    question: str = Field(..., description="The user's question to retrieve context for")

class AskResponse(BaseModel):
    context: str
    chunks: list[dict]
