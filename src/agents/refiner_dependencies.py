from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from .dependencies import BaseDependencies

@dataclass
class PromptRefinerDependencies(BaseDependencies):
    """Dependencies for prompt refiner agent"""
    prompt_patterns: List[Dict[str, str]]
    evaluation_metrics: List[str]
    optimization_targets: List[str] = None

@dataclass
class ToolsRefinerDependencies(BaseDependencies):
    """Dependencies for tools refiner agent"""
    mcp_servers: List[Dict[str, Any]]
    tool_library: Dict[str, Any]
    validation_endpoints: List[str] = None

@dataclass
class AgentRefinerDependencies(BaseDependencies):
    """Dependencies for agent refiner agent"""
    agent_templates: Dict[str, Any]
    performance_metrics: Dict[str, float]
    optimization_rules: List[str] = None
