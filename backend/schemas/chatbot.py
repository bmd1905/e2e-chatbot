from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=10_000)
    agent_type: str = Field(
        ...,
        description="Type of agent to use: 'multi_step', 'prompt_optim', or 'simple'",
    )
    history: Optional[List[Dict[str, str]]] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class FeedbackRequest(BaseModel):
    message_id: int
    is_positive: bool


class ChatResponse(BaseModel):
    response: str
    metadata: Optional[Dict[str, Any]] = {}
