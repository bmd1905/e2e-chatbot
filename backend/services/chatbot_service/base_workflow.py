from abc import ABC, ABCMeta, abstractmethod

from llama_index.core.workflow import Workflow


# Create a custom metaclass that combines WorkflowMeta and ABCMeta
class WorkflowABCMeta(type(Workflow), ABCMeta):
    pass


class BaseWorkflow(Workflow, ABC, metaclass=WorkflowABCMeta):
    @abstractmethod
    async def execute_request_workflow(
        self, user_input: str, history: list = None
    ) -> str:
        pass
