from pydantic_ai import Agent, RunContext
from .refiner_dependencies import PromptRefinerDependencies
from .refiner_models import PromptRefineOutput
from typing import List, Dict, Any

class PromptRefinerAgent:
    """Autonomous prompt optimization agent"""
    
    def __init__(self):
        self.agent = Agent(
            model='openai:gpt-4o',
            deps_type=PromptRefinerDependencies,
            result_type=PromptRefineOutput,
            system_prompt=self._get_system_prompt(),
        )
        
        # Add tools to the agent
        self.agent.tool(self.analyze_prompt_effectiveness)
        self.agent.tool(self.apply_prompt_patterns)
        self.agent.tool(self.test_prompt_variations)
    
    def _get_system_prompt(self) -> str:
        return """You are a prompt engineering expert that optimizes system prompts for maximum effectiveness.
        Analyze existing prompts, apply proven patterns, and create variations that improve agent performance.
        Focus on clarity, specificity, and task-oriented instructions."""
    
    async def analyze_prompt_effectiveness(
        self, 
        ctx: RunContext[PromptRefinerDependencies], 
        current_prompt: str
    ) -> str:
        """Analyze current prompt for effectiveness"""
        return f"Analyzed prompt effectiveness: {current_prompt[:50]}..."
    
    async def apply_prompt_patterns(
        self, 
        ctx: RunContext[PromptRefinerDependencies], 
        prompt: str
    ) -> str:
        """Apply patterns to optimize the prompt"""
        optimized_prompt = prompt
        # Example pattern application
        for pattern in ctx.deps.prompt_patterns:
            optimized_prompt = optimized_prompt.replace(pattern['find'], pattern['replace'])
        return optimized_prompt
    
    async def test_prompt_variations(
        self, 
        ctx: RunContext[PromptRefinerDependencies], 
        prompt: str
    ) -> float:
        """Test different variations of the prompt"""
        return 0.95  # Example effectiveness score
    
    async def refine(
        self, 
        agent_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Refine agent prompts"""
        current_prompt = agent_data.get('system_prompt', '')
        
        deps = PromptRefinerDependencies(
            user_id="system",
            session_id="refine",
            api_keys={},
            http_client=None,
            prompt_patterns=self._load_prompt_patterns(),
            evaluation_metrics=['clarity', 'specificity', 'effectiveness']
        )
        
        result = await self.agent.run(
            f"Optimize this system prompt for better agent performance: {current_prompt}",
            deps=deps
        )
        
        agent_data['system_prompt'] = result.data.optimized_prompt
        agent_data['prompt_improvements'] = result.data.improvements_made
        
        return agent_data
    
    def _load_prompt_patterns(self) -> List[Dict[str, str]]:
        """Load predefined prompt patterns"""
        return [
            {'find': '{USER}', 'replace': '{Agent}'},
            {'find': '[EXAMPLE]', 'replace': '[Sample]'}
        ]
