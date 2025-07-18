#!/usr/bin/env python3
"""
Command-line interface for Enhanced Agentic Workflow Architecture
"""

import asyncio
import sys
import os
import argparse
from typing import Optional, List
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.grok_heavy.orchestrator import GrokHeavyOrchestrator
from src.grok_heavy.progress_display import ProgressDisplay

# Load environment variables
load_dotenv()

console = Console()

def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser"""
    parser = argparse.ArgumentParser(
        description="Enhanced Agentic Workflow Architecture CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s query "What is artificial intelligence?"
  %(prog)s grok "Analyze the impact of AI on software development"
  %(prog)s config --show
  %(prog)s config --set OPENAI_API_KEY=your_key_here
  %(prog)s server --start
  %(prog)s agent --create --template coding_agent
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Query command
    query_parser = subparsers.add_parser('query', help='Run a simple query')
    query_parser.add_argument('text', help='Query text')
    query_parser.add_argument('--model', default='openai:gpt-4o', help='Model to use')
    query_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    # Grok heavy command
    grok_parser = subparsers.add_parser('grok', help='Run Grok heavy analysis')
    grok_parser.add_argument('text', help='Query text for deep analysis')
    grok_parser.add_argument('--agents', type=int, default=4, help='Number of agents to use')
    grok_parser.add_argument('--timeout', type=int, default=300, help='Timeout in seconds')
    
    # Configuration command
    config_parser = subparsers.add_parser('config', help='Manage configuration')
    config_parser.add_argument('--show', action='store_true', help='Show current configuration')
    config_parser.add_argument('--set', metavar='KEY=VALUE', action='append', help='Set configuration value')
    config_parser.add_argument('--validate', action='store_true', help='Validate configuration')
    config_parser.add_argument('--env-check', action='store_true', help='Check environment variables')
    
    # Server command
    server_parser = subparsers.add_parser('server', help='Manage MCP server')
    server_parser.add_argument('--start', action='store_true', help='Start MCP server')
    server_parser.add_argument('--stop', action='store_true', help='Stop MCP server')
    server_parser.add_argument('--status', action='store_true', help='Show server status')
    server_parser.add_argument('--port', type=int, default=8080, help='Server port')
    
    # Agent command
    agent_parser = subparsers.add_parser('agent', help='Agent management')
    agent_parser.add_argument('--create', action='store_true', help='Create new agent')
    agent_parser.add_argument('--template', help='Agent template to use')
    agent_parser.add_argument('--list', action='store_true', help='List available agents')
    agent_parser.add_argument('--tools', nargs='*', help='Tools to include')
    
    # Tools command
    tools_parser = subparsers.add_parser('tools', help='Tool management')
    tools_parser.add_argument('--list', action='store_true', help='List available tools')
    tools_parser.add_argument('--search', help='Search tools')
    tools_parser.add_argument('--install', help='Install tool')
    tools_parser.add_argument('--category', help='Filter by category')
    
    # Database command
    db_parser = subparsers.add_parser('database', help='Database management')
    db_parser.add_argument('--setup', action='store_true', help='Setup databases')
    db_parser.add_argument('--test', action='store_true', help='Test database connections')
    db_parser.add_argument('--migrate', action='store_true', help='Run database migrations')
    
    return parser

async def handle_query(args):
    """Handle simple query command"""
    console.print(f"[bold cyan]Running query:[/bold cyan] {args.text}")
    
    # TODO: Implement single agent query
    console.print("[yellow]Single agent query not implemented yet[/yellow]")
    console.print("Use 'grok' command for multi-agent analysis")

async def handle_grok(args):
    """Handle Grok heavy analysis command"""
    console.print(f"[bold cyan]🚀 Starting Grok heavy analysis:[/bold cyan] {args.text}")
    console.print()
    
    # Check environment
    if not os.getenv('OPENAI_API_KEY'):
        console.print("[red]❌ OPENAI_API_KEY not set. Please configure your environment.[/red]")
        return
    
    # Initialize orchestrator
    orchestrator = GrokHeavyOrchestrator(max_workers=args.agents)
    progress_display = ProgressDisplay()
    
    try:
        # Run analysis
        result = await orchestrator.run_grok_heavy_analysis(
            args.text,
            progress_callback=progress_display.update_progress
        )
        
        # Display results
        progress_display.display_final_result(result)
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Analysis interrupted by user.[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error during analysis: {str(e)}[/red]")
        if args.verbose:
            console.print_exception()

def handle_config(args):
    """Handle configuration command"""
    if args.show:
        show_config()
    elif args.set:
        set_config(args.set)
    elif args.validate:
        validate_config()
    elif args.env_check:
        check_environment()
    else:
        console.print("[yellow]Use --show, --set, --validate, or --env-check[/yellow]")

def show_config():
    """Show current configuration"""
    console.print("[bold cyan]Current Configuration:[/bold cyan]")
    
    # Environment variables
    env_vars = [
        'OPENAI_API_KEY',
        'ANTHROPIC_API_KEY',
        'GOOGLE_API_KEY',
        'SUPABASE_URL',
        'SUPABASE_KEY',
        'REDIS_URL',
        'LOGFIRE_TOKEN'
    ]
    
    table = Table(title="Environment Variables")
    table.add_column("Variable", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Value", style="dim")
    
    for var in env_vars:
        value = os.getenv(var, "")
        if value:
            status = "✅ Set"
            display_value = f"{value[:10]}..." if len(value) > 10 else value
        else:
            status = "❌ Not set"
            display_value = ""
        
        table.add_row(var, status, display_value)
    
    console.print(table)

def set_config(config_items: List[str]):
    """Set configuration values"""
    for item in config_items:
        if '=' not in item:
            console.print(f"[red]Invalid format: {item}. Use KEY=VALUE[/red]")
            continue
        
        key, value = item.split('=', 1)
        
        # Set environment variable
        os.environ[key] = value
        
        # Save to .env file
        from dotenv import set_key
        set_key('.env', key, value)
        
        console.print(f"[green]✅ Set {key}[/green]")

def validate_config():
    """Validate configuration"""
    console.print("[bold cyan]Validating Configuration:[/bold cyan]")
    
    errors = []
    warnings = []
    
    # Check required environment variables
    required_vars = ['OPENAI_API_KEY']
    for var in required_vars:
        if not os.getenv(var):
            errors.append(f"Missing required environment variable: {var}")
    
    # Check optional but recommended variables
    optional_vars = ['SUPABASE_URL', 'SUPABASE_KEY', 'LOGFIRE_TOKEN']
    for var in optional_vars:
        if not os.getenv(var):
            warnings.append(f"Optional environment variable not set: {var}")
    
    # Display results
    if errors:
        console.print("\n[red]❌ Errors found:[/red]")
        for error in errors:
            console.print(f"  • {error}")
    
    if warnings:
        console.print("\n[yellow]⚠️  Warnings:[/yellow]")
        for warning in warnings:
            console.print(f"  • {warning}")
    
    if not errors and not warnings:
        console.print("\n[green]✅ Configuration is valid![/green]")

def check_environment():
    """Check environment setup"""
    console.print("[bold cyan]Environment Check:[/bold cyan]")
    
    # Check Python version
    python_version = sys.version_info
    console.print(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check required packages
    required_packages = [
        'pydantic_ai',
        'openai',
        'anthropic',
        'rich',
        'streamlit',
        'logfire'
    ]
    
    console.print("\n[bold]Package Status:[/bold]")
    for package in required_packages:
        try:
            __import__(package)
            console.print(f"  ✅ {package}")
        except ImportError:
            console.print(f"  ❌ {package}")
    
    # Check file system
    console.print("\n[bold]File System:[/bold]")
    required_dirs = ['src', 'config']
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            console.print(f"  ✅ {dir_name}/ directory")
        else:
            console.print(f"  ❌ {dir_name}/ directory")

def handle_server(args):
    """Handle server command"""
    if args.start:
        console.print("[bold cyan]Starting MCP server...[/bold cyan]")
        console.print("[yellow]MCP server functionality not implemented yet[/yellow]")
    elif args.stop:
        console.print("[bold cyan]Stopping MCP server...[/bold cyan]")
        console.print("[yellow]MCP server functionality not implemented yet[/yellow]")
    elif args.status:
        console.print("[bold cyan]Server Status:[/bold cyan]")
        console.print("[yellow]MCP server functionality not implemented yet[/yellow]")
    else:
        console.print("[yellow]Use --start, --stop, or --status[/yellow]")

def handle_agent(args):
    """Handle agent command"""
    if args.create:
        console.print("[bold cyan]Creating new agent...[/bold cyan]")
        console.print("[yellow]Agent creation functionality not implemented yet[/yellow]")
    elif args.list:
        console.print("[bold cyan]Available Agent Templates:[/bold cyan]")
        templates = [
            "coding_agent",
            "research_agent", 
            "analysis_agent",
            "testing_agent",
            "devops_agent"
        ]
        for template in templates:
            console.print(f"  • {template}")
    else:
        console.print("[yellow]Use --create or --list[/yellow]")

def handle_tools(args):
    """Handle tools command"""
    if args.list:
        console.print("[bold cyan]Available Tools:[/bold cyan]")
        tools = [
            "web_scraper",
            "file_processor",
            "api_client",
            "data_analyzer",
            "code_formatter"
        ]
        for tool in tools:
            console.print(f"  • {tool}")
    elif args.search:
        console.print(f"[bold cyan]Searching tools for: {args.search}[/bold cyan]")
        console.print("[yellow]Tool search functionality not implemented yet[/yellow]")
    else:
        console.print("[yellow]Use --list or --search[/yellow]")

def handle_database(args):
    """Handle database command"""
    if args.setup:
        console.print("[bold cyan]Setting up databases...[/bold cyan]")
        console.print("[yellow]Database setup functionality not implemented yet[/yellow]")
    elif args.test:
        console.print("[bold cyan]Testing database connections...[/bold cyan]")
        console.print("[yellow]Database test functionality not implemented yet[/yellow]")
    elif args.migrate:
        console.print("[bold cyan]Running database migrations...[/bold cyan]")
        console.print("[yellow]Database migration functionality not implemented yet[/yellow]")
    else:
        console.print("[yellow]Use --setup, --test, or --migrate[/yellow]")

def display_help():
    """Display help information"""
    help_text = """
[bold cyan]Enhanced Agentic Workflow Architecture CLI[/bold cyan]

[bold yellow]Available Commands:[/bold yellow]
  query      - Run a simple query
  grok       - Run Grok heavy analysis (multi-agent)
  config     - Manage configuration
  server     - Manage MCP server
  agent      - Agent management
  tools      - Tool management
  database   - Database management

[bold yellow]Quick Start:[/bold yellow]
  1. Set up environment: python -m src.cli.main config --env-check
  2. Configure API key: python -m src.cli.main config --set OPENAI_API_KEY=your_key
  3. Run analysis: python -m src.cli.main grok "Your query here"

[bold yellow]Examples:[/bold yellow]
  python -m src.cli.main grok "What is artificial intelligence?"
  python -m src.cli.main config --show
  python -m src.cli.main tools --list
  python -m src.cli.main agent --create --template coding_agent
    """
    
    console.print(Panel(help_text, title="Help", border_style="cyan"))

async def main():
    """Main CLI entry point"""
    parser = create_parser()
    
    if len(sys.argv) == 1:
        display_help()
        return
    
    args = parser.parse_args()
    
    try:
        if args.command == 'query':
            await handle_query(args)
        elif args.command == 'grok':
            await handle_grok(args)
        elif args.command == 'config':
            handle_config(args)
        elif args.command == 'server':
            handle_server(args)
        elif args.command == 'agent':
            handle_agent(args)
        elif args.command == 'tools':
            handle_tools(args)
        elif args.command == 'database':
            handle_database(args)
        else:
            parser.print_help()
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation interrupted by user.[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {str(e)}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
