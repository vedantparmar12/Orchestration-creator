from typing import Dict, Any, Optional, List, Callable
import json
import uuid
import asyncio
from datetime import datetime
from fastapi import HTTPException
import logfire
from enum import Enum

class MCPCapability(Enum):
    """MCP server capabilities"""
    TOOLS = "tools"
    RESOURCES = "resources"
    PROMPTS = "prompts"
    LOGGING = "logging"
    PROGRESS = "progress"
    SAMPLING = "sampling"

class MCPErrorCode(Enum):
    """Standard MCP error codes"""
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    SERVER_ERROR = -32000

class MCPMessage:
    """MCP message descriptor"""
    def __init__(self, jsonrpc: str, method: str, params: Optional[Dict[str, Any]] = None, id: Optional[str] = None):
        self.jsonrpc = jsonrpc
        self.method = method
        self.params = params or {}
        self.id = id or str(uuid.uuid4())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "jsonrpc": self.jsonrpc,
            "method": self.method,
            "params": self.params,
            "id": self.id
        }

class MCPTool:
    """MCP tool interface"""
    def __init__(self, name: str, function: Callable, description: str = "", input_schema: Dict[str, Any] = None):
        self.name = name
        self.function = function
        self.description = description
        self.input_schema = input_schema or {"type": "object", "properties": {}}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema
        }

class MCPResource:
    """MCP resource interface"""
    def __init__(self, uri: str, name: str, description: str = "", mime_type: str = "application/json"):
        self.uri = uri
        self.name = name
        self.description = description
        self.mime_type = mime_type

    def to_dict(self) -> Dict[str, Any]:
        return {
            "uri": self.uri,
            "name": self.name,
            "description": self.description,
            "mimeType": self.mime_type
        }

class MCPPrompt:
    """MCP prompt interface"""
    def __init__(self, name: str, description: str = "", arguments: List[Dict[str, Any]] = None):
        self.name = name
        self.description = description
        self.arguments = arguments or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "arguments": self.arguments
        }

class MCPServer:
    """Model Context Protocol server implementation"""
    
    def __init__(self, name: str = "enhanced-agentic-workflow", version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.tools: Dict[str, MCPTool] = {}
        self.resources: Dict[str, MCPResource] = {}
        self.prompts: Dict[str, MCPPrompt] = {}
        self.capabilities: List[MCPCapability] = [
            MCPCapability.TOOLS,
            MCPCapability.RESOURCES,
            MCPCapability.PROMPTS,
            MCPCapability.LOGGING,
            MCPCapability.PROGRESS
        ]
        self.client_info: Dict[str, Any] = {}
        self.request_handlers: Dict[str, Callable] = {
            "initialize": self._handle_initialize,
            "tools/list": self._handle_tools_list,
            "tools/call": self._handle_tools_call,
            "resources/list": self._handle_resources_list,
            "resources/read": self._handle_resources_read,
            "resources/subscribe": self._handle_resources_subscribe,
            "prompts/list": self._handle_prompts_list,
            "prompts/get": self._handle_prompts_get,
            "logging/setLevel": self._handle_logging_set_level,
            "progress/create": self._handle_progress_create,
            "progress/update": self._handle_progress_update,
            "progress/complete": self._handle_progress_complete,
            "completion/complete": self._handle_completion_complete,
            "ping": self._handle_ping
        }

        # Initialize with default tools and resources
        self._register_default_tools()
        self._register_default_resources()
        self._register_default_prompts()

    async def handle_message(self, message: Dict[str, Any], connection_id: str) -> Dict[str, Any]:
        """Handle MCP protocol messages"""
        try:
            # Validate message structure
            if not isinstance(message, dict):
                return self._error_response(None, MCPErrorCode.INVALID_REQUEST, "Message must be a JSON object")
            
            if "jsonrpc" not in message or message["jsonrpc"] != "2.0":
                return self._error_response(message.get("id"), MCPErrorCode.INVALID_REQUEST, "Invalid JSON-RPC version")
            
            if "method" not in message:
                return self._error_response(message.get("id"), MCPErrorCode.INVALID_REQUEST, "Missing method")
            
            method = message["method"]
            params = message.get("params", {})
            message_id = message.get("id")
            
            # Handle the request
            if method in self.request_handlers:
                try:
                    result = await self.request_handlers[method](params, connection_id)
                    return self._success_response(message_id, result)
                except Exception as e:
                    logfire.error("MCP request handler failed", method=method, error=str(e))
                    return self._error_response(message_id, MCPErrorCode.INTERNAL_ERROR, f"Handler failed: {str(e)}")
            else:
                return self._error_response(message_id, MCPErrorCode.METHOD_NOT_FOUND, f"Unknown method: {method}")
            
        except json.JSONDecodeError:
            return self._error_response(None, MCPErrorCode.PARSE_ERROR, "Invalid JSON")
        except Exception as e:
            logfire.error("Failed to handle MCP message", error=str(e))
            return self._error_response(None, MCPErrorCode.SERVER_ERROR, f"Server error: {str(e)}")

    async def _handle_initialize(self, params: Dict[str, Any], connection_id: str) -> Dict[str, Any]:
        """Handle initialize request"""
        self.client_info[connection_id] = {
            "clientInfo": params.get("clientInfo", {}),
            "capabilities": params.get("capabilities", {}),
            "protocolVersion": params.get("protocolVersion", "2024-11-05")
        }
        
        return {
            "serverInfo": {
                "name": self.name,
                "version": self.version
            },
            "capabilities": {
                "tools": {"listChanged": True},
                "resources": {"listChanged": True, "subscribe": True},
                "prompts": {"listChanged": True},
                "logging": {},
                "progress": {"supports": True}
            },
            "protocolVersion": "2024-11-05"
        }

    async def _handle_tools_list(self, params: Dict[str, Any], connection_id: str) -> Dict[str, Any]:
        """Handle tools/list request"""
        return {
            "tools": [tool.to_dict() for tool in self.tools.values()]
        }

    async def _handle_tools_call(self, params: Dict[str, Any], connection_id: str) -> Dict[str, Any]:
        """Handle tools/call request"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if not tool_name:
            raise ValueError("Tool name is required")
        
        if tool_name not in self.tools:
            raise ValueError(f"Tool not found: {tool_name}")
        
        tool = self.tools[tool_name]
        
        try:
            # Execute tool function
            if asyncio.iscoroutinefunction(tool.function):
                result = await tool.function(**arguments)
            else:
                result = tool.function(**arguments)
            
            return {
                "content": [{
                    "type": "text",
                    "text": str(result)
                }],
                "isError": False
            }
            
        except Exception as e:
            logfire.error("Tool execution failed", tool_name=tool_name, error=str(e))
            return {
                "content": [{
                    "type": "text",
                    "text": f"Tool execution failed: {str(e)}"
                }],
                "isError": True
            }

    async def _handle_resources_list(self, params: Dict[str, Any], connection_id: str) -> Dict[str, Any]:
        """Handle resources/list request"""
        return {
            "resources": [resource.to_dict() for resource in self.resources.values()]
        }

    async def _handle_resources_read(self, params: Dict[str, Any], connection_id: str) -> Dict[str, Any]:
        """Handle resources/read request"""
        uri = params.get("uri")
        
        if not uri:
            raise ValueError("Resource URI is required")
        
        if uri not in self.resources:
            raise ValueError(f"Resource not found: {uri}")
        
        resource = self.resources[uri]
        
        # Generate resource content based on URI
        content = await self._generate_resource_content(uri)
        
        return {
            "contents": [{
                "uri": uri,
                "mimeType": resource.mime_type,
                "text": content
            }]
        }

    async def _handle_resources_subscribe(self, params: Dict[str, Any], connection_id: str) -> Dict[str, Any]:
        """Handle resources/subscribe request"""
        uri = params.get("uri")
        
        if not uri:
            raise ValueError("Resource URI is required")
        
        if uri not in self.resources:
            raise ValueError(f"Resource not found: {uri}")
        
        # TODO: Implement resource subscription
        return {"success": True}

    async def _handle_prompts_list(self, params: Dict[str, Any], connection_id: str) -> Dict[str, Any]:
        """Handle prompts/list request"""
        return {
            "prompts": [prompt.to_dict() for prompt in self.prompts.values()]
        }

    async def _handle_prompts_get(self, params: Dict[str, Any], connection_id: str) -> Dict[str, Any]:
        """Handle prompts/get request"""
        name = params.get("name")
        arguments = params.get("arguments", {})
        
        if not name:
            raise ValueError("Prompt name is required")
        
        if name not in self.prompts:
            raise ValueError(f"Prompt not found: {name}")
        
        # Generate prompt content
        prompt_content = await self._generate_prompt_content(name, arguments)
        
        return {
            "description": self.prompts[name].description,
            "messages": [{
                "role": "user",
                "content": {
                    "type": "text",
                    "text": prompt_content
                }
            }]
        }

    async def _handle_logging_set_level(self, params: Dict[str, Any], connection_id: str) -> Dict[str, Any]:
        """Handle logging/setLevel request"""
        level = params.get("level")
        # TODO: Implement logging level management
        return {"success": True}

    async def _handle_progress_create(self, params: Dict[str, Any], connection_id: str) -> Dict[str, Any]:
        """Handle progress/create request"""
        progress_id = str(uuid.uuid4())
        # TODO: Implement progress tracking
        return {"progressId": progress_id}

    async def _handle_progress_update(self, params: Dict[str, Any], connection_id: str) -> Dict[str, Any]:
        """Handle progress/update request"""
        # TODO: Implement progress update
        return {"success": True}

    async def _handle_progress_complete(self, params: Dict[str, Any], connection_id: str) -> Dict[str, Any]:
        """Handle progress/complete request"""
        # TODO: Implement progress completion
        return {"success": True}

    async def _handle_completion_complete(self, params: Dict[str, Any], connection_id: str) -> Dict[str, Any]:
        """Handle completion/complete request"""
        # TODO: Implement completion suggestions
        return {"completion": {"values": [], "total": 0, "hasMore": False}}

    async def _handle_ping(self, params: Dict[str, Any], connection_id: str) -> Dict[str, Any]:
        """Handle ping request"""
        return {"pong": True, "timestamp": datetime.now().isoformat()}

    def _success_response(self, message_id: Optional[str], result: Any) -> Dict[str, Any]:
        """Create success response"""
        return {
            "jsonrpc": "2.0",
            "id": message_id,
            "result": result
        }

    def _error_response(self, message_id: Optional[str], error_code: MCPErrorCode, message: str) -> Dict[str, Any]:
        """Create error response"""
        return {
            "jsonrpc": "2.0",
            "id": message_id,
            "error": {
                "code": error_code.value,
                "message": message
            }
        }

    def register_tool(self, name: str, function: Callable, description: str = "", input_schema: Dict[str, Any] = None):
        """Register a tool for MCP access"""
        self.tools[name] = MCPTool(name=name, function=function, description=description, input_schema=input_schema)

    def register_resource(self, uri: str, name: str, description: str = "", mime_type: str = "application/json"):
        """Register a resource for MCP access"""
        self.resources[uri] = MCPResource(uri=uri, name=name, description=description, mime_type=mime_type)

    def register_prompt(self, name: str, description: str = "", arguments: List[Dict[str, Any]] = None):
        """Register a prompt for MCP access"""
        self.prompts[name] = MCPPrompt(name=name, description=description, arguments=arguments)

    def _register_default_tools(self):
        """Register default tools"""
        self.register_tool(
            "execute_workflow",
            self._tool_execute_workflow,
            "Execute a workflow with the specified configuration",
            {
                "type": "object",
                "properties": {
                    "workflow_type": {"type": "string", "description": "Type of workflow to execute"},
                    "query": {"type": "string", "description": "Query to process"},
                    "configuration": {"type": "object", "description": "Workflow configuration"}
                },
                "required": ["workflow_type", "query"]
            }
        )
        
        self.register_tool(
            "generate_agent",
            self._tool_generate_agent,
            "Generate a new agent based on requirements",
            {
                "type": "object",
                "properties": {
                    "agent_type": {"type": "string", "description": "Type of agent to generate"},
                    "requirements": {"type": "string", "description": "Agent requirements"},
                    "tools": {"type": "array", "items": {"type": "string"}, "description": "Tools to include"}
                },
                "required": ["agent_type", "requirements"]
            }
        )
        
        self.register_tool(
            "get_system_status",
            self._tool_get_system_status,
            "Get current system status and health information",
            {"type": "object", "properties": {}}
        )

    def _register_default_resources(self):
        """Register default resources"""
        self.register_resource(
            "agent://templates",
            "Agent Templates",
            "Available agent templates for generation",
            "application/json"
        )
        
        self.register_resource(
            "workflow://templates",
            "Workflow Templates",
            "Available workflow templates for execution",
            "application/json"
        )
        
        self.register_resource(
            "system://status",
            "System Status",
            "Current system status and metrics",
            "application/json"
        )

    def _register_default_prompts(self):
        """Register default prompts"""
        self.register_prompt(
            "generate_agent",
            "Generate a new agent based on requirements",
            [
                {"name": "agent_type", "description": "Type of agent to generate", "required": True},
                {"name": "requirements", "description": "Detailed requirements", "required": True},
                {"name": "template_id", "description": "Optional template ID", "required": False}
            ]
        )
        
        self.register_prompt(
            "analyze_code",
            "Analyze code and provide insights",
            [
                {"name": "code", "description": "Code to analyze", "required": True},
                {"name": "language", "description": "Programming language", "required": False}
            ]
        )

    async def _generate_resource_content(self, uri: str) -> str:
        """Generate content for a resource"""
        if uri == "agent://templates":
            # Return agent templates
            return json.dumps({
                "templates": [
                    {"id": "coder", "name": "Coder Agent", "description": "Code generation and analysis"},
                    {"id": "research", "name": "Research Agent", "description": "Research and analysis"},
                    {"id": "synthesis", "name": "Synthesis Agent", "description": "Result synthesis"}
                ]
            }, indent=2)
        
        elif uri == "workflow://templates":
            # Return workflow templates
            return json.dumps({
                "templates": [
                    {"id": "grok_heavy", "name": "Grok Heavy Analysis", "description": "Deep multi-agent analysis"},
                    {"id": "multi_agent", "name": "Multi-Agent", "description": "Coordinated multi-agent execution"},
                    {"id": "single_agent", "name": "Single Agent", "description": "Simple single agent execution"}
                ]
            }, indent=2)
        
        elif uri == "system://status":
            # Return system status
            return json.dumps({
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "version": self.version,
                "active_agents": 0,
                "active_workflows": 0
            }, indent=2)
        
        return json.dumps({"error": "Resource not found"}, indent=2)

    async def _generate_prompt_content(self, name: str, arguments: Dict[str, Any]) -> str:
        """Generate content for a prompt"""
        if name == "generate_agent":
            agent_type = arguments.get("agent_type", "general")
            requirements = arguments.get("requirements", "No specific requirements")
            template_id = arguments.get("template_id", "None")
            
            return f"""Generate a new {agent_type} agent with the following specifications:

Requirements: {requirements}
Template ID: {template_id}

Please provide a detailed implementation plan and configuration for this agent."""
        
        elif name == "analyze_code":
            code = arguments.get("code", "No code provided")
            language = arguments.get("language", "auto-detect")
            
            return f"""Analyze the following {language} code and provide insights:

```{language}
{code}
```

Please provide:
1. Code quality assessment
2. Potential improvements
3. Security considerations
4. Performance optimization suggestions"""
        
        return f"Prompt '{name}' with arguments: {arguments}"

    async def _tool_execute_workflow(self, workflow_type: str, query: str, configuration: Dict[str, Any] = None) -> str:
        """Execute workflow tool"""
        # This would integrate with the actual workflow execution system
        return f"Workflow '{workflow_type}' executed with query: {query}"

    async def _tool_generate_agent(self, agent_type: str, requirements: str, tools: List[str] = None) -> str:
        """Generate agent tool"""
        # This would integrate with the actual agent generation system
        return f"Agent '{agent_type}' generated with requirements: {requirements}"

    async def _tool_get_system_status(self) -> str:
        """Get system status tool"""
        return json.dumps({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": self.version,
            "capabilities": [cap.value for cap in self.capabilities]
        }, indent=2)

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any], call_id: str = None) -> Any:
        """Execute a tool directly (for API compatibility)"""
        if tool_name not in self.tools:
            raise ValueError(f"Tool not found: {tool_name}")
        
        tool = self.tools[tool_name]
        
        if asyncio.iscoroutinefunction(tool.function):
            return await tool.function(**arguments)
        else:
            return tool.function(**arguments)
