from pydantic import BaseModel, Field
from typing import List, Dict, Any

class PromptRefineOutput(BaseModel):
    """Output from prompt refiner agent"""
    optimized_prompt: str = Field(description="Optimized system prompt")
    improvements_made: List[str] = Field(description="List of improvements applied")
    effectiveness_score: float = Field(ge=0, le=1, description="Predicted effectiveness")
    reasoning: str = Field(description="Reasoning behind optimizations")
    patterns_used: List[str] = Field(description="Patterns applied in optimization")

class ToolsRefineOutput(BaseModel):
    """Output from tools refiner agent"""
    optimized_tools: List[Dict[str, Any]] = Field(description="Optimized tool configurations")
    new_tools_added: List[str] = Field(description="New tools added")
    tools_removed: List[str] = Field(description="Tools removed or deprecated")
    mcp_configurations: Dict[str, Any] = Field(description="MCP server configurations")
    validation_results: Dict[str, bool] = Field(description="Tool validation results")
    performance_improvements: List[str] = Field(description="Performance improvements made")

class AgentRefineOutput(BaseModel):
    """Output from agent refiner agent"""
    optimized_config: Dict[str, Any] = Field(description="Optimized agent configuration")
    performance_improvements: List[str] = Field(description="Performance improvements made")
    behavioral_adjustments: List[str] = Field(description="Behavioral adjustments applied")
    effectiveness_score: float = Field(ge=0, le=1, description="Predicted effectiveness")
    recommendations: List[str] = Field(description="Additional recommendations")
