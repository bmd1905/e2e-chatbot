import asyncio
from typing import Dict, List

from llama_index.core.prompts import PromptTemplate
from llama_index.core.workflow import Event, Workflow, step
from llama_index.llms.groq import Groq
from pydantic import BaseModel, Field

from .. import logger


class Subtask(BaseModel):
    description: str
    result: str = ""


class AgentRequest(BaseModel):
    user_input: str
    history: List[str] = Field(default_factory=list)
    subtasks: List[Subtask] = Field(default_factory=list)


class AgentResponse(BaseModel):
    final_response: str
    subtask_results: Dict[str, str]


class SubtasksOut(BaseModel):
    subtasks: List[str] = Field(
        ..., description="List of subtasks to complete the user request."
    )


class MultiStepAgent(Workflow):
    llm = Groq("llama-3.1-8b-instant", max_tokens=128)

    # Prompt templates
    decomposition_prompt_template = PromptTemplate(
        "Break down the following user request into a maximum of 3 clear, actionable, and self-contained subtasks. "
        "Each subtask should represent a logical step towards fulfilling the request and have a specific, measurable outcome. "
        "Consider the different components or stages involved in completing the request. "
        "Provide sufficient context and instructions for each subtask to be executed independently:\n{user_input}"
    )

    execution_prompt_template = PromptTemplate(
        "Perform the following subtask and provide a detailed result. "
        "Ensure the response is clear and directly addresses the task:\n{subtask_description}"
    )

    combination_prompt_template = PromptTemplate(
        "Synthesize the following subtask results into a comprehensive and well-structured response. "
        "Ensure a smooth flow of information and logical transitions between the different sections. "
        "Address all subtasks in a coherent manner, maintaining clarity and conciseness. "
        "The final output should read as a unified whole, not a collection of separate parts:\n{subtask_results}"
    )

    final_response_prompt_template = PromptTemplate(
        "Refine the following draft response into a polished and natural-sounding final answer. "
        "Focus on clarity, conciseness, and a smooth, engaging writing style. "
        "Ensure the response is easy to understand and free of any awkward phrasing or grammatical errors. "
        "Maintain the original meaning and information while enhancing the overall quality of the writing:\n{draft_response}"
    )

    @step
    async def decompose_task(self, event: Event) -> Event:
        request = event.payload
        response = await self.llm.astructured_predict(
            output_cls=SubtasksOut,
            prompt=self.decomposition_prompt_template,
            user_input=request.user_input,
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
            response = await self.llm.acomplete(
                self.execution_prompt_template.format(
                    subtask_description=subtask.description
                )
            )
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
        response = await self.llm.acomplete(
            self.combination_prompt_template.format(subtask_results=subtask_results)
        )
        return Event(
            payload=AgentResponse(
                final_response=str(response).strip(), subtask_results=subtask_results
            )
        )

    @step
    async def generate_final_response(self, event: Event) -> Event:
        response = event.payload
        final_response = await self.llm.acomplete(
            self.final_response_prompt_template.format(
                draft_response=response.final_response
            )
        )
        response.final_response = str(final_response).strip()
        return Event(payload=response)

    async def execute_request_workflow(self, request: AgentRequest) -> str:
        try:
            # Include history in the decomposition step
            history_text = "\n".join(request.history)
            decomposition_prompt = (
                f"Given the following conversation history:\n{history_text}\n\nUser request:"
                f"{request.user_input}\n\nBreak down the user request into subtasks."
            )

            # Task Decomposition
            event = await self.decompose_task(
                Event(payload=AgentRequest(user_input=decomposition_prompt))
            )
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
