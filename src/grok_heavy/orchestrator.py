from typing import Dict, Any, List, Callable, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor
from pydantic_ai import Agent, RunContext
from ..agents.models import *
from ..agents.dependencies import *
from ..utils.openrouter_config import get_model_string, get_openrouter_client
from ..utils.pydantic_ai_config import create_openrouter_model, get_configured_model_name
import logfire
from rich.console import Console
import os

class GrokHeavyOrchestrator:
    """Grok heavy-style multi-agent orchestration with live progress"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.console = Console()
        
        # Get OpenRouter model configuration
        self.model_name = get_configured_model_name()
        self.openrouter_model = create_openrouter_model()
        
        # Initialize question generator
        self.question_generator = Agent(
            model=self.openrouter_model,
            result_type=GrokQuestionSet,
            system_prompt=self._get_question_generation_prompt()
        )
        
        # Initialize specialized agents
        self.agents = {
            'research_agent': self._create_research_agent(),
            'analysis_agent': self._create_analysis_agent(),
            'perspective_agent': self._create_perspective_agent(),
            'verification_agent': self._create_verification_agent()
        }
        
        # Initialize synthesis agent
        self.synthesis_agent = Agent(
            model=self.openrouter_model,
            result_type=GrokSynthesisOutput,
            system_prompt=self._get_synthesis_prompt()
        )
        
        # Initialize deep reflection agent (Phase 5)
        self.reflection_agent = Agent(
            model=self.openrouter_model,
            result_type=GrokSynthesisOutput,
            system_prompt=self._get_reflection_prompt()
        )
    
    def _get_question_generation_prompt(self) -> str:
        return """You are a question generation expert for deep multi-agent analysis.
        
        Given a user query, generate 4 specialized research questions that will enable
        comprehensive analysis from different perspectives:
        
        1. RESEARCH question: Focus on factual background and foundational information
        2. ANALYSIS question: Focus on achievements, contributions, and impact analysis  
        3. PERSPECTIVE question: Focus on alternative viewpoints and broader context
        4. VERIFICATION question: Focus on fact-checking and current status validation
        
        Make questions specific, actionable, and designed to gather complementary information.
        Each question should lead to insights that others might miss."""
    
    def _get_synthesis_prompt(self) -> str:
        return """You are a synthesis expert who combines multiple agent outputs into comprehensive analysis.
        
        Given outputs from research, analysis, perspective, and verification agents, create a
        comprehensive synthesis that:
        
        1. Combines all perspectives into a coherent narrative
        2. Identifies key insights and patterns
        3. Provides confidence assessment
        4. Summarizes methodology used
        5. Lists all sources and agent contributions
        
        Create a Grok heavy-style response that is thorough, nuanced, and insightful."""
    
    def _get_reflection_prompt(self) -> str:
        return """You are an expert in meta-analysis and deep reflection.
        
        Given an initial synthesis and the raw agent results, enhance the analysis by:
        
        1. DEEPENING INSIGHTS: Find hidden connections and patterns not immediately obvious
        2. META-ANALYSIS: Reflect on the methodology and identify potential blind spots
        3. NOVEL INTERPRETATIONS: Propose alternative frameworks for understanding the findings
        4. PHILOSOPHICAL DEPTH: Add layers of meaning and broader implications
        5. CRYSTALLIZED WISDOM: Distill the essence into profound takeaways
        
        This is Phase 5 - the final deepening that transforms good analysis into extraordinary insight.
        Make it worthy of the 'Grok heavy' standard."""
    
    async def run_grok_heavy_analysis(
        self, 
        user_query: str, 
        progress_callback: Optional[Callable] = None
    ) -> GrokSynthesisOutput:
        """Run complete Grok heavy analysis with live progress"""
        
        # Step 1: Generate specialized questions
        if progress_callback:
            progress_callback("question_generation", "Generating specialized research questions...")
        
        questions = await self._generate_questions(user_query)
        
        if progress_callback:
            progress_callback("questions_generated", questions)
        
        # Step 2: Execute parallel agents
        if progress_callback:
            progress_callback("parallel_execution", "Starting parallel agent execution...")
        
        agent_results = await self._execute_parallel_agents(
            questions, 
            user_query, 
            progress_callback
        )
        
        # Step 3: Synthesize results
        if progress_callback:
            progress_callback("synthesis", "Synthesizing comprehensive analysis...")
        
        initial_result = await self._synthesize_results(
            user_query, 
            questions, 
            agent_results
        )
        
        # Step 4: Deep Reflection & Insights Enhancement (Phase 5)
        if progress_callback:
            progress_callback("deep_reflection", "Phase 5: Deep reflection and insights enhancement...")
        
        final_result = await self._enhance_with_deep_reflection(
            user_query,
            initial_result,
            agent_results
        )
        
        if progress_callback:
            progress_callback("complete", final_result)
        
        return final_result
    
    async def _generate_questions(self, user_query: str) -> GrokQuestionSet:
        """Generate 4 specialized research questions"""
        result = await self.question_generator.run(
            f"Generate 4 specialized research questions for: {user_query}"
        )
        return result.data
    
    @logfire.instrument('parallel_agent_execution')
    async def _execute_parallel_agents(
        self, 
        questions: GrokQuestionSet, 
        user_query: str,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Execute 4 agents in parallel with live progress tracking"""
        
        # Prepare agent tasks
        tasks = [
            self._execute_agent_with_progress(
                'research_agent', 
                questions.research_question, 
                user_query,
                progress_callback
            ),
            self._execute_agent_with_progress(
                'analysis_agent', 
                questions.analysis_question, 
                user_query,
                progress_callback
            ),
            self._execute_agent_with_progress(
                'perspective_agent', 
                questions.perspective_question, 
                user_query,
                progress_callback
            ),
            self._execute_agent_with_progress(
                'verification_agent', 
                questions.verification_question, 
                user_query,
                progress_callback
            )
        ]
        
        # Execute all agents concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        agent_results = {}
        agent_names = ['research_agent', 'analysis_agent', 'perspective_agent', 'verification_agent']
        
        for i, result in enumerate(results):
            agent_name = agent_names[i]
            if isinstance(result, Exception):
                agent_results[agent_name] = {
                    "error": str(result),
                    "status": "failed"
                }
            else:
                agent_results[agent_name] = result
        
        return agent_results
    
    async def _execute_agent_with_progress(
        self, 
        agent_name: str, 
        question: str, 
        context: str,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Execute single agent with progress tracking"""
        
        if progress_callback:
            progress_callback(f"{agent_name}_started", f"🔄 {agent_name} analyzing...")
        
        try:
            agent = self.agents[agent_name]
            
            # Create appropriate dependencies
            deps = self._create_agent_dependencies(agent_name)
            
            # Run agent
            result = await agent.run(
                f"Context: {context}\nSpecific task: {question}",
                deps=deps
            )
            
            if progress_callback:
                progress_callback(f"{agent_name}_completed", f"✅ {agent_name} completed")
            
            return {
                "status": "completed",
                "data": result.data,
                "question": question
            }
            
        except Exception as e:
            if progress_callback:
                progress_callback(f"{agent_name}_failed", f"❌ {agent_name} failed: {str(e)}")
            
            return {
                "status": "failed",
                "error": str(e),
                "question": question
            }
    
    def _create_agent_dependencies(self, agent_name: str) -> Any:
        """Create dependencies for specific agent"""
        # Create basic dependencies for now
        import httpx
        
        base_deps = {
            "user_id": "grok_heavy",
            "session_id": "analysis_session",
            "api_keys": {},
            "http_client": httpx.AsyncClient()
        }
        
        return base_deps
    
    def _create_research_agent(self) -> Agent:
        """Create specialized research agent"""
        return Agent(
            model=self.openrouter_model,
            result_type=ResearchOutput,
            system_prompt="""You are a research specialist focused on gathering comprehensive 
            factual information. Conduct thorough research using available tools and provide
            detailed, well-sourced findings with high accuracy."""
        )
    
    def _create_analysis_agent(self) -> Agent:
        """Create specialized analysis agent"""
        return Agent(
            model=self.openrouter_model,
            result_type=AnalysisOutput,
            system_prompt="""You are an analysis expert focused on evaluating achievements,
            contributions, and impact. Provide deep analytical insights with supporting evidence
            and quantitative assessments where possible."""
        )
    
    def _create_perspective_agent(self) -> Agent:
        """Create specialized perspective agent"""
        return Agent(
            model=self.openrouter_model,
            result_type=PerspectiveOutput,
            system_prompt="""You are a perspective analyst focused on alternative viewpoints
            and broader context. Explore different angles, potential criticisms, and various
            stakeholder perspectives to provide comprehensive understanding."""
        )
    
    def _create_verification_agent(self) -> Agent:
        """Create specialized verification agent"""
        return Agent(
            model=self.openrouter_model,
            result_type=VerificationOutput,
            system_prompt="""You are a fact-checking specialist focused on verification and
            current status validation. Cross-reference information from multiple sources and
            provide confidence assessments for all claims."""
        )
    
    async def _synthesize_results(
        self, 
        user_query: str, 
        questions: GrokQuestionSet, 
        agent_results: Dict[str, Any]
    ) -> GrokSynthesisOutput:
        """Synthesize all agent results into comprehensive analysis"""
        
        # Prepare synthesis input
        synthesis_input = f"""
        Original Query: {user_query}
        
        Research Question: {questions.research_question}
        Research Results: {agent_results.get('research_agent', {}).get('data', 'No results')}
        
        Analysis Question: {questions.analysis_question}
        Analysis Results: {agent_results.get('analysis_agent', {}).get('data', 'No results')}
        
        Perspective Question: {questions.perspective_question}
        Perspective Results: {agent_results.get('perspective_agent', {}).get('data', 'No results')}
        
        Verification Question: {questions.verification_question}
        Verification Results: {agent_results.get('verification_agent', {}).get('data', 'No results')}
        
        Synthesize all findings into a comprehensive Grok heavy-style analysis.
        """
        
        result = await self.synthesis_agent.run(synthesis_input)
        return result.data
    
    async def _enhance_with_deep_reflection(
        self, 
        user_query: str, 
        initial_synthesis: GrokSynthesisOutput, 
        agent_results: Dict[str, Any]
    ) -> GrokSynthesisOutput:
        """Phase 5: Deep reflection and insights enhancement"""
        
        # Prepare reflection input with all context
        reflection_input = f"""
        ORIGINAL QUERY: {user_query}
        
        INITIAL SYNTHESIS RESULT:
        {initial_synthesis.comprehensive_analysis}
        
        KEY INSIGHTS FROM INITIAL SYNTHESIS:
        {chr(10).join(f'• {insight}' for insight in initial_synthesis.key_insights)}
        
        CONFIDENCE SCORE: {initial_synthesis.confidence_score:.1%}
        
        RAW AGENT RESULTS FOR DEEPER ANALYSIS:
        
        RESEARCH FINDINGS:
        {agent_results.get('research_agent', {}).get('data', 'No results')}
        
        ANALYSIS FINDINGS:
        {agent_results.get('analysis_agent', {}).get('data', 'No results')}
        
        PERSPECTIVE FINDINGS:
        {agent_results.get('perspective_agent', {}).get('data', 'No results')}
        
        VERIFICATION FINDINGS:
        {agent_results.get('verification_agent', {}).get('data', 'No results')}
        
        PHASE 5 MISSION:
        Now perform deep reflection on this analysis. Look beyond the surface.
        Find the patterns within patterns. Discover what makes this truly profound.
        Transform good analysis into extraordinary insight that would make Grok proud.
        """
        
        # Run reflection agent
        reflection_result = await self.reflection_agent.run(reflection_input)
        
        # Enhance the original synthesis with reflection insights
        enhanced_result = reflection_result.data
        
        # Update confidence score based on reflection depth
        if hasattr(enhanced_result, 'confidence_score'):
            enhanced_result.confidence_score = min(enhanced_result.confidence_score + 0.1, 1.0)
        
        return enhanced_result
