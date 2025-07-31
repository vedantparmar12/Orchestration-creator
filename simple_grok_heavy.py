import asyncio
import sys
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from src.utils.pydantic_ai_config import create_openrouter_model
from pydantic_ai import Agent
import os
from dotenv import load_dotenv

load_dotenv()

console = Console()

class SimpleGrokHeavyOrchestrator:
    """Simple Grok Heavy Mode without complex structured output"""
    
    def __init__(self):
        self.model = create_openrouter_model()
        
        # Create 4 different agents with different personalities
        self.agents = {
            'research_agent': Agent(
                model=self.model,
                system_prompt="""You are a research specialist. Focus on gathering comprehensive 
                factual information, background details, and foundational knowledge. Be thorough 
                and well-sourced in your research approach."""
            ),
            'analysis_agent': Agent(
                model=self.model,
                system_prompt="""You are an analysis expert. Focus on evaluating achievements, 
                contributions, impact, and significance. Provide deep analytical insights with 
                supporting evidence and metrics where available."""
            ),
            'perspective_agent': Agent(
                model=self.model,
                system_prompt="""You are a perspective analyst. Focus on alternative viewpoints, 
                broader context, potential criticisms, and different stakeholder perspectives. 
                Explore multiple angles and nuanced interpretations."""
            ),
            'verification_agent': Agent(
                model=self.model,
                system_prompt="""You are a fact-checking specialist. Focus on verifying claims, 
                checking current status, validating information accuracy, and providing confidence 
                assessments for different pieces of information."""
            )
        }
    
    async def run_simple_grok_analysis(self, user_query: str) -> dict:
        """Run simplified Grok heavy analysis"""
        
        # Step 1: Generate questions for each agent
        questions = {
            'research_agent': f"Research the background and foundational information about: {user_query}",
            'analysis_agent': f"Analyze the achievements, contributions, and impact of: {user_query}",
            'perspective_agent': f"Explore alternative perspectives and broader context about: {user_query}",
            'verification_agent': f"Verify key facts and current status information about: {user_query}"
        }
        
        # Step 2: Run agents in parallel
        console.print("\n[bold yellow]🔄 Running 4 specialized agents in parallel...[/bold yellow]")
        
        tasks = []
        for agent_name, question in questions.items():
            tasks.append(self._run_agent(agent_name, question))
        
        # Execute all agents concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Step 3: Process results
        agent_results = {}
        agent_names = list(questions.keys())
        
        for i, result in enumerate(results):
            agent_name = agent_names[i]
            if isinstance(result, Exception):
                agent_results[agent_name] = f"Error: {str(result)}"
            else:
                agent_results[agent_name] = result
        
        # Step 4: Synthesize results
        console.print("[bold yellow]🔄 Synthesizing comprehensive analysis...[/bold yellow]")
        
        synthesis_prompt = f"""
        Based on the following specialized agent outputs about '{user_query}', create a comprehensive 
        Grok heavy-style analysis that synthesizes all perspectives:

        RESEARCH FINDINGS:
        {agent_results.get('research_agent', 'No research data')}

        ANALYSIS INSIGHTS:
        {agent_results.get('analysis_agent', 'No analysis data')}

        ALTERNATIVE PERSPECTIVES:
        {agent_results.get('perspective_agent', 'No perspective data')}

        VERIFICATION RESULTS:
        {agent_results.get('verification_agent', 'No verification data')}

        Create a comprehensive synthesis that combines all these perspectives into a coherent,
        insightful analysis worthy of the 'Grok heavy' standard.
        """
        
        synthesis_agent = Agent(
            model=self.model,
            system_prompt="""You are a synthesis expert who creates comprehensive Grok heavy-style 
            analyses. Combine multiple perspectives into coherent, insightful narratives that 
            provide deep understanding and nuanced insights."""
        )
        
        final_result = await synthesis_agent.run(synthesis_prompt)
        
        return {
            'user_query': user_query,
            'agent_results': agent_results,
            'final_synthesis': final_result.data
        }
    
    async def _run_agent(self, agent_name: str, question: str) -> str:
        """Run individual agent"""
        try:
            result = await self.agents[agent_name].run(question)
            return result.data
        except Exception as e:
            return f"Error: {str(e)}"

def display_banner():
    """Display Grok heavy mode banner"""
    banner = Text("🚀 SIMPLE GROK HEAVY MODE", style="bold cyan")
    banner.append("\\nDeep Multi-Agent Analysis System", style="dim")
    
    panel = Panel(
        banner,
        border_style="cyan",
        padding=(1, 2)
    )
    console.print(panel)
    console.print()

def display_results(results: dict):
    """Display comprehensive results"""
    console.print("\n[bold green]📊 COMPREHENSIVE ANALYSIS RESULTS[/bold green]")
    console.print("=" * 60)
    
    # Show individual agent results
    agent_names = {
        'research_agent': '🔍 Research Agent',
        'analysis_agent': '📊 Analysis Agent', 
        'perspective_agent': '👁️ Perspective Agent',
        'verification_agent': '✅ Verification Agent'
    }
    
    for agent_key, agent_name in agent_names.items():
        console.print(f"\n[bold cyan]{agent_name}:[/bold cyan]")
        result = results['agent_results'].get(agent_key, 'No data')
        console.print(Panel(result, border_style="blue", padding=(1, 2)))
    
    # Show final synthesis
    console.print("\n[bold yellow]🎯 FINAL COMPREHENSIVE SYNTHESIS:[/bold yellow]")
    console.print(Panel(
        results['final_synthesis'],
        title="Grok Heavy Analysis",
        border_style="yellow",
        padding=(1, 2)
    ))

async def main():
    """Main function"""
    display_banner()
    
    if len(sys.argv) > 1:
        # Query provided as command line argument
        user_query = " ".join(sys.argv[1:])
    else:
        # Interactive mode
        console.print("[bold cyan]Simple Grok Heavy Mode[/bold cyan] - Works with any OpenRouter model")
        console.print("Example: 'Who is Elon Musk?' or 'What is quantum computing?'")
        console.print()
        user_query = Prompt.ask("[bold cyan]Enter your query for deep analysis")
    
    if not user_query.strip():
        console.print("[red]No query provided. Exiting.[/red]")
        return
    
    console.print(f"\\n[bold yellow]🎯 Analyzing:[/bold yellow] {user_query}")
    
    # Initialize orchestrator
    orchestrator = SimpleGrokHeavyOrchestrator()
    
    try:
        # Run analysis
        results = await orchestrator.run_simple_grok_analysis(user_query)
        
        # Display results
        display_results(results)
        
    except KeyboardInterrupt:
        console.print("\\n[yellow]Analysis interrupted by user.[/yellow]")
    except Exception as e:
        console.print(f"\\n[red]Error during analysis: {str(e)}[/red]")
        raise

if __name__ == "__main__":
    asyncio.run(main())
