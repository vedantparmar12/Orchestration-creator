from typing import Dict, List, Any, Optional, Callable
import asyncio
from pydantic_ai import Agent, RunContext
from ..agents.models import *
from ..agents.dependencies import *
from ..agents.advisor_agent import AdvisorAgent
from ..agents.coder_agent import CoderAgent  
from ..agents.synthesis_agent import SynthesisAgent
from ..library.agent_templates import AgentTemplate
from ..library.tool_library import ToolDefinition
import logfire
import uuid
from datetime import datetime

class AgentCoordinator:
    """Coordinates multiple agents for complex task execution"""
    
    def __init__(self):
        self.active_agents: Dict[str, Any] = {}
        self.execution_history: List[Dict[str, Any]] = []
    
    async def generate_agent(
        self,
        agent_type: str,
        requirements: str,
        template: Optional[AgentTemplate] = None,
        tools: List[ToolDefinition] = [],
        dependencies: Dict[str, Any] = {},
        configuration: Dict[str, Any] = {}
    ) -> Dict[str, Any]:
        """Generate a new agent based on specifications"""
        
        logfire.info(
            "Agent generation started",
            agent_type=agent_type,
            requirements=requirements[:100] + "..." if len(requirements) > 100 else requirements
        )
        
        agent_id = str(uuid.uuid4())
        
        # Create agent generation task
        generation_task = {
            "agent_id": agent_id,
            "agent_type": agent_type,
            "requirements": requirements,
            "template": template,
            "tools": tools,
            "dependencies": dependencies,
            "configuration": configuration,
            "status": "generating",
            "start_time": datetime.now().isoformat()
        }
        
        try:
            # Use advisor agent to analyze requirements
            advisor = AdvisorAgent()
            advisor_deps = self._create_advisor_dependencies(dependencies)
            
            advisor_result = await advisor.agent.run(
                f"Analyze requirements and provide recommendations for {agent_type} agent: {requirements}",
                deps=advisor_deps
            )
            
            # Use coder agent to generate implementation
            coder = CoderAgent()
            coder_deps = self._create_coder_dependencies(dependencies)
            
            implementation_prompt = f"""
            Generate a complete agent implementation based on:
            
            Agent Type: {agent_type}
            Requirements: {requirements}
            Advisor Recommendations: {advisor_result.data.recommendations}
            Template: {template.name if template else 'None'}
            Tools: {[tool.name for tool in tools]}
            
            Create a fully functional agent with:
            1. System prompt
            2. Tool integrations
            3. Dependency setup
            4. Configuration
            5. Testing instructions
            """
            
            coder_result = await coder.agent.run(
                implementation_prompt,
                deps=coder_deps
            )
            
            # Generate final agent configuration
            agent_config = {
                "agent_id": agent_id,
                "agent_type": agent_type,
                "system_prompt": self._generate_system_prompt(agent_type, requirements, advisor_result.data),
                "tools": [tool.name for tool in tools],
                "dependencies": dependencies,
                "configuration": {
                    **configuration,
                    "template_id": template.id if template else None,
                    "advisor_recommendations": advisor_result.data.recommendations,
                    "confidence_score": advisor_result.data.confidence_score
                },
                "generated_code": coder_result.data.generated_code,
                "file_changes": coder_result.data.file_changes,
                "test_cases": coder_result.data.test_cases,
                "documentation": coder_result.data.documentation,
                "next_steps": coder_result.data.next_steps,
                "created_at": datetime.now().isoformat(),
                "status": "generated"
            }
            
            # Store generated agent
            self.active_agents[agent_id] = agent_config
            
            # Update generation task
            generation_task.update({
                "status": "completed",
                "end_time": datetime.now().isoformat(),
                "result": agent_config
            })
            
            self.execution_history.append(generation_task)
            
            logfire.info(
                "Agent generation completed",
                agent_id=agent_id,
                agent_type=agent_type
            )
            
            return agent_config
            
        except Exception as e:
            generation_task.update({
                "status": "failed",
                "end_time": datetime.now().isoformat(),
                "error": str(e)
            })
            
            self.execution_history.append(generation_task)
            
            logfire.error(
                "Agent generation failed",
                agent_id=agent_id,
                agent_type=agent_type,
                error=str(e)
            )
            
            raise
    
    async def execute_multi_agent_workflow(
        self,
        query: str,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Execute a multi-agent workflow"""
        
        execution_id = str(uuid.uuid4())
        
        logfire.info(
            "Multi-agent workflow started",
            execution_id=execution_id,
            query=query[:100] + "..." if len(query) > 100 else query
        )
        
        if progress_callback:
            progress_callback("workflow_started", "Multi-agent workflow initialization")
        
        try:
            # Step 1: Task analysis and breakdown
            if progress_callback:
                progress_callback("task_analysis", "Analyzing task requirements")
            
            task_analysis = await self._analyze_task(query)
            
            # Step 2: Agent assignment
            if progress_callback:
                progress_callback("agent_assignment", "Assigning specialized agents")
            
            agent_assignments = await self._assign_agents(task_analysis)
            
            # Step 3: Parallel execution
            if progress_callback:
                progress_callback("parallel_execution", "Executing agents in parallel")
            
            agent_results = await self._execute_agents_parallel(agent_assignments, query, progress_callback)
            
            # Step 4: Result synthesis
            if progress_callback:
                progress_callback("result_synthesis", "Synthesizing results")
            
            final_result = await self._synthesize_multi_agent_results(query, agent_results)
            
            if progress_callback:
                progress_callback("workflow_completed", "Multi-agent workflow completed")
            
            logfire.info(
                "Multi-agent workflow completed",
                execution_id=execution_id
            )
            
            return {
                "execution_id": execution_id,
                "query": query,
                "task_analysis": task_analysis,
                "agent_assignments": agent_assignments,
                "agent_results": agent_results,
                "final_result": final_result,
                "status": "completed",
                "execution_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            logfire.error(
                "Multi-agent workflow failed",
                execution_id=execution_id,
                error=str(e)
            )
            
            if progress_callback:
                progress_callback("workflow_failed", f"Workflow failed: {str(e)}")
            
            raise
    
    async def execute_single_agent(
        self,
        query: str,
        agent_type: str = "general",
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Execute a single agent task"""
        
        execution_id = str(uuid.uuid4())
        
        logfire.info(
            "Single agent execution started",
            execution_id=execution_id,
            query=query[:100] + "..." if len(query) > 100 else query,
            agent_type=agent_type
        )
        
        if progress_callback:
            progress_callback("single_agent_started", f"Starting {agent_type} agent")
        
        try:
            # Choose appropriate agent based on type
            if agent_type == "advisor":
                agent = AdvisorAgent()
                deps = self._create_advisor_dependencies({})
            elif agent_type == "coder":
                agent = CoderAgent()
                deps = self._create_coder_dependencies({})
            else:
                # Default to advisor for general queries
                agent = AdvisorAgent()
                deps = self._create_advisor_dependencies({})
            
            if progress_callback:
                progress_callback("agent_execution", f"Executing {agent_type} agent")
            
            # Execute agent
            result = await agent.agent.run(query, deps=deps)
            
            if progress_callback:
                progress_callback("single_agent_completed", f"{agent_type} agent completed")
            
            logfire.info(
                "Single agent execution completed",
                execution_id=execution_id,
                agent_type=agent_type
            )
            
            return {
                "execution_id": execution_id,
                "query": query,
                "agent_type": agent_type,
                "result": result.data.dict() if hasattr(result.data, 'dict') else str(result.data),
                "status": "completed",
                "execution_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            logfire.error(
                "Single agent execution failed",
                execution_id=execution_id,
                agent_type=agent_type,
                error=str(e)
            )
            
            if progress_callback:
                progress_callback("single_agent_failed", f"Agent failed: {str(e)}")
            
            raise
    
    async def _analyze_task(self, query: str) -> Dict[str, Any]:
        """Analyze task requirements"""
        # Simple task analysis - in production this would be more sophisticated
        return {
            "complexity": "medium",
            "estimated_agents": 3,
            "required_skills": ["analysis", "synthesis", "validation"],
            "query": query
        }
    
    async def _assign_agents(self, task_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Assign specialized agents to tasks"""
        assignments = [
            {
                "agent_type": "advisor",
                "task": "Provide context and recommendations",
                "priority": 1
            },
            {
                "agent_type": "coder", 
                "task": "Generate implementation or analysis",
                "priority": 2
            },
            {
                "agent_type": "synthesis",
                "task": "Synthesize results from other agents",
                "priority": 3
            }
        ]
        
        return assignments
    
    async def _execute_agents_parallel(
        self,
        assignments: List[Dict[str, Any]],
        query: str,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Execute multiple agents in parallel"""
        
        tasks = []
        
        for assignment in assignments:
            if assignment["agent_type"] == "advisor":
                agent = AdvisorAgent()
                deps = self._create_advisor_dependencies({})
                task = agent.agent.run(f"{assignment['task']}: {query}", deps=deps)
            elif assignment["agent_type"] == "coder":
                agent = CoderAgent()
                deps = self._create_coder_dependencies({})
                task = agent.agent.run(f"{assignment['task']}: {query}", deps=deps)
            else:
                # Default to advisor
                agent = AdvisorAgent()
                deps = self._create_advisor_dependencies({})
                task = agent.agent.run(f"{assignment['task']}: {query}", deps=deps)
            
            tasks.append((assignment["agent_type"], task))
        
        # Execute all tasks in parallel
        results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
        
        # Process results
        agent_results = {}
        for i, (agent_type, _) in enumerate(tasks):
            result = results[i]
            if isinstance(result, Exception):
                agent_results[agent_type] = {
                    "status": "failed",
                    "error": str(result)
                }
            else:
                agent_results[agent_type] = {
                    "status": "completed",
                    "result": result.data.dict() if hasattr(result.data, 'dict') else str(result.data)
                }
                
            if progress_callback:
                progress_callback(f"{agent_type}_completed", f"{agent_type} agent completed")
        
        return agent_results
    
    async def _synthesize_multi_agent_results(
        self,
        query: str,
        agent_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Synthesize results from multiple agents"""
        
        # Use synthesis agent to combine results
        synthesis_agent = SynthesisAgent()
        synthesis_deps = self._create_synthesis_dependencies({})
        
        synthesis_prompt = f"""
        Synthesize the following multi-agent results for query: {query}
        
        Agent Results:
        {agent_results}
        
        Provide a comprehensive synthesis that combines insights from all agents.
        """
        
        synthesis_result = await synthesis_agent.agent.run(
            synthesis_prompt,
            deps=synthesis_deps
        )
        
        return {
            "synthesis": synthesis_result.data.dict() if hasattr(synthesis_result.data, 'dict') else str(synthesis_result.data),
            "agent_contributions": agent_results,
            "query": query
        }
    
    def _generate_system_prompt(
        self,
        agent_type: str,
        requirements: str,
        advisor_recommendations: ContextOutput
    ) -> str:
        """Generate system prompt for agent"""
        
        base_prompt = f"""You are a specialized {agent_type} agent designed to {requirements}.

Key recommendations from analysis:
{chr(10).join(advisor_recommendations.recommendations)}

Your primary responsibilities:
1. Focus on your specialized domain
2. Provide accurate and helpful responses
3. Follow best practices for {agent_type} tasks
4. Communicate clearly and concisely

Context summary: {advisor_recommendations.context_summary}
Confidence level: {advisor_recommendations.confidence_score:.1%}
"""
        
        return base_prompt
    
    def _create_advisor_dependencies(self, dependencies: Dict[str, Any]) -> AdvisorDependencies:
        """Create advisor agent dependencies"""
        return AdvisorDependencies(
            user_id=dependencies.get("user_id", "system"),
            session_id=dependencies.get("session_id", str(uuid.uuid4())),
            api_keys=dependencies.get("api_keys", {}),
            http_client=dependencies.get("http_client"),
            vector_client=dependencies.get("vector_client"),
            examples_path=dependencies.get("examples_path", ""),
            context_limit=dependencies.get("context_limit", 5)
        )
    
    def _create_coder_dependencies(self, dependencies: Dict[str, Any]) -> CoderDependencies:
        """Create coder agent dependencies"""
        return CoderDependencies(
            user_id=dependencies.get("user_id", "system"),
            session_id=dependencies.get("session_id", str(uuid.uuid4())),
            api_keys=dependencies.get("api_keys", {}),
            http_client=dependencies.get("http_client"),
            workspace_path=dependencies.get("workspace_path", "."),
            git_repo=dependencies.get("git_repo"),
            tool_configs=dependencies.get("tool_configs", {})
        )
    
    def _create_synthesis_dependencies(self, dependencies: Dict[str, Any]) -> BaseDependencies:
        """Create synthesis agent dependencies"""
        return BaseDependencies(
            user_id=dependencies.get("user_id", "system"),
            session_id=dependencies.get("session_id", str(uuid.uuid4())),
            api_keys=dependencies.get("api_keys", {}),
            http_client=dependencies.get("http_client")
        )
    
    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific agent"""
        return self.active_agents.get(agent_id)
    
    def list_active_agents(self) -> List[Dict[str, Any]]:
        """List all active agents"""
        return list(self.active_agents.values())
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get execution history"""
        return self.execution_history
