from fastapi import APIRouter

from backend.schemas.chatbot import ChatRequest, ChatResponse
from backend.services.chatbot_service.base_workflow import get_workflow

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    workflow = get_workflow(request.agent_type)
    response = await workflow.execute_request_workflow(
        user_input=request.prompt,
        history=request.history,
        model=request.model,
    )
    return ChatResponse(response=response)
