import asyncio
from typing import Dict, List

from llama_index.core.prompts import PromptTemplate
from llama_index.core.workflow import Event, Workflow, step
from llama_index.llms.groq import Groq
from llama_index.llms.openai import OpenAI
from pydantic import BaseModel, Field

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


class SubtasksOut(BaseModel):
    subtasks: List[str] = Field(
        ..., description="List of subtasks to complete the user request."
    )


class MultiStepAgent(Workflow):
    # llm = OpenAI(model="gpt-4o-mini", max_tokens=1024, temperature=0.7)
    llm = Groq("llama-3.1-8b-instant")
    # llm = Groq("llama-3.1-70b-versatile")

    @step
    async def decompose_task(self, event: Event) -> Event:
        request = event.payload
        prompt = PromptTemplate(
            "Break down the following user request into a maximum of 3 clear, actionable, and self-contained subtasks. "
            "Each subtask should represent a logical step towards fulfilling the request and have a specific, measurable outcome. "
            "Consider the different components or stages involved in completing the request. "
            "Provide sufficient context and instructions for each subtask to be executed independently:\n{user_input}"
        )
        response = await self.llm.astructured_predict(
            output_cls=SubtasksOut, prompt=prompt, user_input=request.user_input
        )
        subtasks = [
            Subtask(description=task.strip())
            for task in response.subtasks
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
            "Synthesize the following subtask results into a comprehensive and well-structured response. "
            "Ensure a smooth flow of information and logical transitions between the different sections. "
            "Address all subtasks in a coherent manner, maintaining clarity and conciseness. "
            f"The final output should read as a unified whole, not a collection of separate parts:\n{subtask_results}"
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
            "Refine the following draft response into a polished and natural-sounding final answer. "
            "Focus on clarity, conciseness, and a smooth, engaging writing style. "
            "Ensure the response is easy to understand and free of any awkward phrasing or grammatical errors. "
            "Maintain the original meaning and information while enhancing the overall quality of the writing:"
            f"\n{response.final_response}"
        )
        final_response = await self.llm.acomplete(prompt)
        response.final_response = str(final_response).strip()
        return Event(payload=response)

    async def execute_request_workflow(self, request: AgentRequest) -> str:
        try:
            # Task Decomposition
            event = await self.decompose_task(Event(payload=request))
            request = event.payload
            logger.info(f"Subtasks: {request.subtasks}")

            # Parallel Execution
            event = await self.execute_subtasks(Event(payload=request))
            request = event.payload

            # Result Combination
            event = await self.combine_results(Event(payload=request))
            response = event.payload

            # Final Response Generation
            event = await self.generate_final_response(Event(payload=response))
            response = event.payload

            return response.final_response

        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            return "I apologize, but I encountered an error while processing your request. Please try again later."


async def main():
    user_input = (
        "Write a blog post about the benefits of using AI in education in 2 paragraphs."
    )

    agent = MultiStepAgent(timeout=120, verbose=True)
    request = AgentRequest(user_input=user_input)

    final_response = await agent.execute_request_workflow(request=request)
    logger.info(final_response)


if __name__ == "__main__":
    asyncio.run(main())
