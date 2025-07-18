from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from ...library.agent_templates import AgentTemplateLibrary
from ...library.tool_library import ToolLibrary
from ...agents.prompt_refiner import PromptRefinerAgent
from ...agents.tools_refiner import ToolsRefinerAgent
from ...agents.agent_refiner import AgentRefinerAgent
import logfire

router = APIRouter()

class AgentTemplate(BaseModel):
    """Agent template model"""
    id: str
    name: str
    description: str
    category: str
    tags: List[str]
    system_prompt: str
    required_dependencies: List[str]
    recommended_tools: List[str]
    configuration: Dict[str, Any]

class ToolDefinition(BaseModel):
    """Tool definition model"""
    name: str
    description: str
    category: str
    tags: List[str]
    parameters: Dict[str, Any]
    mcp_compatible: bool
    dependencies: List[str]

class RefineRequest(BaseModel):
    """Request model for agent refinement"""
    refinement_type: str  # prompt, tools, agent
    target_config: Dict[str, Any]
    improvement_goals: List[str] = []

class RefineResponse(BaseModel):
    """Response model for agent refinement"""
    refinement_id: str
    status: str
    improvements: List[str]
    updated_config: Dict[str, Any]
    effectiveness_score: float

# Global state for active agents (would be in database in production)
active_agents: Dict[str, Any] = {}

@router.get("/templates", response_model=List[AgentTemplate])
async def list_agent_templates(
    category: Optional[str] = None,
    search: Optional[str] = None
):
    """List all available agent templates"""
    try:
        template_lib = AgentTemplateLibrary()
        templates = await template_lib.list_templates(category=category)
        
        if search:
            templates = [t for t in templates if search.lower() in t.description.lower() or 
                        any(search.lower() in tag.lower() for tag in t.tags)]
        
        return [AgentTemplate(
            id=t.id,
            name=t.name,
            description=t.description,
            category=t.category,
            tags=t.tags,
            system_prompt=t.system_prompt,
            required_dependencies=t.required_dependencies,
            recommended_tools=t.recommended_tools,
            configuration=t.configuration
        ) for t in templates]
        
    except Exception as e:
        logfire.error("Failed to list agent templates", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to list templates: {str(e)}")

@router.get("/templates/{template_id}", response_model=AgentTemplate)
async def get_agent_template(template_id: str):
    """Get a specific agent template"""
    try:
        template_lib = AgentTemplateLibrary()
        template = await template_lib.get_template(template_id)
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        return AgentTemplate(
            id=template.id,
            name=template.name,
            description=template.description,
            category=template.category,
            tags=template.tags,
            system_prompt=template.system_prompt,
            required_dependencies=template.required_dependencies,
            recommended_tools=template.recommended_tools,
            configuration=template.configuration
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logfire.error("Failed to get agent template", template_id=template_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get template: {str(e)}")

@router.get("/tools", response_model=List[ToolDefinition])
async def list_available_tools(
    category: Optional[str] = None,
    search: Optional[str] = None,
    mcp_compatible: Optional[bool] = None
):
    """List all available tools"""
    try:
        tool_lib = ToolLibrary()
        tools = await tool_lib.list_tools(category=category)
        
        if search:
            tools = [t for t in tools if search.lower() in t.description.lower() or 
                    any(search.lower() in tag.lower() for tag in t.tags)]
        
        if mcp_compatible is not None:
            tools = [t for t in tools if t.mcp_compatible == mcp_compatible]
        
        return [ToolDefinition(
            name=t.name,
            description=t.description,
            category=t.category,
            tags=t.tags,
            parameters=t.parameters,
            mcp_compatible=t.mcp_compatible,
            dependencies=t.dependencies
        ) for t in tools]
        
    except Exception as e:
        logfire.error("Failed to list tools", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to list tools: {str(e)}")

@router.get("/tools/{tool_name}", response_model=ToolDefinition)
async def get_tool_definition(tool_name: str):
    """Get a specific tool definition"""
    try:
        tool_lib = ToolLibrary()
        tools = await tool_lib.get_tools([tool_name])
        
        if not tools:
            raise HTTPException(status_code=404, detail="Tool not found")
        
        tool = tools[0]
        return ToolDefinition(
            name=tool.name,
            description=tool.description,
            category=tool.category,
            tags=tool.tags,
            parameters=tool.parameters,
            mcp_compatible=tool.mcp_compatible,
            dependencies=tool.dependencies
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logfire.error("Failed to get tool definition", tool_name=tool_name, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get tool: {str(e)}")

@router.post("/refine/{agent_id}", response_model=RefineResponse)
async def refine_agent(agent_id: str, request: RefineRequest):
    """Trigger agent refinement"""
    try:
        if agent_id not in active_agents:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        agent_data = active_agents[agent_id]
        
        # Choose refiner based on type
        if request.refinement_type == "prompt":
            refiner = PromptRefinerAgent()
        elif request.refinement_type == "tools":
            refiner = ToolsRefinerAgent()
        elif request.refinement_type == "agent":
            refiner = AgentRefinerAgent()
        else:
            raise HTTPException(status_code=400, detail="Invalid refinement type")
        
        # Run refinement
        refined_result = await refiner.refine(agent_data)
        active_agents[agent_id] = refined_result
        
        import uuid
        refinement_id = str(uuid.uuid4())
        
        logfire.info(
            "Agent refinement completed",
            agent_id=agent_id,
            refinement_id=refinement_id,
            refinement_type=request.refinement_type
        )
        
        return RefineResponse(
            refinement_id=refinement_id,
            status="completed",
            improvements=refined_result.get("improvements", []),
            updated_config=refined_result.get("config", {}),
            effectiveness_score=refined_result.get("effectiveness_score", 0.85)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logfire.error("Agent refinement failed", agent_id=agent_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Refinement failed: {str(e)}")

@router.get("/search/templates")
async def search_agent_templates(
    query: str,
    limit: int = 10,
    category: Optional[str] = None
):
    """Search agent templates"""
    try:
        template_lib = AgentTemplateLibrary()
        templates = await template_lib.search_templates(query)
        
        if category:
            templates = [t for t in templates if t.category == category]
        
        return templates[:limit]
        
    except Exception as e:
        logfire.error("Template search failed", query=query, error=str(e))
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/search/tools")
async def search_tools(
    query: str,
    limit: int = 10,
    category: Optional[str] = None
):
    """Search available tools"""
    try:
        tool_lib = ToolLibrary()
        tools = await tool_lib.search_tools(query, limit=limit)
        
        if category:
            tools = [t for t in tools if t.category == category]
        
        return tools
        
    except Exception as e:
        logfire.error("Tool search failed", query=query, error=str(e))
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/recommendations/tools")
async def get_tool_recommendations(
    requirements: str,
    limit: int = 5
):
    """Get tool recommendations based on requirements"""
    try:
        tool_lib = ToolLibrary()
        recommended_tools = await tool_lib.get_recommended_tools(requirements)
        
        return recommended_tools[:limit]
        
    except Exception as e:
        logfire.error("Tool recommendation failed", requirements=requirements, error=str(e))
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")

@router.get("/stats")
async def get_agent_stats():
    """Get agent system statistics"""
    try:
        template_lib = AgentTemplateLibrary()
        tool_lib = ToolLibrary()
        
        templates = await template_lib.list_templates()
        tools = await tool_lib.list_tools()
        
        template_categories = {}
        tool_categories = {}
        
        for template in templates:
            template_categories[template.category] = template_categories.get(template.category, 0) + 1
        
        for tool in tools:
            tool_categories[tool.category] = tool_categories.get(tool.category, 0) + 1
        
        return {
            "active_agents": len(active_agents),
            "total_templates": len(templates),
            "total_tools": len(tools),
            "template_categories": template_categories,
            "tool_categories": tool_categories,
            "mcp_compatible_tools": len([t for t in tools if t.mcp_compatible])
        }
        
    except Exception as e:
        logfire.error("Failed to get agent stats", error=str(e))
        raise HTTPException(status_code=500, detail=f"Stats failed: {str(e)}")

@router.delete("/agents/{agent_id}")
async def delete_agent(agent_id: str):
    """Delete an agent"""
    try:
        if agent_id not in active_agents:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        del active_agents[agent_id]
        
        logfire.info("Agent deleted", agent_id=agent_id)
        
        return {"message": "Agent deleted successfully", "agent_id": agent_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logfire.error("Agent deletion failed", agent_id=agent_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")

@router.get("/agents/{agent_id}/config")
async def get_agent_config(agent_id: str):
    """Get agent configuration"""
    try:
        if agent_id not in active_agents:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        agent_data = active_agents[agent_id]
        
        return {
            "agent_id": agent_id,
            "config": agent_data.get("config", {}),
            "tools": agent_data.get("tools", []),
            "dependencies": agent_data.get("dependencies", []),
            "template_id": agent_data.get("template_id"),
            "created_at": agent_data.get("created_at"),
            "last_updated": agent_data.get("last_updated")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logfire.error("Failed to get agent config", agent_id=agent_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Config retrieval failed: {str(e)}")

@router.put("/agents/{agent_id}/config")
async def update_agent_config(agent_id: str, config: Dict[str, Any]):
    """Update agent configuration"""
    try:
        if agent_id not in active_agents:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        agent_data = active_agents[agent_id]
        agent_data["config"] = config
        agent_data["last_updated"] = datetime.now().isoformat()
        
        logfire.info("Agent config updated", agent_id=agent_id)
        
        return {
            "message": "Agent configuration updated successfully",
            "agent_id": agent_id,
            "config": config
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logfire.error("Agent config update failed", agent_id=agent_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Config update failed: {str(e)}")
