from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .. import logger
from ..core.database import get_session
from ..crud.conversation import save_conversation
from ..models.user import User
from ..routers.auth import get_current_active_user
from ..schemas.chatbot import ChatRequest, ChatResponse
from ..services.multi_step_agent import AgentRequest, MultiStepAgent
from ..services.prompt_optim import PromptOptimizationWorkflow
from .auth import oauth2_scheme


router = APIRouter(
    prefix="/api/v1/chatbot",
    tags=["Chatbot"],
    dependencies=[Depends(get_current_active_user)],
    responses={404: {"description": "Not found"}},
)


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    chat_request: ChatRequest,
    db: AsyncSession = Depends(get_session),
    token: str = Depends(oauth2_scheme),
    current_user: User = Depends(get_current_active_user),
):
    """
    Endpoint to handle chatbot interactions.
    """
    try:
        if chat_request.agent_type == "prompt_optim":
            # Initialize the PromptOptimizationWorkflow
            chatbot_workflow = PromptOptimizationWorkflow(timeout=60, verbose=True)

            # Run the workflow
            result = await chatbot_workflow.execute_request_workflow(
                user_prompt=chat_request.prompt.strip(), history=chat_request.history
            )
        elif chat_request.agent_type == "multi_step":
            # Initialize the MultiStepAgent
            multi_step_agent = MultiStepAgent(timeout=120, verbose=True)

            # Prepare the request
            agent_request = AgentRequest(
                user_input=chat_request.prompt.strip(), history=chat_request.history
            )

            # Run the workflow
            result = await multi_step_agent.execute_request_workflow(
                request=agent_request
            )
        else:
            raise ValueError(f"Invalid agent type: {chat_request.agent_type}")

        response_text = str(result).strip()

        # Save the conversation
        await save_conversation(db, current_user.id, chat_request.prompt, response_text)

        return ChatResponse(response=response_text, metadata=chat_request.metadata)

    except Exception as e:
        # Log the error
        logger.error(f"Chatbot error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request.",
        )
