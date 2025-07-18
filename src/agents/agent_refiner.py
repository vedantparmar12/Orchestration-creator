from pydantic_ai import Agent, RunContext
from .refiner_dependencies import AgentRefinerDependencies
from .refiner_models import AgentRefineOutput
from typing import List, Dict, Any

class AgentRefinerAgent:
    """Agent configuration optimization agent"""
    
    def __init__(self):
        self.agent = Agent(
            model='openai:gpt-4o',
            deps_type=AgentRefinerDependencies,
            result_type=AgentRefineOutput,
            system_prompt=self._get_system_prompt(),
        )
        
        # Add tools to the agent
        self.agent.tool(self.optimize_agent_configuration)
        self.agent.tool(self.evaluate_performance_metrics)
        self.agent.tool(self.apply_behavioral_adjustments)
    
    def _get_system_prompt(self) -> str:
        return """You are a configuration optimization specialist for agent systems.
        Optimize agent configurations to enhance performance, reliability, and alignment with project goals.
        Provide insights and adjustments to improve agent behavior and outcomes."""
    
    async def optimize_agent_configuration(
        self, 
        ctx: RunContext[AgentRefinerDependencies], 
        current_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize agent configurations"""
        optimized_config = current_config.copy()
        
        # Generic optimization logic
        optimized_config['max_retries'] = 5
        optimized_config['parallel_executions'] = True
        optimized_config['error_handling_mode'] = 'robust'
        
        return optimized_config
    
    async def evaluate_performance_metrics(
        self, 
        ctx: RunContext[AgentRefinerDependencies], 
        metrics: Dict[str, float]
    ) -> List[str]:
        """Evaluate and suggest improvements based on performance metrics"""
        recommendations = []
        if metrics.get('response_time', 0) > 1.0:
            recommendations.append("Evaluate and improve processing speed")
        if metrics.get('success_rate', 1.0) < 0.9:
            recommendations.append("Improve error resolution strategies")
        return recommendations
    
    async def apply_behavioral_adjustments(
        self, 
        ctx: RunContext[AgentRefinerDependencies], 
        config: Dict[str, Any]
    ) -> List[str]:
        """Apply behavioral adjustments to the agent"""
        adjustments = []
        current_behavior = config.get('behavior_mode', 'default')
        if current_behavior == 'conservative':
            adjustments.append("Shift to aggressive mode for faster response")
        return adjustments
    
    async def refine(
        self, 
        agent_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Refine agent configuration"""
        current_config = agent_data.get('configuration', {})
        
        deps = AgentRefinerDependencies(
            user_id="system",
            session_id="refine",
            api_keys={},
            http_client=None,
            agent_templates=self._load_agent_templates(),
            performance_metrics=agent_data.get('metrics', {})
        )
        
        result = await self.agent.run(
            f"Refine the configuration for enhanced performance: {current_config}",
            deps=deps
        )
        
        agent_data['configuration'] = result.data.optimized_config
        agent_data['refinement_recommendations'] = result.data.recommendations
        
        return agent_data
    
    def _load_agent_templates(self) -> Dict[str, Any]:
        """Load agent templates for configuration refinement"""
        return {
            'default': {'max_retries': 3, 'parallel_executions': False},
            'performance': {'max_retries': 5, 'parallel_executions': True}
        }
