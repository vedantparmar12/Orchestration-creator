from typing import List, Dict, Any
from pydantic_ai import RunContext
from .base_agent import BaseAgent
from .dependencies import SynthesisDependencies
from .models import FinalOutput, ValidationResult

class SynthesisAgent(BaseAgent[SynthesisDependencies, FinalOutput]):
    """Result synthesis agent that combines outputs from multiple agents"""
    
    def __init__(self, model: str = "openai:gpt-4o", **kwargs):
        super().__init__(
            model=model,
            deps_type=SynthesisDependencies,
            result_type=FinalOutput,
            **kwargs
        )
        
        # Register tools
        self.agent.tool(self.combine_outputs)
        self.agent.tool(self.assess_overall_confidence)
        self.agent.tool(self.create_implementation_plan)
        self.agent.tool(self.calculate_success_metrics)
    
    def get_system_prompt(self) -> str:
        return """You are an expert synthesis agent that combines multiple agent outputs into comprehensive solutions.
        
        Your role is to:
        1. Intelligently combine outputs from different specialized agents
        2. Create coherent implementation plans
        3. Assess overall confidence in the solution
        4. Generate success metrics and validation summaries
        5. Ensure the final output is actionable and complete
        
        Focus on creating synthesis that is greater than the sum of its parts."""
    
    async def combine_outputs(
        self,
        ctx: RunContext[SynthesisDependencies],
        agent_outputs: Dict[str, Any]
    ) -> str:
        """Combine outputs from multiple agents into a coherent solution"""
        combined_solution = []
        
        # Process advisor output
        if 'advisor' in agent_outputs:
            advisor_output = agent_outputs['advisor']
            if hasattr(advisor_output, 'context_summary'):
                combined_solution.append(f"**Context Analysis:** {advisor_output.context_summary}")
                combined_solution.append(f"**Recommendations:** {', '.join(advisor_output.recommendations)}")
        
        # Process scope output  
        if 'scope_reasoner' in agent_outputs:
            scope_output = agent_outputs['scope_reasoner']
            if hasattr(scope_output, 'task_breakdown'):
                combined_solution.append(f"**Task Breakdown:** {', '.join(scope_output.task_breakdown)}")
                combined_solution.append(f"**Estimated Effort:** {scope_output.estimated_effort}")
        
        # Process coder output
        if 'coder' in agent_outputs:
            coder_output = agent_outputs['coder']
            if hasattr(coder_output, 'generated_code'):
                combined_solution.append(f"**Generated Code:** {coder_output.generated_code}")
                combined_solution.append(f"**Next Steps:** {', '.join(coder_output.next_steps)}")
        
        # Process refiner output
        if 'refiner' in agent_outputs:
            refiner_output = agent_outputs['refiner']
            if hasattr(refiner_output, 'refined_code'):
                combined_solution.append(f"**Refined Code:** {refiner_output.refined_code}")
                combined_solution.append(f"**Improvements Made:** {', '.join(refiner_output.improvements_made)}")
        
        return "\\n\\n".join(combined_solution)
    
    async def assess_overall_confidence(
        self,
        ctx: RunContext[SynthesisDependencies],
        agent_outputs: Dict[str, Any]
    ) -> float:
        """Assess overall confidence in the synthesized solution"""
        confidence_scores = []
        
        # Extract confidence scores from individual agents
        for agent_name, output in agent_outputs.items():
            if hasattr(output, 'confidence_score'):
                confidence_scores.append(output.confidence_score)
            elif hasattr(output, 'confidence_level'):
                confidence_scores.append(output.confidence_level)
        
        # Calculate weighted average (with refinement having higher weight)
        if confidence_scores:
            if ctx.deps.confidence_weighting:
                # Give more weight to refiner output if present
                weights = [1.5 if 'refiner' in agent_outputs else 1.0 for _ in confidence_scores]
                weighted_sum = sum(score * weight for score, weight in zip(confidence_scores, weights))
                total_weight = sum(weights)
                return weighted_sum / total_weight
            else:
                return sum(confidence_scores) / len(confidence_scores)
        
        return 0.7  # Default confidence level
    
    async def create_implementation_plan(
        self,
        ctx: RunContext[SynthesisDependencies],
        agent_outputs: Dict[str, Any]
    ) -> List[str]:
        """Create comprehensive implementation plan"""
        plan = []
        
        # Extract task breakdown from scope reasoner
        if 'scope_reasoner' in agent_outputs:
            scope_output = agent_outputs['scope_reasoner']
            if hasattr(scope_output, 'task_breakdown'):
                plan.extend(scope_output.task_breakdown)
        
        # Add implementation steps from coder
        if 'coder' in agent_outputs:
            coder_output = agent_outputs['coder']
            if hasattr(coder_output, 'next_steps'):
                plan.extend(coder_output.next_steps)
        
        # Add refinement steps if applicable
        if 'refiner' in agent_outputs:
            refiner_output = agent_outputs['refiner']
            if hasattr(refiner_output, 'remaining_issues') and refiner_output.remaining_issues:
                plan.append(f"Address remaining issues: {', '.join(refiner_output.remaining_issues)}")
        
        # Add default plan if no specific steps found
        if not plan:
            plan = [
                "1. Review and understand requirements",
                "2. Set up development environment",
                "3. Implement core functionality",
                "4. Add error handling and validation",
                "5. Write comprehensive tests",
                "6. Create documentation",
                "7. Review and refine code"
            ]
        
        return plan
    
    async def calculate_success_metrics(
        self,
        ctx: RunContext[SynthesisDependencies],
        agent_outputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate success metrics for the solution"""
        metrics = {
            'agents_involved': len(agent_outputs),
            'validation_passed': True,
            'code_quality_score': 0.8,
            'completeness_score': 0.9,
            'estimated_implementation_time': 'Not specified'
        }
        
        # Check validation results
        validation_results = []
        for output in agent_outputs.values():
            if hasattr(output, 'validation_results'):
                validation_results.append(output.validation_results)
        
        if validation_results:
            all_passed = all(
                result.test_passed and result.lint_passed and result.type_check_passed
                for result in validation_results
            )
            metrics['validation_passed'] = all_passed
        
        # Extract effort estimates
        if 'scope_reasoner' in agent_outputs:
            scope_output = agent_outputs['scope_reasoner']
            if hasattr(scope_output, 'estimated_effort'):
                metrics['estimated_implementation_time'] = scope_output.estimated_effort
        
        return metrics
    
    async def synthesize_final_output(
        self,
        agent_outputs: Dict[str, Any],
        deps: SynthesisDependencies
    ) -> FinalOutput:
        """Main synthesis method that combines all agent outputs"""
        # Combine all outputs
        solution = await self.combine_outputs(
            RunContext(deps=deps),
            agent_outputs
        )
        
        # Create implementation plan
        implementation_plan = await self.create_implementation_plan(
            RunContext(deps=deps),
            agent_outputs
        )
        
        # Assess confidence
        confidence_score = await self.assess_overall_confidence(
            RunContext(deps=deps),
            agent_outputs
        )
        
        # Calculate success metrics
        success_metrics = await self.calculate_success_metrics(
            RunContext(deps=deps),
            agent_outputs
        )
        
        # Extract code artifacts
        code_artifacts = {}
        for agent_name, output in agent_outputs.items():
            if hasattr(output, 'generated_code'):
                code_artifacts[f"{agent_name}_code"] = output.generated_code
            elif hasattr(output, 'refined_code'):
                code_artifacts[f"{agent_name}_refined"] = output.refined_code
        
        # Create validation summary
        validation_summary = ValidationResult(
            test_passed=success_metrics['validation_passed'],
            lint_passed=success_metrics['validation_passed'],
            type_check_passed=success_metrics['validation_passed'],
            errors=[],
            warnings=[]
        )
        
        return FinalOutput(
            solution=solution,
            implementation_plan=implementation_plan,
            code_artifacts=code_artifacts,
            validation_summary=validation_summary,
            confidence_score=confidence_score,
            success_metrics=success_metrics
        )
