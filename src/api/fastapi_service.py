from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import asyncio
import uuid
import json
from datetime import datetime
from .routers import agent_router, mcp_router, workflow_router
from ..agents.models import *
from ..orchestration.coordinator import AgentCoordinator
from ..library.agent_templates import AgentTemplateLibrary
from ..library.tool_library import ToolLibrary
import logfire

# Configure Logfire
logfire.configure()

class AgentGenerationRequest(BaseModel):
    """Request model for agent generation"""
    agent_type: str
    requirements: str
    template_id: Optional[str] = None
    tools: List[str] = []
    dependencies: Dict[str, Any] = {}
    configuration: Dict[str, Any] = {}

class AgentGenerationResponse(BaseModel):
    """Response model for agent generation"""
    agent_id: str
    status: str
    message: str
    generated_files: List[str] = []
    setup_instructions: List[str] = []
    agent_config: Dict[str, Any] = {}

class WorkflowExecutionRequest(BaseModel):
    """Request model for workflow execution"""
    query: str
    mode: str = "grok_heavy"  # grok_heavy, single_agent, multi_agent
    agent_configs: Dict[str, Any] = {}
    max_parallel_agents: int = 4
    enable_deep_reflection: bool = True

class WorkflowExecutionResponse(BaseModel):
    """Response model for workflow execution"""
    execution_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    progress: Dict[str, Any] = {}
    error: Optional[str] = None

class SystemStatusResponse(BaseModel):
    """System status response"""
    system_health: str
    active_agents: int
    active_workflows: int
    total_requests: int
    uptime: str
    version: str

app = FastAPI(
    title="Enhanced Agentic Workflow API",
    description="Production-ready API for agent generation and workflow management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(agent_router.router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(mcp_router.router, prefix="/api/v1/mcp", tags=["mcp"])
app.include_router(workflow_router.router, prefix="/api/v1/workflows", tags=["workflows"])

# Global state for agent management
active_agents: Dict[str, Any] = {}
active_workflows: Dict[str, Any] = {}
generation_tasks: Dict[str, str] = {}
system_stats = {
    "total_requests": 0,
    "start_time": datetime.now()
}

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logfire.info("FastAPI service starting up")
    
    # Initialize core services
    global agent_coordinator, template_library, tool_library
    agent_coordinator = AgentCoordinator()
    template_library = AgentTemplateLibrary()
    tool_library = ToolLibrary()
    
    logfire.info("FastAPI service started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logfire.info("FastAPI service shutting down")
    
    # Cancel active workflows
    for workflow_id, workflow in active_workflows.items():
        if workflow.get("task") and not workflow["task"].done():
            workflow["task"].cancel()
    
    logfire.info("FastAPI service shut down successfully")

@app.middleware("http")
async def log_requests(request, call_next):
    """Log all requests"""
    system_stats["total_requests"] += 1
    
    start_time = datetime.now()
    response = await call_next(request)
    process_time = (datetime.now() - start_time).total_seconds()
    
    logfire.info(
        "HTTP request",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        process_time=process_time
    )
    
    return response

@app.get("/health", response_model=SystemStatusResponse)
async def health_check():
    """System health check endpoint"""
    uptime = datetime.now() - system_stats["start_time"]
    
    return SystemStatusResponse(
        system_health="healthy",
        active_agents=len(active_agents),
        active_workflows=len(active_workflows),
        total_requests=system_stats["total_requests"],
        uptime=str(uptime),
        version="1.0.0"
    )

@app.post("/api/v1/generate-agent", response_model=AgentGenerationResponse)
async def generate_agent(
    request: AgentGenerationRequest, 
    background_tasks: BackgroundTasks
):
    """Generate a new agent based on requirements"""
    agent_id = str(uuid.uuid4())
    
    logfire.info(
        "Agent generation requested",
        agent_id=agent_id,
        agent_type=request.agent_type,
        requirements=request.requirements[:100] + "..." if len(request.requirements) > 100 else request.requirements
    )
    
    # Start background task for agent generation
    background_tasks.add_task(
        _generate_agent_background,
        agent_id,
        request
    )
    
    generation_tasks[agent_id] = "in_progress"
    
    return AgentGenerationResponse(
        agent_id=agent_id,
        status="generation_started",
        message=f"Agent generation started with ID: {agent_id}"
    )

@app.post("/api/v1/execute-workflow", response_model=WorkflowExecutionResponse)
async def execute_workflow(
    request: WorkflowExecutionRequest,
    background_tasks: BackgroundTasks
):
    """Execute a workflow with specified configuration"""
    execution_id = str(uuid.uuid4())
    
    logfire.info(
        "Workflow execution requested",
        execution_id=execution_id,
        mode=request.mode,
        query=request.query[:100] + "..." if len(request.query) > 100 else request.query
    )
    
    # Start background task for workflow execution
    task = asyncio.create_task(
        _execute_workflow_background(execution_id, request)
    )
    
    active_workflows[execution_id] = {
        "task": task,
        "status": "running",
        "progress": {},
        "start_time": datetime.now()
    }
    
    return WorkflowExecutionResponse(
        execution_id=execution_id,
        status="execution_started"
    )

@app.get("/api/v1/agents/{agent_id}/status")
async def get_agent_status(agent_id: str):
    """Get agent generation status"""
    if agent_id not in generation_tasks:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    status = generation_tasks[agent_id]
    result = active_agents.get(agent_id)
    
    return {
        "agent_id": agent_id,
        "status": status,
        "result": result,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/workflows/{execution_id}/status")
async def get_workflow_status(execution_id: str):
    """Get workflow execution status"""
    if execution_id not in active_workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    workflow = active_workflows[execution_id]
    
    return {
        "execution_id": execution_id,
        "status": workflow["status"],
        "progress": workflow["progress"],
        "start_time": workflow["start_time"].isoformat(),
        "duration": (datetime.now() - workflow["start_time"]).total_seconds()
    }

@app.get("/api/v1/workflows/{execution_id}/stream")
async def stream_workflow_progress(execution_id: str):
    """Stream workflow progress in real-time"""
    if execution_id not in active_workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    async def generate():
        workflow = active_workflows[execution_id]
        
        while workflow["status"] == "running":
            progress_data = {
                "execution_id": execution_id,
                "status": workflow["status"],
                "progress": workflow["progress"],
                "timestamp": datetime.now().isoformat()
            }
            
            yield f"data: {json.dumps(progress_data)}\n\n"
            await asyncio.sleep(1)
        
        # Send final result
        final_data = {
            "execution_id": execution_id,
            "status": workflow["status"],
            "progress": workflow["progress"],
            "result": workflow.get("result"),
            "timestamp": datetime.now().isoformat()
        }
        
        yield f"data: {json.dumps(final_data)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

async def _generate_agent_background(agent_id: str, request: AgentGenerationRequest):
    """Background task for agent generation"""
    try:
        logfire.info("Starting agent generation", agent_id=agent_id)
        
        # Get template if specified
        template = None
        if request.template_id:
            template = await template_library.get_template(request.template_id)
        
        # Get required tools
        tools = await tool_library.get_tools(request.tools)
        
        # Generate agent using multi-agent orchestration
        result = await agent_coordinator.generate_agent(
            agent_type=request.agent_type,
            requirements=request.requirements,
            template=template,
            tools=tools,
            dependencies=request.dependencies,
            configuration=request.configuration
        )
        
        # Store result
        active_agents[agent_id] = result
        generation_tasks[agent_id] = "completed"
        
        logfire.info("Agent generation completed", agent_id=agent_id)
        
    except Exception as e:
        generation_tasks[agent_id] = f"failed: {str(e)}"
        logfire.error("Agent generation failed", agent_id=agent_id, error=str(e))

async def _execute_workflow_background(execution_id: str, request: WorkflowExecutionRequest):
    """Background task for workflow execution"""
    try:
        workflow = active_workflows[execution_id]
        
        # Progress callback
        def progress_callback(event_type: str, data: Any):
            workflow["progress"][event_type] = {
                "data": data,
                "timestamp": datetime.now().isoformat()
            }
        
        if request.mode == "grok_heavy":
            from ..grok_heavy.orchestrator import GrokHeavyOrchestrator
            
            orchestrator = GrokHeavyOrchestrator()
            result = await orchestrator.run_grok_heavy_analysis(
                request.query,
                progress_callback=progress_callback
            )
            
            workflow["result"] = result.dict()
        
        elif request.mode == "multi_agent":
            # Multi-agent workflow
            result = await agent_coordinator.execute_multi_agent_workflow(
                request.query,
                progress_callback=progress_callback
            )
            
            workflow["result"] = result
        
        else:
            # Single agent mode
            result = await agent_coordinator.execute_single_agent(
                request.query,
                progress_callback=progress_callback
            )
            
            workflow["result"] = result
        
        workflow["status"] = "completed"
        logfire.info("Workflow execution completed", execution_id=execution_id)
        
    except Exception as e:
        workflow["status"] = "failed"
        workflow["error"] = str(e)
        logfire.error("Workflow execution failed", execution_id=execution_id, error=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
