from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type, TypeVar, Generic
from pydantic_ai import Agent, RunContext
from pydantic import BaseModel
from .dependencies import BaseDependencies
import logfire

T = TypeVar('T', bound=BaseDependencies)
R = TypeVar('R', bound=BaseModel)

class BaseAgent(Generic[T, R], ABC):
    """Base class for all Pydantic AI agents with dependency injection"""
    
    def __init__(
        self,
        model: str = "openai:gpt-4o",
        deps_type: Type[T] = None,
        result_type: Type[R] = None,
        system_prompt: str = None,
        tools: Optional[list] = None
    ):
        self.model = model
        self.deps_type = deps_type or BaseDependencies
        self.result_type = result_type
        self.tools = tools or []
        
        # Create Pydantic AI agent
        self.agent = Agent(
            model=self.model,
            deps_type=self.deps_type,
            result_type=self.result_type,
            system_prompt=system_prompt or self.get_system_prompt(),
        )
        
        # Register tools
        self._register_tools()
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent"""
        pass
    
    def _register_tools(self):
        """Register tools with the agent"""
        for tool in self.tools:
            self.agent.tool(tool)
    
    @logfire.instrument('agent_execution')
    async def run(self, user_input: str, deps: T) -> R:
        """Execute the agent with given input and dependencies"""
        try:
            result = await self.agent.run(user_input, deps=deps)
            return result.data
        except Exception as e:
            logfire.error(f"Agent execution failed: {str(e)}")
            raise
    
    async def run_sync(self, user_input: str, deps: T) -> R:
        """Synchronous version of run method"""
        result = self.agent.run_sync(user_input, deps=deps)
        return result.data

class AgentRegistry:
    """Registry for managing agent instances"""
    
    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}
    
    def register(self, name: str, agent: BaseAgent):
        """Register an agent with a name"""
        self._agents[name] = agent
    
    def get(self, name: str) -> Optional[BaseAgent]:
        """Get an agent by name"""
        return self._agents.get(name)
    
    def list_agents(self) -> list:
        """List all registered agents"""
        return list(self._agents.keys())
    
    def remove(self, name: str):
        """Remove an agent from registry"""
        if name in self._agents:
            del self._agents[name]

# Global agent registry instance
agent_registry = AgentRegistry()

class AgentFactory:
    """Factory for creating specialized agents"""
    
    @staticmethod
    def create_agent(
        agent_type: str,
        model: str = "openai:gpt-4o",
        custom_config: Optional[Dict[str, Any]] = None
    ) -> BaseAgent:
        """Create an agent of the specified type"""
        
        config = custom_config or {}
        
        if agent_type == "advisor":
            from .advisor_agent import AdvisorAgent
            return AdvisorAgent(model=model, **config)
        elif agent_type == "coder":
            from .coder_agent import CoderAgent
            return CoderAgent(model=model, **config)
        elif agent_type == "refiner":
            from .refiner_agent import RefinerAgent
            return RefinerAgent(model=model, **config)
        elif agent_type == "scope_reasoner":
            from .scope_reasoner import ScopeReasonerAgent
            return ScopeReasonerAgent(model=model, **config)
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")

class AgentCoordinator:
    """Coordinates multiple agents for complex tasks"""
    
    def __init__(self, registry: AgentRegistry = None):
        self.registry = registry or agent_registry
        self.execution_history = []
    
    async def coordinate_agents(
        self,
        agent_specs: list,
        user_input: str,
        shared_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Coordinate multiple agents to handle a complex task"""
        
        results = {}
        context = shared_context or {}
        
        for spec in agent_specs:
            agent_name = spec.get('name')
            agent_type = spec.get('type')
            dependencies = spec.get('dependencies')
            
            # Get or create agent
            agent = self.registry.get(agent_name)
            if not agent:
                agent = AgentFactory.create_agent(agent_type)
                self.registry.register(agent_name, agent)
            
            # Execute agent
            try:
                result = await agent.run(user_input, dependencies)
                results[agent_name] = {
                    'status': 'success',
                    'result': result,
                    'agent_type': agent_type
                }
                
                # Update shared context
                context[agent_name] = result
                
            except Exception as e:
                results[agent_name] = {
                    'status': 'error',
                    'error': str(e),
                    'agent_type': agent_type
                }
        
        # Store execution history
        self.execution_history.append({
            'input': user_input,
            'results': results,
            'context': context
        })
        
        return results
    
    def get_execution_history(self) -> list:
        """Get the execution history"""
        return self.execution_history
    
    def clear_history(self):
        """Clear the execution history"""
        self.execution_history = []
