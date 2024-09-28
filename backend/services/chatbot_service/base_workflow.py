from abc import ABC, ABCMeta, abstractmethod

from llama_index.core.workflow import Workflow
from llama_index.llms.gemini import Gemini
from llama_index.llms.groq import Groq
from llama_index.llms.openai import OpenAI


# Create a custom metaclass that combines WorkflowMeta and ABCMeta
class WorkflowABCMeta(type(Workflow), ABCMeta):
    pass


class BaseWorkflow(Workflow, ABC, metaclass=WorkflowABCMeta):
    def __init__(self, timeout: int = 60, verbose: bool = True):
        super().__init__(timeout=timeout, verbose=verbose)
        self.llm = None  # Initialize llm as None

    def set_model(self, model: str):
        # Update the LLM based on the model name
        if model == "llama-3.1-70b-versatile":
            self.llm = Groq(model=model)
        elif model == "gpt-4o":
            self.llm = OpenAI(model=model)
        elif model == "gpt-4o-mini":
            self.llm = OpenAI(model=model)
        elif model == "models/gemini-1.5-pro":
            self.llm = Gemini(model=model)
        elif model == "models/gemini-1.5-flash":
            self.llm = Gemini(model=model)
        else:
            # raise ValueError(f"Unsupported model: {model}")
            self.llm = Groq(model="llama-3.1-70b-versatile")

    @abstractmethod
    async def execute_request_workflow(
        self, user_input: str, history: list = None, model: str = ...
    ) -> str:
        self.set_model(model)  # Set the model before executing the workflow
        pass
