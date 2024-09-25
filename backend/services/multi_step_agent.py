import asyncio
from typing import Dict, List

from llama_index.core.workflow import Event, Workflow, step
from llama_index.llms.openai import OpenAI
from pydantic import BaseModel

from .. import logger


class Subtask(BaseModel):
    description: str
    result: str = ""


class AgentRequest(BaseModel):
    user_input: str
    subtasks: List[Subtask] = []


class AgentResponse(BaseModel):
    final_response: str
    subtask_results: Dict[str, str]


class MultiStepAgent(Workflow):
    llm = OpenAI(model="gpt-4o-mini", max_tokens=1024, temperature=0.7)

    @step
    async def decompose_task(self, event: Event) -> Event:
        request = event.payload
        prompt = (
            f"Break down the following user request into clear, actionable subtasks. "
            f"Consider each logical step or component needed to fulfill the request:\n{request.user_input}"
        )
        response = await self.llm.acomplete(prompt)
        subtasks = [
            Subtask(description=task.strip())
            for task in str(response).split("\n")
            if task.strip()
        ]
        request.subtasks = subtasks
        return Event(payload=request)

    @step
    async def execute_subtasks(self, event: Event) -> Event:
        request = event.payload

        async def execute_single_subtask(subtask: Subtask):
            prompt = (
                f"Perform the following subtask and provide a detailed result. "
                f"Ensure the response is clear and directly addresses the task:\n{subtask.description}"
            )
            response = await self.llm.acomplete(prompt)
            subtask.result = str(response).strip()

        await asyncio.gather(
            *(execute_single_subtask(subtask) for subtask in request.subtasks)
        )
        return Event(payload=request)

    @step
    async def combine_results(self, event: Event) -> Event:
        request = event.payload
        subtask_results = {
            subtask.description: subtask.result for subtask in request.subtasks
        }
        prompt = (
            f"Integrate the following subtask results into a single, coherent response. "
            f"Ensure the final output is logically structured and all subtasks are addressed:\n{subtask_results}"
        )
        response = await self.llm.acomplete(prompt)
        return Event(
            payload=AgentResponse(
                final_response=str(response).strip(), subtask_results=subtask_results
            )
        )

    @step
    async def generate_final_response(self, event: Event) -> Event:
        response = event.payload
        prompt = (
            f"Craft a final response in natural language based on the following information. "
            f"Ensure the response is clear, concise, and flows naturally:\n{response.final_response}"
        )
        final_response = await self.llm.acomplete(prompt)
        response.final_response = str(final_response).strip()
        return Event(payload=response)


async def process_user_request(user_input: str) -> str:
    agent = MultiStepAgent(timeout=120, verbose=True)
    request = AgentRequest(user_input=user_input)

    try:
        # Task Decomposition
        event = await agent.decompose_task(Event(payload=request))
        request = event.payload
        logger.info(f"Subtasks: {request.subtasks}")

        # Parallel Execution
        event = await agent.execute_subtasks(Event(payload=request))
        request = event.payload

        # Result Combination
        event = await agent.combine_results(Event(payload=request))
        response = event.payload

        # Final Response Generation
        event = await agent.generate_final_response(Event(payload=response))
        response = event.payload

        return response.final_response

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return "I apologize, but I encountered an error while processing your request. Please try again later."


async def main():
    user_input = (
        "Write a blog post about the benefits of using AI in education in 2 paragraphs."
    )
    final_response = await process_user_request(user_input)
    logger.info(final_response)


if __name__ == "__main__":
    asyncio.run(main())
