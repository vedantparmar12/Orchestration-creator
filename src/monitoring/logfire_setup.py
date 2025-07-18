import logfire
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import os

class LogfireMonitoring:
    """Pydantic Logfire integration for monitoring and debugging"""
    
    def __init__(self, project_name: str = "enhanced-agentic-workflow"):
        self.project_name = project_name
        self.enabled = os.getenv("LOGFIRE_ENABLED", "true").lower() == "true"
        
        if self.enabled:
            # Configure Logfire
            logfire.configure(
                project_name=project_name,
                service_name="agent-creator",
                service_version="1.0.0"
            )
            
            # Initialize with startup event
            logfire.info(
                "Agent Creator system started",
                project=project_name,
                timestamp=datetime.now().isoformat()
            )
    
    def log_agent_execution(
        self,
        agent_name: str,
        user_input: str,
        result: Any,
        execution_time: float,
        success: bool,
        error: Optional[str] = None
    ):
        """Log agent execution details"""
        if not self.enabled:
            return
        
        log_data = {
            "agent_name": agent_name,
            "user_input": user_input[:200] + "..." if len(user_input) > 200 else user_input,
            "execution_time": execution_time,
            "success": success,
            "timestamp": datetime.now().isoformat()
        }
        
        if error:
            log_data["error"] = error
            logfire.error(
                f"Agent {agent_name} execution failed",
                **log_data
            )
        else:
            log_data["result_type"] = type(result).__name__
            logfire.info(
                f"Agent {agent_name} executed successfully",
                **log_data
            )
    
    def log_validation_results(
        self,
        agent_name: str,
        validation_results: Dict[str, Any],
        passed: bool
    ):
        """Log validation results"""
        if not self.enabled:
            return
        
        log_data = {
            "agent_name": agent_name,
            "validation_passed": passed,
            "test_passed": validation_results.get("test_passed", False),
            "lint_passed": validation_results.get("lint_passed", False),
            "type_check_passed": validation_results.get("type_check_passed", False),
            "error_count": len(validation_results.get("errors", [])),
            "warning_count": len(validation_results.get("warnings", [])),
            "timestamp": datetime.now().isoformat()
        }
        
        if passed:
            logfire.info(
                f"Validation passed for {agent_name}",
                **log_data
            )
        else:
            log_data["errors"] = validation_results.get("errors", [])
            logfire.warning(
                f"Validation failed for {agent_name}",
                **log_data
            )
    
    def log_multi_agent_coordination(
        self,
        agents_involved: List[str],
        coordination_time: float,
        success_rate: float,
        final_result: Any
    ):
        """Log multi-agent coordination results"""
        if not self.enabled:
            return
        
        log_data = {
            "agents_involved": agents_involved,
            "agent_count": len(agents_involved),
            "coordination_time": coordination_time,
            "success_rate": success_rate,
            "final_result_type": type(final_result).__name__,
            "timestamp": datetime.now().isoformat()
        }
        
        logfire.info(
            "Multi-agent coordination completed",
            **log_data
        )
    
    def log_self_correction_cycle(
        self,
        agent_name: str,
        cycle_number: int,
        improvements_made: List[str],
        validation_passed: bool,
        cycle_complete: bool
    ):
        """Log self-correction cycle details"""
        if not self.enabled:
            return
        
        log_data = {
            "agent_name": agent_name,
            "cycle_number": cycle_number,
            "improvements_count": len(improvements_made),
            "improvements_made": improvements_made,
            "validation_passed": validation_passed,
            "cycle_complete": cycle_complete,
            "timestamp": datetime.now().isoformat()
        }
        
        logfire.info(
            f"Self-correction cycle {cycle_number} for {agent_name}",
            **log_data
        )
    
    def log_tool_execution(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        result: Any,
        execution_time: float,
        success: bool,
        error: Optional[str] = None
    ):
        """Log tool execution details"""
        if not self.enabled:
            return
        
        log_data = {
            "tool_name": tool_name,
            "parameter_count": len(parameters),
            "execution_time": execution_time,
            "success": success,
            "timestamp": datetime.now().isoformat()
        }
        
        if error:
            log_data["error"] = error
            logfire.error(
                f"Tool {tool_name} execution failed",
                **log_data
            )
        else:
            log_data["result_type"] = type(result).__name__
            logfire.info(
                f"Tool {tool_name} executed successfully",
                **log_data
            )
    
    def log_performance_metrics(
        self,
        agent_name: str,
        metrics: Dict[str, Any]
    ):
        """Log performance metrics"""
        if not self.enabled:
            return
        
        log_data = {
            "agent_name": agent_name,
            "timestamp": datetime.now().isoformat(),
            **metrics
        }
        
        logfire.info(
            f"Performance metrics for {agent_name}",
            **log_data
        )
    
    def log_error(
        self,
        error_type: str,
        error_message: str,
        context: Dict[str, Any] = None
    ):
        """Log error details"""
        if not self.enabled:
            return
        
        log_data = {
            "error_type": error_type,
            "error_message": error_message,
            "timestamp": datetime.now().isoformat()
        }
        
        if context:
            log_data.update(context)
        
        logfire.error(
            f"Error occurred: {error_type}",
            **log_data
        )
    
    def log_user_interaction(
        self,
        user_input: str,
        response_type: str,
        processing_time: float,
        success: bool
    ):
        """Log user interaction details"""
        if not self.enabled:
            return
        
        log_data = {
            "user_input_length": len(user_input),
            "response_type": response_type,
            "processing_time": processing_time,
            "success": success,
            "timestamp": datetime.now().isoformat()
        }
        
        logfire.info(
            "User interaction processed",
            **log_data
        )
    
    def log_mcp_interaction(
        self,
        server_name: str,
        tool_name: str,
        success: bool,
        response_time: float,
        error: Optional[str] = None
    ):
        """Log MCP server interaction"""
        if not self.enabled:
            return
        
        log_data = {
            "server_name": server_name,
            "tool_name": tool_name,
            "success": success,
            "response_time": response_time,
            "timestamp": datetime.now().isoformat()
        }
        
        if error:
            log_data["error"] = error
            logfire.error(
                f"MCP interaction failed: {server_name}/{tool_name}",
                **log_data
            )
        else:
            logfire.info(
                f"MCP interaction successful: {server_name}/{tool_name}",
                **log_data
            )
    
    def create_span(self, operation_name: str, **kwargs):
        """Create a Logfire span for tracking operations"""
        if not self.enabled:
            return logfire.no_auto_trace()
        
        return logfire.span(operation_name, **kwargs)
    
    def get_monitoring_stats(self) -> Dict[str, Any]:
        """Get monitoring statistics"""
        if not self.enabled:
            return {"enabled": False}
        
        return {
            "enabled": True,
            "project_name": self.project_name,
            "service_name": "agent-creator",
            "service_version": "1.0.0",
            "timestamp": datetime.now().isoformat()
        }
    
    def shutdown(self):
        """Shutdown monitoring"""
        if self.enabled:
            logfire.info(
                "Agent Creator system shutting down",
                project=self.project_name,
                timestamp=datetime.now().isoformat()
            )

# Global monitoring instance
monitoring = LogfireMonitoring()

# Convenience functions for easy access
def log_agent_execution(agent_name: str, user_input: str, result: Any, 
                       execution_time: float, success: bool, error: Optional[str] = None):
    """Convenience function for logging agent execution"""
    monitoring.log_agent_execution(agent_name, user_input, result, execution_time, success, error)

def log_validation_results(agent_name: str, validation_results: Dict[str, Any], passed: bool):
    """Convenience function for logging validation results"""
    monitoring.log_validation_results(agent_name, validation_results, passed)

def log_error(error_type: str, error_message: str, context: Dict[str, Any] = None):
    """Convenience function for logging errors"""
    monitoring.log_error(error_type, error_message, context)

def create_span(operation_name: str, **kwargs):
    """Convenience function for creating spans"""
    return monitoring.create_span(operation_name, **kwargs)
