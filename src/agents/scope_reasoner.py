from pydantic_ai import Agent, RunContext
from .base_agent import BaseAgent
from .dependencies import BaseDependencies
from .models import ScopeOutput, TaskComplexity
from typing import List, Dict, Any
import re

class ScopeReasonerAgent(BaseAgent[BaseDependencies, ScopeOutput]):
    """Task scoping with advanced reasoning agent using Pydantic AI"""
    
    def __init__(self, model: str = "openai:gpt-4o", **kwargs):
        super().__init__(
            model=model,
            deps_type=BaseDependencies,
            result_type=ScopeOutput,
            **kwargs
        )
        
        # Register tools
        self.agent.tool(self.analyze_task_complexity)
        self.agent.tool(self.identify_dependencies)
        self.agent.tool(self.assess_risk_factors)
        self.agent.tool(self.estimate_effort)
    
    def get_system_prompt(self) -> str:
        return """You are an expert task scoping and reasoning agent.
        
        Your role is to:
        1. Break down complex tasks into manageable subtasks
        2. Assess the complexity level of tasks
        3. Identify dependencies between tasks
        4. Estimate effort and time requirements
        5. Identify potential risk factors
        
        Use systematic analysis to provide comprehensive task scoping that enables
        effective planning and execution."""
    
    async def analyze_task_complexity(
        self,
        ctx: RunContext[BaseDependencies],
        task_description: str
    ) -> TaskComplexity:
        """Analyze the complexity of a task"""
        # Complexity indicators
        complexity_indicators = {
            'simple': ['fix', 'update', 'change', 'modify', 'small'],
            'complex': ['implement', 'build', 'create', 'develop', 'system'],
            'research': ['analyze', 'investigate', 'research', 'study', 'explore']
        }
        
        task_lower = task_description.lower()
        scores = {}
        
        for complexity, indicators in complexity_indicators.items():
            score = sum(1 for indicator in indicators if indicator in task_lower)
            scores[complexity] = score
        
        # Determine complexity based on highest score
        if scores['research'] >= 2:
            return TaskComplexity.RESEARCH
        elif scores['complex'] >= 2 or len(task_description.split()) > 50:
            return TaskComplexity.COMPLEX
        else:
            return TaskComplexity.SIMPLE
    
    async def identify_dependencies(
        self,
        ctx: RunContext[BaseDependencies],
        task_description: str
    ) -> List[str]:
        """Identify task dependencies"""
        dependencies = []
        
        # Common dependency patterns
        dependency_patterns = {
            r'database|db|storage': 'Database setup and configuration',
            r'api|endpoint|service': 'API design and implementation',
            r'auth|authentication|login': 'Authentication system',
            r'test|testing|unit test': 'Testing framework setup',
            r'ui|interface|frontend': 'User interface development',
            r'deploy|deployment|production': 'Deployment pipeline',
            r'docker|container': 'Containerization setup',
            r'config|configuration|settings': 'Configuration management'
        }
        
        task_lower = task_description.lower()
        
        for pattern, dependency in dependency_patterns.items():
            if re.search(pattern, task_lower):
                dependencies.append(dependency)
        
        # Add generic dependencies for complex tasks
        if len(task_description.split()) > 30:
            dependencies.extend([
                'Requirements analysis',
                'Architecture design',
                'Documentation'
            ])
        
        return dependencies
    
    async def assess_risk_factors(
        self,
        ctx: RunContext[BaseDependencies],
        task_description: str,
        dependencies: List[str]
    ) -> List[str]:
        """Assess potential risk factors"""
        risk_factors = []
        
        task_lower = task_description.lower()
        
        # Risk indicators
        if 'new' in task_lower or 'first time' in task_lower:
            risk_factors.append('Unfamiliar technology or approach')
        
        if 'integration' in task_lower:
            risk_factors.append('Integration complexity')
        
        if 'performance' in task_lower or 'scale' in task_lower:
            risk_factors.append('Performance and scalability challenges')
        
        if 'security' in task_lower:
            risk_factors.append('Security implementation complexity')
        
        if len(dependencies) > 5:
            risk_factors.append('High number of dependencies')
        
        if 'deadline' in task_lower or 'urgent' in task_lower:
            risk_factors.append('Time pressure')
        
        # Generic risks for complex tasks
        if len(task_description.split()) > 40:
            risk_factors.extend([
                'Scope creep potential',
                'Resource allocation challenges'
            ])
        
        return risk_factors
    
    async def estimate_effort(
        self,
        ctx: RunContext[BaseDependencies],
        task_description: str,
        complexity: TaskComplexity,
        dependencies: List[str]
    ) -> str:
        """Estimate effort required for the task"""
        base_effort = {
            TaskComplexity.SIMPLE: 2,
            TaskComplexity.COMPLEX: 8,
            TaskComplexity.RESEARCH: 6
        }
        
        effort_hours = base_effort[complexity]
        
        # Adjust for dependencies
        effort_hours += len(dependencies) * 1.5
        
        # Adjust for task description length (complexity indicator)
        word_count = len(task_description.split())
        if word_count > 30:
            effort_hours *= 1.5
        
        # Convert to time estimate
        if effort_hours < 4:
            return "2-4 hours"
        elif effort_hours < 8:
            return "4-8 hours (half day)"
        elif effort_hours < 16:
            return "1-2 days"
        elif effort_hours < 32:
            return "2-4 days"
        else:
            return "1+ weeks"
    
    async def breakdown_task(
        self,
        ctx: RunContext[BaseDependencies],
        task_description: str
    ) -> List[str]:
        """Break down a task into subtasks"""
        subtasks = []
        
        # Generic subtask patterns
        if 'implement' in task_description.lower():
            subtasks.extend([
                'Analyze requirements',
                'Design architecture',
                'Implement core functionality',
                'Write tests',
                'Documentation'
            ])
        elif 'fix' in task_description.lower():
            subtasks.extend([
                'Identify root cause',
                'Develop fix',
                'Test fix',
                'Deploy fix'
            ])
        else:
            # Default breakdown
            subtasks.extend([
                'Planning and analysis',
                'Implementation',
                'Testing and validation',
                'Documentation and review'
            ])
        
        return subtasks

