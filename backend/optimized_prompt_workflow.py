import asyncio
import json
from typing import List, Optional

from llama_index.core.workflow import Event, StartEvent, StopEvent, Workflow, step
from llama_index.llms.openai import OpenAI
from pydantic import BaseModel

from . import logger


class OptimizePromptEvent(Event):
    optimized_prompt: str


class GenerateResponseEvent(Event):
    final_prompt: str


class EvaluatePromptOut(BaseModel):
    is_optimize: bool


class OptimizePromptOut(BaseModel):
    optimized_prompt: str


class ChatbotWorkflow(Workflow):
    llm = OpenAI(model="gpt-4o", max_tokens=32, temperature=0.2)
    eval_llm = llm.as_structured_llm(output_cls=EvaluatePromptOut)
    optim_llm = llm.as_structured_llm(output_cls=OptimizePromptOut)

    # Updated prompt to include history
    prompt = (
        "Evaluate the following user prompt to determine if optimization is needed, "
        "considering the conversation history. "
        "User Prompt: {user_prompt}\nConversation History: {history}"
    )

    @step
    async def evaluate_prompt(
        self, ev: StartEvent
    ) -> GenerateResponseEvent | OptimizePromptEvent:
        # Retrieve history from the event, defaulting to an empty string if not provided
        history = ev.get("history", "")

        prompt = self.prompt.format(
            user_prompt=ev.user_prompt.strip(), history=history.strip()
        )

        logger.info(f"Prompt: {prompt}")

        response = await self.eval_llm.acomplete(prompt)

        is_optimize = EvaluatePromptOut(**json.loads(response.text)).is_optimize

        logger.info(f"Is optimization needed: {is_optimize}")

        if is_optimize:
            return OptimizePromptEvent(optimized_prompt=ev.user_prompt)

        return GenerateResponseEvent(final_prompt=ev.user_prompt)

    @step
    async def optimize_prompt(self, ev: OptimizePromptEvent) -> GenerateResponseEvent:
        prompt = ev.optimized_prompt
        optimization_prompt = (
            "Improve the following user prompt to better fit the entire conversation history:\n"
            f"Original Prompt: {prompt}"
        )
        response = await self.optim_llm.acomplete(optimization_prompt)
        optimized_prompt = str(response).strip()

        optimized_prompt = OptimizePromptOut(
            **json.loads(response.text)
        ).optimized_prompt

        logger.info(f"Optimization needed: {optimized_prompt}")

        return GenerateResponseEvent(final_prompt=optimized_prompt)

    @step
    async def generate_response(self, ev: GenerateResponseEvent) -> StopEvent:
        # You can incorporate conversation history from context if needed
        response_prompt = f"Chatbot response to: {ev.final_prompt}"
        chatbot_response = await self.llm.acomplete(response_prompt)
        return StopEvent(result=str(chatbot_response).strip())


async def main():
    # Initialize the workflow
    chatbot_workflow = ChatbotWorkflow(timeout=60, verbose=True)

    # Example user prompt
    user_prompt = "MLOps?"

    # Example conversation history (can be None or omitted)
    history: Optional[List[str]] = [
        "User: Hi, I need help with machine learning operations.",
        "Chatbot: Sure, I'd be happy to help you with MLOps. What specifically would you like to know?",
    ]

    logger.info(f"User: {user_prompt}")

    # Run the workflow with history as an optional argument
    result = await chatbot_workflow.run(
        user_prompt=user_prompt, history="\n".join(history) if history else ""
    )

    # Print the chatbot's response
    print(f"Chatbot: {str(result)}")


if __name__ == "__main__":
    asyncio.run(main())
