from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import json
import httpx
import asyncio

class MCPTool(BaseModel):
    """MCP tool definition"""
    name: str
    description: str
    parameters: Dict[str, Any]
    server_url: str
    method: str = "POST"
    headers: Dict[str, str] = {}

class MCPServer(BaseModel):
    """MCP server configuration"""
    name: str
    url: str
    description: str
    tools: List[MCPTool] = []
    auth_token: Optional[str] = None
    enabled: bool = True

class MCPToolsIntegration:
    """MCP server tools integration"""
    
    def __init__(self):
        self.servers: Dict[str, MCPServer] = {}
        self.client = httpx.AsyncClient(timeout=30.0)
        self._load_default_servers()
    
    def _load_default_servers(self):
        """Load default MCP servers"""
        # VS Code MCP server
        vscode_server = MCPServer(
            name="vscode",
            url="http://localhost:3000",
            description="VS Code MCP server for file operations",
            tools=[
                MCPTool(
                    name="read_file",
                    description="Read file contents",
                    parameters={
                        "path": {"type": "string", "description": "File path"}
                    },
                    server_url="http://localhost:3000/read_file"
                ),
                MCPTool(
                    name="write_file",
                    description="Write file contents",
                    parameters={
                        "path": {"type": "string", "description": "File path"},
                        "content": {"type": "string", "description": "File content"}
                    },
                    server_url="http://localhost:3000/write_file"
                ),
                MCPTool(
                    name="list_files",
                    description="List files in directory",
                    parameters={
                        "path": {"type": "string", "description": "Directory path"}
                    },
                    server_url="http://localhost:3000/list_files"
                )
            ]
        )
        self.servers["vscode"] = vscode_server
        
        # GitHub MCP server
        github_server = MCPServer(
            name="github",
            url="http://localhost:3001",
            description="GitHub MCP server for repository operations",
            tools=[
                MCPTool(
                    name="get_repo_info",
                    description="Get repository information",
                    parameters={
                        "owner": {"type": "string", "description": "Repository owner"},
                        "repo": {"type": "string", "description": "Repository name"}
                    },
                    server_url="http://localhost:3001/repo_info"
                ),
                MCPTool(
                    name="create_issue",
                    description="Create GitHub issue",
                    parameters={
                        "owner": {"type": "string", "description": "Repository owner"},
                        "repo": {"type": "string", "description": "Repository name"},
                        "title": {"type": "string", "description": "Issue title"},
                        "body": {"type": "string", "description": "Issue body"}
                    },
                    server_url="http://localhost:3001/create_issue"
                )
            ]
        )
        self.servers["github"] = github_server
    
    async def register_server(self, server: MCPServer):
        """Register a new MCP server"""
        self.servers[server.name] = server
        
        # Test connection
        try:
            await self.test_server_connection(server.name)
            print(f"Successfully registered MCP server: {server.name}")
        except Exception as e:
            print(f"Warning: Could not connect to MCP server {server.name}: {e}")
    
    async def test_server_connection(self, server_name: str) -> bool:
        """Test connection to MCP server"""
        if server_name not in self.servers:
            return False
        
        server = self.servers[server_name]
        
        try:
            response = await self.client.get(f"{server.url}/health")
            return response.status_code == 200
        except Exception:
            return False
    
    async def call_tool(self, server_name: str, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Call a tool on an MCP server"""
        if server_name not in self.servers:
            raise ValueError(f"Server {server_name} not found")
        
        server = self.servers[server_name]
        
        # Find the tool
        tool = None
        for t in server.tools:
            if t.name == tool_name:
                tool = t
                break
        
        if not tool:
            raise ValueError(f"Tool {tool_name} not found on server {server_name}")
        
        # Prepare headers
        headers = {"Content-Type": "application/json"}
        headers.update(tool.headers)
        
        if server.auth_token:
            headers["Authorization"] = f"Bearer {server.auth_token}"
        
        # Make the request
        try:
            response = await self.client.request(
                method=tool.method,
                url=tool.server_url,
                json=parameters,
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"MCP tool call failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            raise Exception(f"Error calling MCP tool: {str(e)}")
    
    async def list_available_tools(self, server_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all available tools"""
        tools = []
        
        servers = [self.servers[server_name]] if server_name else self.servers.values()
        
        for server in servers:
            for tool in server.tools:
                tools.append({
                    "server": server.name,
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters
                })
        
        return tools
    
    async def get_server_status(self) -> Dict[str, Any]:
        """Get status of all MCP servers"""
        status = {}
        
        for server_name, server in self.servers.items():
            is_connected = await self.test_server_connection(server_name)
            status[server_name] = {
                "url": server.url,
                "connected": is_connected,
                "tools_count": len(server.tools),
                "enabled": server.enabled
            }
        
        return status
    
    async def create_mcp_tool_wrapper(self, server_name: str, tool_name: str):
        """Create a wrapper function for an MCP tool"""
        async def tool_wrapper(**kwargs):
            return await self.call_tool(server_name, tool_name, kwargs)
        
        # Get tool info for documentation
        server = self.servers[server_name]
        tool = next((t for t in server.tools if t.name == tool_name), None)
        
        if tool:
            tool_wrapper.__doc__ = tool.description
            tool_wrapper.__name__ = f"{server_name}_{tool_name}"
        
        return tool_wrapper
    
    async def enable_server(self, server_name: str):
        """Enable an MCP server"""
        if server_name in self.servers:
            self.servers[server_name].enabled = True
    
    async def disable_server(self, server_name: str):
        """Disable an MCP server"""
        if server_name in self.servers:
            self.servers[server_name].enabled = False
    
    async def get_tool_schema(self, server_name: str, tool_name: str) -> Dict[str, Any]:
        """Get JSON schema for a tool"""
        if server_name not in self.servers:
            return {}
        
        server = self.servers[server_name]
        tool = next((t for t in server.tools if t.name == tool_name), None)
        
        if tool:
            return {
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    "type": "object",
                    "properties": tool.parameters,
                    "required": [k for k, v in tool.parameters.items() if v.get("required", False)]
                }
            }
        
        return {}
    
    async def sync_with_server(self, server_name: str):
        """Sync tool definitions with MCP server"""
        if server_name not in self.servers:
            return
        
        server = self.servers[server_name]
        
        try:
            # Get tool list from server
            response = await self.client.get(f"{server.url}/tools")
            if response.status_code == 200:
                tools_data = response.json()
                
                # Update tools list
                server.tools = []
                for tool_data in tools_data:
                    tool = MCPTool(
                        name=tool_data["name"],
                        description=tool_data["description"],
                        parameters=tool_data["parameters"],
                        server_url=f"{server.url}/{tool_data['name']}"
                    )
                    server.tools.append(tool)
                
                print(f"Synced {len(server.tools)} tools from {server_name}")
            
        except Exception as e:
            print(f"Error syncing with server {server_name}: {e}")
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

# Global MCP tools integration instance
mcp_tools = MCPToolsIntegration()
