from typing import Dict, Any, Callable
from pydantic import BaseModel
from .state_manager import WorkflowStateManager, PydanticWorkflowConfig
from ..agents.models import TaskComplexity

class TaskRouter:
    """Routes tasks to single or multi-agent execution paths"""

    def __init__(self, workflow_manager: WorkflowStateManager):
        self.workflow_manager = workflow_manager

    def route(self, user_input: str) -> Dict[str, Any]:
        """Determine the complexity of the task and route accordingly"""
        complexity = self.evaluate_complexity(user_input)

        if complexity == TaskComplexity.SIMPLE:
            return self.workflow_manager._single_agent_execution({})
        elif complexity == TaskComplexity.COMPLEX:
            return self.workflow_manager._multi_agent_execution({})

    def evaluate_complexity(self, user_input: str) -> TaskComplexity:
        """Evaluate task complexity"""
        # Simple heuristic for demonstration purposes
        if len(user_input.split()) < 10:
            return TaskComplexity.SIMPLE
        else:
            return TaskComplexity.COMPLEX
