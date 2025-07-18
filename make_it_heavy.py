import asyncio
import sys
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text
from src.grok_heavy.orchestrator import GrokHeavyOrchestrator
from src.grok_heavy.progress_display import ProgressDisplay
import logfire
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Logfire for monitoring
logfire.configure()

console = Console()

def display_banner():
    """Display Grok heavy mode banner"""
    banner = Text("🚀 GROK HEAVY MODE", style="bold cyan")
    banner.append("\nDeep Multi-Agent Analysis System", style="dim")
    
    panel = Panel(
        banner,
        border_style="cyan",
        padding=(1, 2)
    )
    console.print(panel)
    console.print()

def display_example():
    """Display example usage"""
    example_text = """
[bold yellow]Example Query:[/bold yellow] "Who is Pietro Schirano?"

[bold green]Generated Research Questions:[/bold green]
• Agent 1: Research Pietro Schirano's professional background and career history
• Agent 2: Analyze Pietro Schirano's achievements and contributions to technology  
• Agent 3: Find alternative perspectives on Pietro Schirano's work and impact
• Agent 4: Verify and cross-check information about Pietro Schirano's current role

[bold blue]Result:[/bold blue] Comprehensive Grok heavy-style analysis combining all perspectives
    """
    console.print(Panel(example_text, title="How It Works", border_style="green"))
    console.print()

async def main():
    """Main Grok heavy mode interface"""
    display_banner()
    
    if len(sys.argv) > 1:
        # Query provided as command line argument
        user_query = " ".join(sys.argv[1:])
    else:
        # Interactive mode
        display_example()
        user_query = Prompt.ask("[bold cyan]Enter your query for deep analysis")
    
    if not user_query.strip():
        console.print("[red]No query provided. Exiting.[/red]")
        return
    
    console.print(f"\n[bold yellow]🎯 Analyzing:[/bold yellow] {user_query}")
    console.print()
    
    # Initialize Grok heavy orchestrator
    orchestrator = GrokHeavyOrchestrator()
    progress_display = ProgressDisplay()
    
    try:
        # Run Grok heavy analysis with live progress
        result = await orchestrator.run_grok_heavy_analysis(
            user_query, 
            progress_callback=progress_display.update_progress
        )
        
        # Display final result
        progress_display.display_final_result(result)
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Analysis interrupted by user.[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error during analysis: {str(e)}[/red]")
        raise

if __name__ == "__main__":
    asyncio.run(main())
