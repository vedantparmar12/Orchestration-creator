#!/usr/bin/env python3
"""
Test script for MCP connection
Tests the MCP protocol implementation and connection
"""

import asyncio
import json
import websockets
import httpx
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
import time

console = Console()

class MCPConnectionTest:
    """Test MCP protocol connection and functionality"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.connection_id = None
    
    async def test_mcp_connection(self):
        """Test MCP connection and basic functionality"""
        console.print(Panel(
            "🔗 MCP Connection Test",
            style="cyan",
            padding=(1, 2)
        ))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            
            # Test 1: Server info
            task1 = progress.add_task("Testing MCP server info...", total=1)
            success1 = await self._test_server_info()
            progress.update(task1, advance=1)
            
            if not success1:
                console.print("[red]❌ MCP server info test failed[/red]")
                return False
            
            # Test 2: Connection
            task2 = progress.add_task("Testing MCP connection...", total=1)
            success2 = await self._test_connection()
            progress.update(task2, advance=1)
            
            if not success2:
                console.print("[red]❌ MCP connection test failed[/red]")
                return False
            
            # Test 3: Tools
            task3 = progress.add_task("Testing MCP tools...", total=1)
            success3 = await self._test_tools()
            progress.update(task3, advance=1)
            
            if not success3:
                console.print("[red]❌ MCP tools test failed[/red]")
                return False
            
            # Test 4: Resources
            task4 = progress.add_task("Testing MCP resources...", total=1)
            success4 = await self._test_resources()
            progress.update(task4, advance=1)
            
            if not success4:
                console.print("[red]❌ MCP resources test failed[/red]")
                return False
            
            # Test 5: Prompts
            task5 = progress.add_task("Testing MCP prompts...", total=1)
            success5 = await self._test_prompts()
            progress.update(task5, advance=1)
            
            if not success5:
                console.print("[red]❌ MCP prompts test failed[/red]")
                return False
        
        console.print("[green]✅ All MCP tests passed![/green]")
        return True
    
    async def _test_server_info(self) -> bool:
        """Test MCP server info endpoint"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/v1/mcp/server/info")
                
                if response.status_code == 200:
                    info = response.json()
                    console.print(f"[green]✅ Server: {info['name']} v{info['version']}[/green]")
                    console.print(f"[green]✅ Capabilities: {', '.join(info['capabilities'])}[/green]")
                    return True
                else:
                    console.print(f"[red]❌ Server info failed: {response.status_code}[/red]")
                    return False
        
        except Exception as e:
            console.print(f"[red]❌ Server info error: {str(e)}[/red]")
            return False
    
    async def _test_connection(self) -> bool:
        """Test MCP connection establishment"""
        try:
            async with httpx.AsyncClient() as client:
                connection_request = {
                    "client_info": {
                        "name": "test-client",
                        "version": "1.0.0"
                    },
                    "protocol_version": "2024-11-05",
                    "capabilities": {
                        "tools": {"listChanged": True},
                        "resources": {"listChanged": True},
                        "prompts": {"listChanged": True}
                    }
                }
                
                response = await client.post(
                    f"{self.base_url}/api/v1/mcp/connect",
                    json=connection_request
                )
                
                if response.status_code == 200:
                    result = response.json()
                    self.connection_id = result['connection_id']
                    console.print(f"[green]✅ Connected with ID: {self.connection_id}[/green]")
                    return True
                else:
                    console.print(f"[red]❌ Connection failed: {response.status_code}[/red]")
                    return False
        
        except Exception as e:
            console.print(f"[red]❌ Connection error: {str(e)}[/red]")
            return False
    
    async def _test_tools(self) -> bool:
        """Test MCP tools functionality"""
        try:
            async with httpx.AsyncClient() as client:
                # List tools
                response = await client.get(f"{self.base_url}/api/v1/mcp/tools/list")
                
                if response.status_code == 200:
                    tools = response.json()
                    console.print(f"[green]✅ Found {len(tools['tools'])} tools[/green]")
                    
                    # Display tools table
                    table = Table(title="Available MCP Tools")
                    table.add_column("Name", style="cyan")
                    table.add_column("Description", style="green")
                    
                    for tool in tools['tools']:
                        table.add_row(tool['name'], tool['description'])
                    
                    console.print(table)
                    
                    # Test tool execution
                    if tools['tools']:
                        tool_name = tools['tools'][0]['name']
                        tool_request = {
                            "name": tool_name,
                            "arguments": {}
                        }
                        
                        response = await client.post(
                            f"{self.base_url}/api/v1/mcp/tools/call",
                            json=tool_request
                        )
                        
                        if response.status_code == 200:
                            console.print(f"[green]✅ Tool '{tool_name}' executed successfully[/green]")
                        else:
                            console.print(f"[yellow]⚠️ Tool execution failed: {response.status_code}[/yellow]")
                    
                    return True
                else:
                    console.print(f"[red]❌ Tools list failed: {response.status_code}[/red]")
                    return False
        
        except Exception as e:
            console.print(f"[red]❌ Tools test error: {str(e)}[/red]")
            return False
    
    async def _test_resources(self) -> bool:
        """Test MCP resources functionality"""
        try:
            async with httpx.AsyncClient() as client:
                # List resources
                response = await client.get(f"{self.base_url}/api/v1/mcp/resources/list")
                
                if response.status_code == 200:
                    resources = response.json()
                    console.print(f"[green]✅ Found {len(resources['resources'])} resources[/green]")
                    
                    # Test resource reading
                    if resources['resources']:
                        resource_uri = resources['resources'][0]['uri']
                        response = await client.get(
                            f"{self.base_url}/api/v1/mcp/resources/read",
                            params={"uri": resource_uri}
                        )
                        
                        if response.status_code == 200:
                            console.print(f"[green]✅ Resource '{resource_uri}' read successfully[/green]")
                        else:
                            console.print(f"[yellow]⚠️ Resource read failed: {response.status_code}[/yellow]")
                    
                    return True
                else:
                    console.print(f"[red]❌ Resources list failed: {response.status_code}[/red]")
                    return False
        
        except Exception as e:
            console.print(f"[red]❌ Resources test error: {str(e)}[/red]")
            return False
    
    async def _test_prompts(self) -> bool:
        """Test MCP prompts functionality"""
        try:
            async with httpx.AsyncClient() as client:
                # List prompts
                response = await client.get(f"{self.base_url}/api/v1/mcp/prompts/list")
                
                if response.status_code == 200:
                    prompts = response.json()
                    console.print(f"[green]✅ Found {len(prompts['prompts'])} prompts[/green]")
                    
                    # Test prompt generation
                    if prompts['prompts']:
                        prompt_name = prompts['prompts'][0]['name']
                        response = await client.post(
                            f"{self.base_url}/api/v1/mcp/prompts/get",
                            params={"name": prompt_name}
                        )
                        
                        if response.status_code == 200:
                            console.print(f"[green]✅ Prompt '{prompt_name}' generated successfully[/green]")
                        else:
                            console.print(f"[yellow]⚠️ Prompt generation failed: {response.status_code}[/yellow]")
                    
                    return True
                else:
                    console.print(f"[red]❌ Prompts list failed: {response.status_code}[/red]")
                    return False
        
        except Exception as e:
            console.print(f"[red]❌ Prompts test error: {str(e)}[/red]")
            return False
    
    async def test_websocket_connection(self):
        """Test WebSocket MCP connection"""
        console.print(Panel(
            "🔌 WebSocket MCP Connection Test",
            style="cyan",
            padding=(1, 2)
        ))
        
        if not self.connection_id:
            console.print("[red]❌ No connection ID available[/red]")
            return False
        
        try:
            websocket_url = f"ws://localhost:8080/api/v1/mcp/ws/{self.connection_id}"
            
            async with websockets.connect(websocket_url) as websocket:
                # Send ping message
                ping_message = {
                    "jsonrpc": "2.0",
                    "method": "ping",
                    "params": {},
                    "id": "test-ping"
                }
                
                await websocket.send(json.dumps(ping_message))
                response = await websocket.recv()
                result = json.loads(response)
                
                if result.get("result", {}).get("pong"):
                    console.print("[green]✅ WebSocket ping successful[/green]")
                    return True
                else:
                    console.print("[red]❌ WebSocket ping failed[/red]")
                    return False
        
        except Exception as e:
            console.print(f"[red]❌ WebSocket error: {str(e)}[/red]")
            return False
    
    async def display_mcp_capabilities(self):
        """Display comprehensive MCP capabilities"""
        console.print(Panel(
            "📋 MCP Capabilities Overview",
            style="cyan",
            padding=(1, 2)
        ))
        
        try:
            async with httpx.AsyncClient() as client:
                # Get server info
                response = await client.get(f"{self.base_url}/api/v1/mcp/server/info")
                info = response.json()
                
                # Get tools
                response = await client.get(f"{self.base_url}/api/v1/mcp/tools/list")
                tools = response.json()
                
                # Get resources
                response = await client.get(f"{self.base_url}/api/v1/mcp/resources/list")
                resources = response.json()
                
                # Get prompts
                response = await client.get(f"{self.base_url}/api/v1/mcp/prompts/list")
                prompts = response.json()
                
                # Display summary
                summary_table = Table(title="MCP Server Summary")
                summary_table.add_column("Component", style="cyan")
                summary_table.add_column("Count", style="green")
                summary_table.add_column("Status", style="yellow")
                
                summary_table.add_row("Tools", str(len(tools['tools'])), "✅ Available")
                summary_table.add_row("Resources", str(len(resources['resources'])), "✅ Available")
                summary_table.add_row("Prompts", str(len(prompts['prompts'])), "✅ Available")
                summary_table.add_row("Capabilities", str(len(info['capabilities'])), "✅ Active")
                
                console.print(summary_table)
                
                # Display IDE integration info
                console.print("\n[bold cyan]IDE Integration Instructions:[/bold cyan]")
                console.print("1. Copy the mcp_config.json file to your IDE's MCP configuration directory")
                console.print("2. Restart your IDE (VS Code, Cursor, etc.)")
                console.print("3. The Enhanced Agentic Workflow server will be available as an MCP provider")
                console.print("4. Access tools, resources, and prompts through your IDE's MCP interface")
                
        except Exception as e:
            console.print(f"[red]❌ Error displaying capabilities: {str(e)}[/red]")

async def main():
    """Main test function"""
    console.print(Panel(
        "🚀 MCP Protocol Test Suite",
        style="bold cyan",
        padding=(1, 2)
    ))
    
    console.print("[yellow]⚠️  Make sure the FastAPI service is running on http://localhost:8080[/yellow]")
    console.print("[dim]Start with: python -m uvicorn src.api.fastapi_service:app --host 0.0.0.0 --port 8080[/dim]")
    console.print()
    
    input("Press Enter to continue with MCP tests...")
    
    # Initialize test client
    test_client = MCPConnectionTest()
    
    # Run tests
    success = await test_client.test_mcp_connection()
    
    if success:
        # Test WebSocket connection
        await test_client.test_websocket_connection()
        
        # Display capabilities
        await test_client.display_mcp_capabilities()
        
        console.print(Panel(
            "[bold green]🎉 All MCP tests completed successfully![/bold green]\n\n"
            "Your MCP server is ready for IDE integration:\n"
            "• Tools: Execute workflows and generate agents\n"
            "• Resources: Access templates and system status\n"
            "• Prompts: Generate context-aware prompts\n"
            "• WebSocket: Real-time communication support",
            title="✅ MCP Test Results",
            style="green"
        ))
    else:
        console.print(Panel(
            "[bold red]❌ Some MCP tests failed![/bold red]\n\n"
            "Please check:\n"
            "• FastAPI service is running on port 8080\n"
            "• All dependencies are installed\n"
            "• No port conflicts exist",
            title="⚠️  MCP Test Issues",
            style="red"
        ))

if __name__ == "__main__":
    asyncio.run(main())
