#!/usr/bin/env python3
"""
Test script for Phase 5 Grok Heavy Mode
Verifies that the deep reflection enhancement works properly
"""

import asyncio
import sys
import os
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.grok_heavy.orchestrator import GrokHeavyOrchestrator
from src.grok_heavy.progress_display import ProgressDisplay

# Load environment variables
load_dotenv()

console = Console()

def check_environment():
    """Check if required environment variables are set"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == 'your_openai_api_key_here':
        console.print(Panel(
            "[red]❌ OpenAI API key not found![/red]\n\n"
            "Please set your OpenAI API key in the .env file:\n"
            "OPENAI_API_KEY=your_actual_key_here",
            title="⚠️  Configuration Error",
            border_style="red"
        ))
        return False
    
    console.print(Panel(
        "[green]✅ OpenAI API key found![/green]\n"
        "Ready to test Phase 5 Grok Heavy Mode",
        title="🚀 Environment Check",
        border_style="green"
    ))
    return True

async def test_phase5_simple():
    """Test Phase 5 with a simple query"""
    console.print("\n[bold cyan]Testing Phase 5 with simple query...[/bold cyan]")
    
    orchestrator = GrokHeavyOrchestrator()
    progress_display = ProgressDisplay()
    
    test_query = "What is artificial intelligence?"
    
    try:
        result = await orchestrator.run_grok_heavy_analysis(
            test_query,
            progress_callback=progress_display.update_progress
        )
        
        # Display results
        progress_display.display_final_result(result)
        
        # Verify Phase 5 enhancements
        console.print("\n[bold green]✅ Phase 5 Test Completed Successfully![/bold green]")
        console.print(f"[dim]Query: {test_query}[/dim]")
        console.print(f"[dim]Analysis length: {len(result.comprehensive_analysis)} characters[/dim]")
        console.print(f"[dim]Key insights: {len(result.key_insights)} insights[/dim]")
        console.print(f"[dim]Confidence score: {result.confidence_score:.1%}[/dim]")
        
        return True
        
    except Exception as e:
        console.print(f"\n[red]❌ Phase 5 Test Failed: {str(e)}[/red]")
        return False

async def test_phase5_complex():
    """Test Phase 5 with a complex query"""
    console.print("\n[bold cyan]Testing Phase 5 with complex query...[/bold cyan]")
    
    orchestrator = GrokHeavyOrchestrator()
    progress_display = ProgressDisplay()
    
    test_query = "Analyze the impact of quantum computing on current encryption methods"
    
    try:
        result = await orchestrator.run_grok_heavy_analysis(
            test_query,
            progress_callback=progress_display.update_progress
        )
        
        # Display results
        progress_display.display_final_result(result)
        
        # Verify Phase 5 enhancements
        console.print("\n[bold green]✅ Phase 5 Complex Test Completed Successfully![/bold green]")
        console.print(f"[dim]Query: {test_query}[/dim]")
        console.print(f"[dim]Analysis length: {len(result.comprehensive_analysis)} characters[/dim]")
        console.print(f"[dim]Key insights: {len(result.key_insights)} insights[/dim]")
        console.print(f"[dim]Confidence score: {result.confidence_score:.1%}[/dim]")
        
        return True
        
    except Exception as e:
        console.print(f"\n[red]❌ Phase 5 Complex Test Failed: {str(e)}[/red]")
        return False

def show_phase5_info():
    """Show information about Phase 5 features"""
    info_text = """
[bold cyan]🧠 Phase 5: Deep Reflection & Insights Enhancement[/bold cyan]

[bold yellow]What Phase 5 Does:[/bold yellow]
• Deep meta-analysis of initial synthesis
• Finds hidden connections and patterns
• Proposes novel interpretations
• Adds philosophical depth and broader implications
• Crystallizes insights into profound takeaways

[bold yellow]Enhanced Workflow:[/bold yellow]
1. 🎯 Generate Research Questions
2. 🔀 Parallel Agent Execution
3. 🔄 Intelligent Synthesis
4. 🧠 Phase 5: Deep Reflection ← [bold green]NEW![/bold green]
5. ✅ Analysis Complete

[bold yellow]Key Features:[/bold yellow]
• Specialized reflection agent
• Meta-analysis capabilities
• Pattern recognition
• Philosophical enhancement
• Confidence score boosting
    """
    
    console.print(Panel(
        info_text,
        title="📋 Phase 5 Information",
        border_style="blue",
        padding=(1, 2)
    ))

async def main():
    """Main test function"""
    console.print(Panel(
        Text("🚀 Phase 5 Grok Heavy Mode Test Suite", style="bold white"),
        border_style="cyan",
        padding=(1, 2)
    ))
    
    # Show Phase 5 information
    show_phase5_info()
    
    # Check environment
    if not check_environment():
        return
    
    # Ask user what to test
    console.print("\n[bold cyan]Select test mode:[/bold cyan]")
    console.print("1. Simple test (recommended)")
    console.print("2. Complex test")
    console.print("3. Both tests")
    console.print("4. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            success = await test_phase5_simple()
            break
        elif choice == '2':
            success = await test_phase5_complex()
            break
        elif choice == '3':
            success1 = await test_phase5_simple()
            if success1:
                success2 = await test_phase5_complex()
                success = success1 and success2
            else:
                success = False
            break
        elif choice == '4':
            console.print("[yellow]Exiting test suite.[/yellow]")
            return
        else:
            console.print("[red]Invalid choice. Please enter 1, 2, 3, or 4.[/red]")
    
    # Final summary
    if success:
        console.print(Panel(
            "[bold green]🎉 All Phase 5 tests completed successfully![/bold green]\n\n"
            "Your Grok Heavy Mode system is ready with:\n"
            "• Deep reflection capabilities\n"
            "• Enhanced insight generation\n"
            "• Meta-analysis features\n"
            "• Phase 5 completion",
            title="✅ Test Suite Complete",
            border_style="green"
        ))
    else:
        console.print(Panel(
            "[bold red]❌ Some tests failed![/bold red]\n\n"
            "Please check:\n"
            "• Your OpenAI API key\n"
            "• Internet connection\n"
            "• Dependencies installation",
            title="⚠️  Test Issues",
            border_style="red"
        ))

if __name__ == "__main__":
    asyncio.run(main())
