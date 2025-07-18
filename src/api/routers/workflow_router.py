from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import uuid
import asyncio
from datetime import datetime
from ...grok_heavy.orchestrator import GrokHeavyOrchestrator
from ...orchestration.coordinator import AgentCoordinator
from ...workflow.state_manager import WorkflowStateManager
from ...workflow.router import WorkflowRouter
import logfire

router = APIRouter()

class WorkflowTemplate(BaseModel):
    """Workflow template model"""
    id: str
    name: str
    description: str
    steps: List[Dict[str, Any]]
    configuration: Dict[str, Any]
    estimated_duration: int  # in seconds

class WorkflowExecution(BaseModel):
    """Workflow execution model"""
    execution_id: str
    workflow_type: str
    status: str
    progress: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    start_time: str
    end_time: Optional[str] = None
    duration: Optional[float] = None

class WorkflowMetrics(BaseModel):
    """Workflow metrics model"""
    total_executions: int
    successful_executions: int
    failed_executions: int
    average_duration: float
    success_rate: float

# Global workflow state
workflow_templates = {
    "grok_heavy": WorkflowTemplate(
        id="grok_heavy",
        name="Grok Heavy Analysis",
        description="Deep multi-agent analysis with reflection",
        steps=[
            {"name": "question_generation", "description": "Generate specialized research questions"},
            {"name": "parallel_execution", "description": "Execute 4 agents in parallel"},
            {"name": "synthesis", "description": "Synthesize results"},
            {"name": "deep_reflection", "description": "Deep reflection and insights enhancement"}
        ],
        configuration={"max_agents": 4, "enable_reflection": True},
        estimated_duration=180
    ),
    "multi_agent": WorkflowTemplate(
        id="multi_agent",
        name="Multi-Agent Coordination",
        description="Coordinated multi-agent execution",
        steps=[
            {"name": "task_breakdown", "description": "Break down complex task"},
            {"name": "agent_assignment", "description": "Assign tasks to specialized agents"},
            {"name": "parallel_execution", "description": "Execute agents in parallel"},
            {"name": "result_synthesis", "description": "Synthesize agent results"}
        ],
        configuration={"max_agents": 6, "enable_validation": True},
        estimated_duration=120
    ),
    "single_agent": WorkflowTemplate(
        id="single_agent",
        name="Single Agent Execution",
        description="Simple single agent execution",
        steps=[
            {"name": "task_analysis", "description": "Analyze task requirements"},
            {"name": "agent_execution", "description": "Execute single agent"},
            {"name": "result_processing", "description": "Process and validate results"}
        ],
        configuration={"agent_type": "general", "enable_validation": False},
        estimated_duration=60
    )
}

active_workflows: Dict[str, Dict[str, Any]] = {}
execution_metrics: Dict[str, int] = {
    "total_executions": 0,
    "successful_executions": 0,
    "failed_executions": 0
}

@router.get("/templates", response_model=List[WorkflowTemplate])
async def list_workflow_templates():
    """List available workflow templates"""
    try:
        return list(workflow_templates.values())
    except Exception as e:
        logfire.error("Failed to list workflow templates", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to list templates: {str(e)}")

@router.get("/templates/{template_id}", response_model=WorkflowTemplate)
async def get_workflow_template(template_id: str):
    """Get a specific workflow template"""
    try:
        if template_id not in workflow_templates:
            raise HTTPException(status_code=404, detail="Template not found")
        
        return workflow_templates[template_id]
    except HTTPException:
        raise
    except Exception as e:
        logfire.error("Failed to get workflow template", template_id=template_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get template: {str(e)}")

@router.post("/execute")
async def execute_workflow(
    template_id: str,
    query: str,
    configuration: Dict[str, Any] = {},
    background_tasks: BackgroundTasks = None
):
    """Execute a workflow"""
    try:
        if template_id not in workflow_templates:
            raise HTTPException(status_code=404, detail="Template not found")
        
        execution_id = str(uuid.uuid4())
        template = workflow_templates[template_id]
        
        # Merge configurations
        merged_config = {**template.configuration, **configuration}
        
        # Create execution record
        execution = {
            "execution_id": execution_id,
            "template_id": template_id,
            "workflow_type": template.name,
            "query": query,
            "configuration": merged_config,
            "status": "running",
            "progress": {},
            "start_time": datetime.now().isoformat(),
            "template": template
        }
        
        active_workflows[execution_id] = execution
        execution_metrics["total_executions"] += 1
        
        # Start background execution
        if background_tasks:
            background_tasks.add_task(_execute_workflow_task, execution_id, query, merged_config)
        else:
            asyncio.create_task(_execute_workflow_task(execution_id, query, merged_config))
        
        logfire.info(
            "Workflow execution started",
            execution_id=execution_id,
            template_id=template_id,
            query=query[:100] + "..." if len(query) > 100 else query
        )
        
        return {
            "execution_id": execution_id,
            "status": "started",
            "template": template,
            "estimated_duration": template.estimated_duration
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logfire.error("Failed to execute workflow", template_id=template_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")

@router.get("/executions", response_model=List[WorkflowExecution])
async def list_workflow_executions(
    status: Optional[str] = None,
    template_id: Optional[str] = None,
    limit: int = 50
):
    """List workflow executions"""
    try:
        executions = []
        
        for execution_id, execution_data in active_workflows.items():
            if status and execution_data["status"] != status:
                continue
            
            if template_id and execution_data["template_id"] != template_id:
                continue
            
            duration = None
            if execution_data.get("end_time"):
                start = datetime.fromisoformat(execution_data["start_time"])
                end = datetime.fromisoformat(execution_data["end_time"])
                duration = (end - start).total_seconds()
            
            executions.append(WorkflowExecution(
                execution_id=execution_id,
                workflow_type=execution_data["workflow_type"],
                status=execution_data["status"],
                progress=execution_data["progress"],
                result=execution_data.get("result"),
                error=execution_data.get("error"),
                start_time=execution_data["start_time"],
                end_time=execution_data.get("end_time"),
                duration=duration
            ))
        
        # Sort by start time descending
        executions.sort(key=lambda x: x.start_time, reverse=True)
        
        return executions[:limit]
        
    except Exception as e:
        logfire.error("Failed to list workflow executions", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to list executions: {str(e)}")

@router.get("/executions/{execution_id}", response_model=WorkflowExecution)
async def get_workflow_execution(execution_id: str):
    """Get a specific workflow execution"""
    try:
        if execution_id not in active_workflows:
            raise HTTPException(status_code=404, detail="Execution not found")
        
        execution_data = active_workflows[execution_id]
        
        duration = None
        if execution_data.get("end_time"):
            start = datetime.fromisoformat(execution_data["start_time"])
            end = datetime.fromisoformat(execution_data["end_time"])
            duration = (end - start).total_seconds()
        
        return WorkflowExecution(
            execution_id=execution_id,
            workflow_type=execution_data["workflow_type"],
            status=execution_data["status"],
            progress=execution_data["progress"],
            result=execution_data.get("result"),
            error=execution_data.get("error"),
            start_time=execution_data["start_time"],
            end_time=execution_data.get("end_time"),
            duration=duration
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logfire.error("Failed to get workflow execution", execution_id=execution_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get execution: {str(e)}")

@router.post("/executions/{execution_id}/cancel")
async def cancel_workflow_execution(execution_id: str):
    """Cancel a workflow execution"""
    try:
        if execution_id not in active_workflows:
            raise HTTPException(status_code=404, detail="Execution not found")
        
        execution_data = active_workflows[execution_id]
        
        if execution_data["status"] not in ["running", "started"]:
            raise HTTPException(status_code=400, detail="Execution cannot be cancelled")
        
        # Cancel the execution
        execution_data["status"] = "cancelled"
        execution_data["end_time"] = datetime.now().isoformat()
        execution_data["error"] = "Cancelled by user"
        
        # Cancel background task if it exists
        if "task" in execution_data and not execution_data["task"].done():
            execution_data["task"].cancel()
        
        logfire.info("Workflow execution cancelled", execution_id=execution_id)
        
        return {
            "execution_id": execution_id,
            "status": "cancelled",
            "message": "Execution cancelled successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logfire.error("Failed to cancel workflow execution", execution_id=execution_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Cancellation failed: {str(e)}")

@router.get("/metrics", response_model=WorkflowMetrics)
async def get_workflow_metrics():
    """Get workflow execution metrics"""
    try:
        total = execution_metrics["total_executions"]
        successful = execution_metrics["successful_executions"]
        failed = execution_metrics["failed_executions"]
        
        # Calculate average duration
        durations = []
        for execution_data in active_workflows.values():
            if execution_data.get("end_time"):
                start = datetime.fromisoformat(execution_data["start_time"])
                end = datetime.fromisoformat(execution_data["end_time"])
                duration = (end - start).total_seconds()
                durations.append(duration)
        
        average_duration = sum(durations) / len(durations) if durations else 0
        success_rate = (successful / total) if total > 0 else 0
        
        return WorkflowMetrics(
            total_executions=total,
            successful_executions=successful,
            failed_executions=failed,
            average_duration=average_duration,
            success_rate=success_rate
        )
        
    except Exception as e:
        logfire.error("Failed to get workflow metrics", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")

@router.get("/stats")
async def get_workflow_stats():
    """Get detailed workflow statistics"""
    try:
        stats = {
            "total_executions": execution_metrics["total_executions"],
            "successful_executions": execution_metrics["successful_executions"],
            "failed_executions": execution_metrics["failed_executions"],
            "active_executions": len([e for e in active_workflows.values() if e["status"] == "running"]),
            "template_usage": {},
            "status_distribution": {}
        }
        
        # Calculate template usage
        for execution_data in active_workflows.values():
            template_id = execution_data["template_id"]
            stats["template_usage"][template_id] = stats["template_usage"].get(template_id, 0) + 1
        
        # Calculate status distribution
        for execution_data in active_workflows.values():
            status = execution_data["status"]
            stats["status_distribution"][status] = stats["status_distribution"].get(status, 0) + 1
        
        return stats
        
    except Exception as e:
        logfire.error("Failed to get workflow stats", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@router.delete("/executions/{execution_id}")
async def delete_workflow_execution(execution_id: str):
    """Delete a workflow execution"""
    try:
        if execution_id not in active_workflows:
            raise HTTPException(status_code=404, detail="Execution not found")
        
        execution_data = active_workflows[execution_id]
        
        # Can only delete completed/failed/cancelled executions
        if execution_data["status"] == "running":
            raise HTTPException(status_code=400, detail="Cannot delete running execution")
        
        del active_workflows[execution_id]
        
        logfire.info("Workflow execution deleted", execution_id=execution_id)
        
        return {
            "execution_id": execution_id,
            "message": "Execution deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logfire.error("Failed to delete workflow execution", execution_id=execution_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")

async def _execute_workflow_task(execution_id: str, query: str, configuration: Dict[str, Any]):
    """Background task for workflow execution"""
    try:
        execution_data = active_workflows[execution_id]
        template_id = execution_data["template_id"]
        
        # Progress callback
        def progress_callback(event_type: str, data: Any):
            execution_data["progress"][event_type] = {
                "data": data,
                "timestamp": datetime.now().isoformat()
            }
        
        # Execute based on template
        if template_id == "grok_heavy":
            orchestrator = GrokHeavyOrchestrator()
            result = await orchestrator.run_grok_heavy_analysis(
                query,
                progress_callback=progress_callback
            )
            execution_data["result"] = result.dict()
        
        elif template_id == "multi_agent":
            coordinator = AgentCoordinator()
            result = await coordinator.execute_multi_agent_workflow(
                query,
                progress_callback=progress_callback
            )
            execution_data["result"] = result
        
        elif template_id == "single_agent":
            coordinator = AgentCoordinator()
            result = await coordinator.execute_single_agent(
                query,
                progress_callback=progress_callback
            )
            execution_data["result"] = result
        
        # Update execution status
        execution_data["status"] = "completed"
        execution_data["end_time"] = datetime.now().isoformat()
        execution_metrics["successful_executions"] += 1
        
        logfire.info("Workflow execution completed", execution_id=execution_id)
        
    except asyncio.CancelledError:
        execution_data["status"] = "cancelled"
        execution_data["end_time"] = datetime.now().isoformat()
        execution_data["error"] = "Execution was cancelled"
        logfire.info("Workflow execution cancelled", execution_id=execution_id)
    
    except Exception as e:
        execution_data["status"] = "failed"
        execution_data["end_time"] = datetime.now().isoformat()
        execution_data["error"] = str(e)
        execution_metrics["failed_executions"] += 1
        logfire.error("Workflow execution failed", execution_id=execution_id, error=str(e))
