import asyncio
from typing import List, Optional

from llama_index.core.prompts import PromptTemplate
from llama_index.core.workflow import Event, StartEvent, StopEvent, Workflow, step
from llama_index.llms.groq import Groq
from llama_index.llms.openai import OpenAI
from pydantic import BaseModel

from .. import logger


class OptimizePromptEvent(Event):
    optimized_prompt: str


class GenerateResponseEvent(Event):
    final_prompt: str


class EvaluatePromptOutput(BaseModel):
    needs_optimization: bool


class OptimizePromptOutput(BaseModel):
    optimized_prompt: str


class PromptOptimizationWorkflow(Workflow):
    llm = Groq("llama-3.1-70b-versatile", max_tokens=64)

    evaluation_prompt_template = PromptTemplate(
        "Evaluate the following user prompt to determine if optimization is needed, "
        "considering the conversation history. "
        "User Prompt: {user_prompt}\nConversation History: {history}"
    )

    optimization_prompt_template = PromptTemplate(
        "Improve the following user prompt to better fit the entire conversation history:\n"
        "Original Prompt: {original_prompt}"
    )

    @step
    async def evaluate_prompt(
        self, event: StartEvent
    ) -> GenerateResponseEvent | OptimizePromptEvent:
        # Evaluate the user prompt
        evaluation_response = await self.llm.astructured_predict(
            output_cls=EvaluatePromptOutput,
            prompt=self.evaluation_prompt_template,
            user_prompt=event.user_prompt,
            history=event.get("history", ""),
        )
        needs_optimization = evaluation_response.needs_optimization

        logger.info(f"Is optimization needed: {needs_optimization}")

        if needs_optimization:
            return OptimizePromptEvent(optimized_prompt=event.user_prompt)

        return GenerateResponseEvent(final_prompt=event.user_prompt)

    @step
    async def optimize_prompt(
        self, event: OptimizePromptEvent
    ) -> GenerateResponseEvent:
        # Optimize the user prompt
        optimization_response = await self.llm.astructured_predict(
            output_cls=OptimizePromptOutput,
            prompt=self.optimization_prompt_template,
            original_prompt=event.optimized_prompt,
        )
        optimized_prompt = optimization_response.optimized_prompt

        logger.info(f"Optimized Prompt: {optimized_prompt}")

        return GenerateResponseEvent(final_prompt=optimized_prompt)

    @step
    async def generate_response(self, event: GenerateResponseEvent) -> StopEvent:
        # Generate the chatbot's response
        response_prompt = f"Chatbot response to: {event.final_prompt}"
        chatbot_response = await self.llm.acomplete(response_prompt)
        return StopEvent(result=str(chatbot_response).strip())

    async def execute_request_workflow(
        self, user_prompt: str, history: Optional[str] = ""
    ) -> str:
        try:
            # Evaluate the prompt
            event = await self.evaluate_prompt(
                StartEvent(user_prompt=user_prompt, history=history)
            )
            if isinstance(event, OptimizePromptEvent):
                # Optimize the prompt if needed
                event = await self.optimize_prompt(event)

            # Generate the final response
            response_event = await self.generate_response(event)
            return response_event.result

        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            return "I apologize, but I encountered an error while processing your request. Please try again later."


async def main():
    # Initialize the workflow
    chatbot_workflow = PromptOptimizationWorkflow(timeout=60, verbose=True)

    # Example user prompt
    user_prompt = "MLOps?"

    # Example conversation history
    conversation_history: Optional[List[str]] = [
        "User: Hi, I need help with machine learning.",
        "Chatbot: Sure, I'd be happy to help you with Machine Learning",
    ]

    logger.info(f"User: {user_prompt}")

    # Run the workflow with history as an optional argument
    final_response = await chatbot_workflow.execute_request_workflow(
        user_prompt=user_prompt,
        history="\n".join(conversation_history) if conversation_history else "",
    )

    # Print the chatbot's response
    print(f"Chatbot: {final_response}")


if __name__ == "__main__":
    asyncio.run(main())
