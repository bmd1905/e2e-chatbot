from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=10_000)
    history: Optional[List[Dict[str, str]]] = Field(default_factory=list)
    agent_type: str = Field(
        ..., description="Type of agent to use: 'multi_step' or 'prompt_optim'"
    )
    metadata: Optional[Dict[str, Any]] = {}


class ChatResponse(BaseModel):
    response: str
    metadata: Optional[Dict[str, Any]] = {}
