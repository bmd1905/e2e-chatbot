from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=10_000)
    history: Optional[List[str]] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = {}


class ChatResponse(BaseModel):
    response: str
    metadata: Optional[Dict[str, Any]] = {}
