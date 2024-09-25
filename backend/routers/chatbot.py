from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .. import logger
from ..core.database import get_session
from ..crud.conversation import save_conversation
from ..models.user import User
from ..routers.auth import get_current_active_user
from ..schemas.chatbot import ChatRequest, ChatResponse
from ..services.prompt_optim import PromptOptimWorkflow

router = APIRouter(
    prefix="/chatbot",
    tags=["Chatbot"],
    dependencies=[Depends(get_current_active_user)],
    responses={404: {"description": "Not found"}},
)


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    chat_request: ChatRequest,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """
    Endpoint to handle chatbot interactions.

    - **prompt**: The user's message to the chatbot.
    - **history**: Previous conversation messages.
    - **metadata**: Additional data like user ID or session ID.
    """
    try:
        # Initialize the workflow
        chatbot_workflow = PromptOptimWorkflow(timeout=60, verbose=True)

        # Prepare history
        history_text = "\n".join(chat_request.history) if chat_request.history else ""

        # Run the workflow
        result = await chatbot_workflow.run(
            user_prompt=chat_request.prompt.strip(), history=history_text
        )

        response_text = str(result).strip()

        await save_conversation(db, current_user.id, chat_request.prompt, response_text)

        return ChatResponse(response=response_text, metadata=chat_request.metadata)

    except Exception as e:
        # Log the error
        logger.error(f"Chatbot error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request.",
        )
