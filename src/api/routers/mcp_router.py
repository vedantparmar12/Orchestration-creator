from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import json
import uuid
import asyncio
from datetime import datetime
from ...mcp.protocol import MCPServer, MCPMessage, MCPTool, MCPResource
from ...library.tool_library import ToolLibrary
import logfire

router = APIRouter()

class MCPServerConfig(BaseModel):
    """MCP server configuration"""
    name: str
    version: str
    description: str
    capabilities: List[str]
    tools: List[str]
    resources: List[str]
    prompts: List[str]

class MCPConnectionRequest(BaseModel):
    """MCP connection request"""
    client_info: Dict[str, Any]
    protocol_version: str = "2024-11-05"
    capabilities: Dict[str, Any] = {}

class MCPConnectionResponse(BaseModel):
    """MCP connection response"""
    connection_id: str
    server_info: Dict[str, Any]
    capabilities: Dict[str, Any]
    protocol_version: str

class MCPToolCall(BaseModel):
    """MCP tool call request"""
    name: str
    arguments: Dict[str, Any]
    call_id: Optional[str] = None

class MCPToolResponse(BaseModel):
    """MCP tool response"""
    call_id: str
    result: Any
    error: Optional[str] = None
    metadata: Dict[str, Any] = {}

# Global MCP server instance
mcp_server = MCPServer()
active_connections: Dict[str, Dict[str, Any]] = {}

@router.get("/server/info", response_model=MCPServerConfig)
async def get_mcp_server_info():
    """Get MCP server information"""
    try:
        tool_lib = ToolLibrary()
        available_tools = await tool_lib.list_tools()
        mcp_tools = [tool.name for tool in available_tools if tool.mcp_compatible]
        
        return MCPServerConfig(
            name="enhanced-agentic-workflow",
            version="1.0.0",
            description="Enhanced Agentic Workflow MCP Server",
            capabilities=["tools", "resources", "prompts", "progress"],
            tools=mcp_tools,
            resources=["agent_templates", "knowledge_base", "execution_history"],
            prompts=["generate_agent", "analyze_code", "optimize_workflow"]
        )
        
    except Exception as e:
        logfire.error("Failed to get MCP server info", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get server info: {str(e)}")

@router.post("/connect", response_model=MCPConnectionResponse)
async def connect_mcp_client(request: MCPConnectionRequest):
    """Connect MCP client to server"""
    try:
        connection_id = str(uuid.uuid4())
        
        # Store connection info
        active_connections[connection_id] = {
            "client_info": request.client_info,
            "protocol_version": request.protocol_version,
            "capabilities": request.capabilities,
            "connected_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat()
        }
        
        server_info = {
            "name": "enhanced-agentic-workflow",
            "version": "1.0.0",
            "description": "Enhanced Agentic Workflow MCP Server"
        }
        
        server_capabilities = {
            "tools": {"listChanged": True},
            "resources": {"listChanged": True, "subscribe": True},
            "prompts": {"listChanged": True},
            "progress": {"supports": True}
        }
        
        logfire.info(
            "MCP client connected",
            connection_id=connection_id,
            client_info=request.client_info
        )
        
        return MCPConnectionResponse(
            connection_id=connection_id,
            server_info=server_info,
            capabilities=server_capabilities,
            protocol_version=request.protocol_version
        )
        
    except Exception as e:
        logfire.error("MCP connection failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Connection failed: {str(e)}")

@router.get("/tools/list")
async def list_mcp_tools(connection_id: Optional[str] = None):
    """List available MCP tools"""
    try:
        # Update connection activity
        if connection_id and connection_id in active_connections:
            active_connections[connection_id]["last_activity"] = datetime.now().isoformat()
        
        tool_lib = ToolLibrary()
        available_tools = await tool_lib.list_tools()
        mcp_tools = [tool for tool in available_tools if tool.mcp_compatible]
        
        tools = []
        for tool in mcp_tools:
            tools.append({
                "name": tool.name,
                "description": tool.description,
                "inputSchema": {
                    "type": "object",
                    "properties": tool.parameters,
                    "required": tool.dependencies
                }
            })
        
        return {"tools": tools}
        
    except Exception as e:
        logfire.error("Failed to list MCP tools", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to list tools: {str(e)}")

@router.post("/tools/call", response_model=MCPToolResponse)
async def call_mcp_tool(request: MCPToolCall, connection_id: Optional[str] = None):
    """Call an MCP tool"""
    try:
        call_id = request.call_id or str(uuid.uuid4())
        
        # Update connection activity
        if connection_id and connection_id in active_connections:
            active_connections[connection_id]["last_activity"] = datetime.now().isoformat()
        
        logfire.info(
            "MCP tool call",
            tool_name=request.name,
            call_id=call_id,
            connection_id=connection_id
        )
        
        # Execute tool
        result = await mcp_server.execute_tool(
            request.name,
            request.arguments,
            call_id=call_id
        )
        
        return MCPToolResponse(
            call_id=call_id,
            result=result,
            metadata={
                "execution_time": datetime.now().isoformat(),
                "tool_name": request.name
            }
        )
        
    except Exception as e:
        logfire.error("MCP tool call failed", tool_name=request.name, error=str(e))
        return MCPToolResponse(
            call_id=request.call_id or str(uuid.uuid4()),
            result=None,
            error=str(e),
            metadata={"error_time": datetime.now().isoformat()}
        )

@router.get("/resources/list")
async def list_mcp_resources(connection_id: Optional[str] = None):
    """List available MCP resources"""
    try:
        # Update connection activity
        if connection_id and connection_id in active_connections:
            active_connections[connection_id]["last_activity"] = datetime.now().isoformat()
        
        resources = [
            {
                "uri": "agent://templates",
                "name": "Agent Templates",
                "description": "Available agent templates",
                "mimeType": "application/json"
            },
            {
                "uri": "knowledge://base",
                "name": "Knowledge Base",
                "description": "Vector knowledge base",
                "mimeType": "application/json"
            },
            {
                "uri": "execution://history",
                "name": "Execution History",
                "description": "Workflow execution history",
                "mimeType": "application/json"
            }
        ]
        
        return {"resources": resources}
        
    except Exception as e:
        logfire.error("Failed to list MCP resources", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to list resources: {str(e)}")

@router.get("/resources/read")
async def read_mcp_resource(uri: str, connection_id: Optional[str] = None):
    """Read an MCP resource"""
    try:
        # Update connection activity
        if connection_id and connection_id in active_connections:
            active_connections[connection_id]["last_activity"] = datetime.now().isoformat()
        
        if uri == "agent://templates":
            from ...library.agent_templates import AgentTemplateLibrary
            template_lib = AgentTemplateLibrary()
            templates = await template_lib.list_templates()
            
            return {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": json.dumps([template.dict() for template in templates], indent=2)
                    }
                ]
            }
        
        elif uri == "knowledge://base":
            from ...knowledge.vector_search import VectorKnowledgeBase
            # Return knowledge base info
            return {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": json.dumps({"status": "available", "type": "vector_database"}, indent=2)
                    }
                ]
            }
        
        elif uri == "execution://history":
            # Return execution history
            return {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": json.dumps({"executions": []}, indent=2)
                    }
                ]
            }
        
        else:
            raise HTTPException(status_code=404, detail="Resource not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logfire.error("Failed to read MCP resource", uri=uri, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to read resource: {str(e)}")

@router.get("/prompts/list")
async def list_mcp_prompts(connection_id: Optional[str] = None):
    """List available MCP prompts"""
    try:
        # Update connection activity
        if connection_id and connection_id in active_connections:
            active_connections[connection_id]["last_activity"] = datetime.now().isoformat()
        
        prompts = [
            {
                "name": "generate_agent",
                "description": "Generate a new agent based on requirements",
                "arguments": [
                    {
                        "name": "agent_type",
                        "description": "Type of agent to generate",
                        "required": True
                    },
                    {
                        "name": "requirements",
                        "description": "Detailed requirements for the agent",
                        "required": True
                    },
                    {
                        "name": "template_id",
                        "description": "Optional template ID to use",
                        "required": False
                    }
                ]
            },
            {
                "name": "analyze_code",
                "description": "Analyze code and provide insights",
                "arguments": [
                    {
                        "name": "code",
                        "description": "Code to analyze",
                        "required": True
                    },
                    {
                        "name": "language",
                        "description": "Programming language",
                        "required": False
                    }
                ]
            },
            {
                "name": "optimize_workflow",
                "description": "Optimize workflow configuration",
                "arguments": [
                    {
                        "name": "workflow_config",
                        "description": "Current workflow configuration",
                        "required": True
                    },
                    {
                        "name": "optimization_goals",
                        "description": "Optimization goals",
                        "required": False
                    }
                ]
            }
        ]
        
        return {"prompts": prompts}
        
    except Exception as e:
        logfire.error("Failed to list MCP prompts", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to list prompts: {str(e)}")

@router.post("/prompts/get")
async def get_mcp_prompt(
    name: str,
    arguments: Dict[str, Any] = {},
    connection_id: Optional[str] = None
):
    """Get an MCP prompt"""
    try:
        # Update connection activity
        if connection_id and connection_id in active_connections:
            active_connections[connection_id]["last_activity"] = datetime.now().isoformat()
        
        if name == "generate_agent":
            prompt = f"""Generate a new agent with the following specifications:

Agent Type: {arguments.get('agent_type', 'general')}
Requirements: {arguments.get('requirements', 'No specific requirements')}
Template ID: {arguments.get('template_id', 'None')}

Please provide a detailed implementation plan and configuration for this agent."""
        
        elif name == "analyze_code":
            prompt = f"""Analyze the following code and provide insights:

Language: {arguments.get('language', 'auto-detect')}
Code:
```
{arguments.get('code', 'No code provided')}
```

Please provide analysis including:
1. Code quality assessment
2. Potential improvements
3. Security considerations
4. Performance optimization suggestions"""
        
        elif name == "optimize_workflow":
            prompt = f"""Optimize the following workflow configuration:

Current Configuration:
{json.dumps(arguments.get('workflow_config', {}), indent=2)}

Optimization Goals: {arguments.get('optimization_goals', 'General optimization')}

Please provide optimization recommendations and updated configuration."""
        
        else:
            raise HTTPException(status_code=404, detail="Prompt not found")
        
        return {
            "description": f"Generated prompt for {name}",
            "messages": [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": prompt
                    }
                }
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logfire.error("Failed to get MCP prompt", name=name, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get prompt: {str(e)}")

@router.websocket("/ws/{connection_id}")
async def mcp_websocket(websocket: WebSocket, connection_id: str):
    """WebSocket endpoint for MCP real-time communication"""
    try:
        await websocket.accept()
        
        if connection_id not in active_connections:
            await websocket.close(code=1008, reason="Invalid connection ID")
            return
        
        logfire.info("MCP WebSocket connected", connection_id=connection_id)
        
        while True:
            try:
                # Receive message
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Process MCP message
                response = await mcp_server.handle_message(message, connection_id)
                
                # Send response
                await websocket.send_text(json.dumps(response))
                
                # Update connection activity
                active_connections[connection_id]["last_activity"] = datetime.now().isoformat()
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logfire.error("WebSocket message error", error=str(e))
                error_response = {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32603,
                        "message": "Internal error",
                        "data": str(e)
                    }
                }
                await websocket.send_text(json.dumps(error_response))
    
    except Exception as e:
        logfire.error("WebSocket connection error", error=str(e))
    
    finally:
        if connection_id in active_connections:
            active_connections[connection_id]["disconnected_at"] = datetime.now().isoformat()
        logfire.info("MCP WebSocket disconnected", connection_id=connection_id)

@router.get("/connections")
async def list_mcp_connections():
    """List active MCP connections"""
    try:
        return {
            "active_connections": len(active_connections),
            "connections": [
                {
                    "connection_id": conn_id,
                    "client_info": conn_data["client_info"],
                    "connected_at": conn_data["connected_at"],
                    "last_activity": conn_data["last_activity"],
                    "protocol_version": conn_data["protocol_version"]
                }
                for conn_id, conn_data in active_connections.items()
                if "disconnected_at" not in conn_data
            ]
        }
        
    except Exception as e:
        logfire.error("Failed to list MCP connections", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to list connections: {str(e)}")

@router.delete("/connections/{connection_id}")
async def disconnect_mcp_client(connection_id: str):
    """Disconnect MCP client"""
    try:
        if connection_id not in active_connections:
            raise HTTPException(status_code=404, detail="Connection not found")
        
        active_connections[connection_id]["disconnected_at"] = datetime.now().isoformat()
        
        logfire.info("MCP client disconnected", connection_id=connection_id)
        
        return {"message": "Client disconnected successfully", "connection_id": connection_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logfire.error("Failed to disconnect MCP client", connection_id=connection_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Disconnect failed: {str(e)}")

@router.get("/stats")
async def get_mcp_stats():
    """Get MCP server statistics"""
    try:
        active_count = len([c for c in active_connections.values() if "disconnected_at" not in c])
        total_count = len(active_connections)
        
        return {
            "active_connections": active_count,
            "total_connections": total_count,
            "server_status": "running",
            "protocol_version": "2024-11-05",
            "uptime": (datetime.now() - datetime.fromisoformat("2024-01-01T00:00:00")).total_seconds()
        }
        
    except Exception as e:
        logfire.error("Failed to get MCP stats", error=str(e))
        raise HTTPException(status_code=500, detail=f"Stats failed: {str(e)}")
