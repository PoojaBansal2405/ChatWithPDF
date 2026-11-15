from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length = 1,
        max_length = 2000
    )

class ChatResponse(BaseModel):
    notebook_id: str
    question: str
    answer: str

class MessageResponse(BaseModel):
    notebook_id: str
    role: str
    content: str
    timestamp: datetime
