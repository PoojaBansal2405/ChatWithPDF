from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class NotebookCreate(BaseModel):
    title:str = Field(
        ...,
        min_length=1,
        max_length=100
    )

class NotebookResponse(BaseModel):
    notebook_id: str
    title: str
    created_at: datetime