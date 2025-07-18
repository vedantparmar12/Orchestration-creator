from dataclasses import dataclass
from typing import Optional, Dict, Any, List
import httpx
from supabase import Client as SupabaseClient

@dataclass
class BaseDependencies:
    """Base dependencies for all agents"""
    user_id: str
    session_id: str
    api_keys: Dict[str, str]
    http_client: httpx.AsyncClient

@dataclass
class AdvisorDependencies(BaseDependencies):
    """Dependencies for advisor agent"""
    vector_client: SupabaseClient
    examples_path: str
    context_limit: int = 5

@dataclass
class CoderDependencies(BaseDependencies):
    """Dependencies for coder agent"""
    workspace_path: str
    git_repo: Optional[str] = None
    tool_configs: Dict[str, Any] = None

@dataclass
class RefinerDependencies(BaseDependencies):
    """Dependencies for refiner agent"""
    validation_config: Dict[str, bool]
    max_retry_attempts: int = 3

@dataclass
class PromptRefinerDependencies(BaseDependencies):
    """Dependencies for prompt refiner agent"""
    prompt_patterns: List[str]
    evaluation_metrics: List[str]
    optimization_targets: Dict[str, Any] = None

@dataclass
class ToolsRefinerDependencies(BaseDependencies):
    """Dependencies for tools refiner agent"""
    mcp_servers: List[str]
    tool_library: Dict[str, Any]
    validation_tools: List[str] = None

@dataclass
class AgentRefinerDependencies(BaseDependencies):
    """Dependencies for agent refiner agent"""
    agent_templates: Dict[str, Any]
    performance_metrics: Dict[str, float]
    optimization_config: Dict[str, Any] = None

@dataclass
class ResearchDependencies(BaseDependencies):
    """Dependencies for research agent"""
    search_tools: List[str]
    fact_checking_apis: List[str]
    source_validation: bool = True

@dataclass
class AnalysisDependencies(BaseDependencies):
    """Dependencies for analysis agent"""
    analysis_tools: List[str]
    metrics_calculation: bool = True
    impact_assessment: bool = True

@dataclass
class PerspectiveDependencies(BaseDependencies):
    """Dependencies for perspective agent"""
    viewpoint_sources: List[str]
    stakeholder_analysis: bool = True
    bias_detection: bool = True

@dataclass
class VerificationDependencies(BaseDependencies):
    """Dependencies for verification agent"""
    fact_check_sources: List[str]
    credibility_scoring: bool = True
    cross_reference_tools: List[str] = None

@dataclass
class SynthesisDependencies(BaseDependencies):
    """Dependencies for synthesis agent"""
    synthesis_strategy: str = "comprehensive"
    confidence_weighting: bool = True
    output_format: str = "detailed"
