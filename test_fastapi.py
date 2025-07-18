#!/usr/bin/env python3
"""
Test script for FastAPI service
Tests the basic functionality of the Enhanced Agentic Workflow API
"""

import asyncio
import sys
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import httpx

# Load environment variables
load_dotenv()

console = Console()

def display_banner():
    """Display test banner"""
    banner = "🚀 FastAPI Service Test Suite"
    
    panel = Panel(
        banner,
        border_style="cyan",
        padding=(1, 2)
    )
    console.print(panel)
    console.print()

async def test_health_check():
    """Test health check endpoint"""
    console.print("[bold cyan]Testing Health Check...[/bold cyan]")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8080/health")
            
            if response.status_code == 200:
                data = response.json()
                console.print("[green]✅ Health check passed[/green]")
                console.print(f"System Health: {data['system_health']}")
                console.print(f"Version: {data['version']}")
                console.print(f"Uptime: {data['uptime']}")
                return True
            else:
                console.print(f"[red]❌ Health check failed: {response.status_code}[/red]")
                return False
                
    except Exception as e:
        console.print(f"[red]❌ Health check error: {str(e)}[/red]")
        return False

async def test_agent_endpoints():
    """Test agent management endpoints"""
    console.print("\n[bold cyan]Testing Agent Endpoints...[/bold cyan]")
    
    try:
        async with httpx.AsyncClient() as client:
            # Test list templates
            response = await client.get("http://localhost:8080/api/v1/agents/templates")
            if response.status_code == 200:
                templates = response.json()
                console.print(f"[green]✅ Found {len(templates)} agent templates[/green]")
            else:
                console.print(f"[red]❌ Templates endpoint failed: {response.status_code}[/red]")
                return False
            
            # Test list tools
            response = await client.get("http://localhost:8080/api/v1/agents/tools")
            if response.status_code == 200:
                tools = response.json()
                console.print(f"[green]✅ Found {len(tools)} available tools[/green]")
            else:
                console.print(f"[red]❌ Tools endpoint failed: {response.status_code}[/red]")
                return False
            
            # Test agent stats
            response = await client.get("http://localhost:8080/api/v1/agents/stats")
            if response.status_code == 200:
                stats = response.json()
                console.print(f"[green]✅ Agent stats retrieved[/green]")
                console.print(f"Active agents: {stats['active_agents']}")
                console.print(f"Total templates: {stats['total_templates']}")
                console.print(f"Total tools: {stats['total_tools']}")
            else:
                console.print(f"[red]❌ Stats endpoint failed: {response.status_code}[/red]")
                return False
            
            return True
            
    except Exception as e:
        console.print(f"[red]❌ Agent endpoints error: {str(e)}[/red]")
        return False

async def test_workflow_endpoints():
    """Test workflow management endpoints"""
    console.print("\n[bold cyan]Testing Workflow Endpoints...[/bold cyan]")
    
    try:
        async with httpx.AsyncClient() as client:
            # Test list workflow templates
            response = await client.get("http://localhost:8080/api/v1/workflows/templates")
            if response.status_code == 200:
                templates = response.json()
                console.print(f"[green]✅ Found {len(templates)} workflow templates[/green]")
                
                # Display templates
                table = Table(title="Workflow Templates")
                table.add_column("ID", style="cyan")
                table.add_column("Name", style="magenta")
                table.add_column("Description", style="green")
                table.add_column("Duration", style="yellow")
                
                for template in templates:
                    table.add_row(
                        template['id'],
                        template['name'],
                        template['description'][:50] + "..." if len(template['description']) > 50 else template['description'],
                        f"{template['estimated_duration']}s"
                    )
                
                console.print(table)
            else:
                console.print(f"[red]❌ Workflow templates failed: {response.status_code}[/red]")
                return False
            
            # Test workflow metrics
            response = await client.get("http://localhost:8080/api/v1/workflows/metrics")
            if response.status_code == 200:
                metrics = response.json()
                console.print(f"[green]✅ Workflow metrics retrieved[/green]")
                console.print(f"Total executions: {metrics['total_executions']}")
                console.print(f"Success rate: {metrics['success_rate']:.1%}")
            else:
                console.print(f"[red]❌ Metrics endpoint failed: {response.status_code}[/red]")
                return False
            
            return True
            
    except Exception as e:
        console.print(f"[red]❌ Workflow endpoints error: {str(e)}[/red]")
        return False

async def test_mcp_endpoints():
    """Test MCP protocol endpoints"""
    console.print("\n[bold cyan]Testing MCP Endpoints...[/bold cyan]")
    
    try:
        async with httpx.AsyncClient() as client:
            # Test MCP server info
            response = await client.get("http://localhost:8080/api/v1/mcp/server/info")
            if response.status_code == 200:
                info = response.json()
                console.print(f"[green]✅ MCP server info retrieved[/green]")
                console.print(f"Server: {info['name']} v{info['version']}")
                console.print(f"Capabilities: {', '.join(info['capabilities'])}")
                console.print(f"Tools: {len(info['tools'])}")
                console.print(f"Resources: {len(info['resources'])}")
            else:
                console.print(f"[red]❌ MCP server info failed: {response.status_code}[/red]")
                return False
            
            # Test MCP connections
            response = await client.get("http://localhost:8080/api/v1/mcp/connections")
            if response.status_code == 200:
                connections = response.json()
                console.print(f"[green]✅ MCP connections retrieved[/green]")
                console.print(f"Active connections: {connections['active_connections']}")
            else:
                console.print(f"[red]❌ MCP connections failed: {response.status_code}[/red]")
                return False
            
            return True
            
    except Exception as e:
        console.print(f"[red]❌ MCP endpoints error: {str(e)}[/red]")
        return False

async def test_agent_generation():
    """Test agent generation functionality"""
    console.print("\n[bold cyan]Testing Agent Generation...[/bold cyan]")
    
    try:
        async with httpx.AsyncClient() as client:
            # Test agent generation
            agent_request = {
                "agent_type": "test_agent",
                "requirements": "Create a simple test agent for API testing",
                "tools": ["basic_tool"],
                "configuration": {"test_mode": True}
            }
            
            response = await client.post(
                "http://localhost:8080/api/v1/generate-agent",
                json=agent_request
            )
            
            if response.status_code == 200:
                result = response.json()
                agent_id = result['agent_id']
                console.print(f"[green]✅ Agent generation started[/green]")
                console.print(f"Agent ID: {agent_id}")
                console.print(f"Status: {result['status']}")
                
                # Check status after a moment
                await asyncio.sleep(2)
                status_response = await client.get(f"http://localhost:8080/api/v1/agents/{agent_id}/status")
                if status_response.status_code == 200:
                    status = status_response.json()
                    console.print(f"[green]✅ Agent status retrieved[/green]")
                    console.print(f"Current status: {status['status']}")
                else:
                    console.print(f"[yellow]⚠️ Status check failed: {status_response.status_code}[/yellow]")
                
                return True
            else:
                console.print(f"[red]❌ Agent generation failed: {response.status_code}[/red]")
                console.print(f"Response: {response.text}")
                return False
            
    except Exception as e:
        console.print(f"[red]❌ Agent generation error: {str(e)}[/red]")
        return False

async def run_all_tests():
    """Run all tests"""
    display_banner()
    
    console.print("[bold yellow]Starting FastAPI Service Tests...[/bold yellow]")
    console.print("[dim]Make sure the FastAPI service is running on http://localhost:8080[/dim]")
    console.print()
    
    tests = [
        ("Health Check", test_health_check),
        ("Agent Endpoints", test_agent_endpoints),
        ("Workflow Endpoints", test_workflow_endpoints),
        ("MCP Endpoints", test_mcp_endpoints),
        ("Agent Generation", test_agent_generation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        console.print(f"\n[bold blue]Running {test_name}...[/bold blue]")
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            console.print(f"[red]❌ {test_name} failed with exception: {str(e)}[/red]")
            results.append((test_name, False))
    
    # Display summary
    console.print("\n" + "="*50)
    console.print("[bold cyan]Test Results Summary[/bold cyan]")
    console.print("="*50)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        if result:
            console.print(f"[green]✅ {test_name}[/green]")
            passed += 1
        else:
            console.print(f"[red]❌ {test_name}[/red]")
            failed += 1
    
    console.print(f"\n[bold]Total: {len(results)} tests[/bold]")
    console.print(f"[green]Passed: {passed}[/green]")
    console.print(f"[red]Failed: {failed}[/red]")
    
    if failed == 0:
        console.print("\n[bold green]🎉 All tests passed![/bold green]")
    else:
        console.print(f"\n[bold red]❌ {failed} test(s) failed[/bold red]")
    
    return failed == 0

if __name__ == "__main__":
    # Check if service is running
    console.print("[yellow]⚠️  Make sure to start the FastAPI service first:[/yellow]")
    console.print("[dim]python -m uvicorn src.api.fastapi_service:app --host 0.0.0.0 --port 8080[/dim]")
    console.print()
    
    input("Press Enter to continue with tests...")
    
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
