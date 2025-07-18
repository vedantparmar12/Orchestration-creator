from pydantic_ai import Agent, RunContext
from .base_agent import BaseAgent
from .dependencies import CoderDependencies
from .models import CodeOutput
from typing import List, Dict, Any
import os
import subprocess
import tempfile

class CoderAgent(BaseAgent[CoderDependencies, CodeOutput]):
    """Code implementation agent using Pydantic AI"""
    
    def __init__(self, model: str = "openai:gpt-4o", **kwargs):
        super().__init__(
            model=model,
            deps_type=CoderDependencies,
            result_type=CodeOutput,
            **kwargs
        )
        
        # Register tools
        self.agent.tool(self.create_file)
        self.agent.tool(self.modify_file)
        self.agent.tool(self.run_tests)
        self.agent.tool(self.validate_syntax)
        self.agent.tool(self.generate_documentation)
    
    def get_system_prompt(self) -> str:
        return """You are an expert code implementation agent.
        
        Your role is to:
        1. Generate high-quality, well-structured code
        2. Follow best practices and coding standards
        3. Implement proper error handling
        4. Write comprehensive tests
        5. Create clear documentation
        
        Focus on creating maintainable, efficient, and well-documented code
        that follows established patterns and conventions."""
    
    async def create_file(
        self,
        ctx: RunContext[CoderDependencies],
        file_path: str,
        content: str
    ) -> str:
        """Create a new file with given content"""
        try:
            full_path = os.path.join(ctx.deps.workspace_path, file_path)
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return f"File created successfully: {file_path}"
        except Exception as e:
            return f"Error creating file {file_path}: {str(e)}"
    
    async def modify_file(
        self,
        ctx: RunContext[CoderDependencies],
        file_path: str,
        modifications: str
    ) -> str:
        """Modify an existing file"""
        try:
            full_path = os.path.join(ctx.deps.workspace_path, file_path)
            
            if not os.path.exists(full_path):
                return f"File not found: {file_path}"
            
            # Read current content
            with open(full_path, 'r', encoding='utf-8') as f:
                current_content = f.read()
            
            # Apply modifications (simplified - in practice would use more sophisticated logic)
            modified_content = f"{current_content}\n\n{modifications}"
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            
            return f"File modified successfully: {file_path}"
        except Exception as e:
            return f"Error modifying file {file_path}: {str(e)}"
    
    async def validate_syntax(
        self,
        ctx: RunContext[CoderDependencies],
        file_path: str
    ) -> str:
        """Validate Python syntax of a file"""
        try:
            full_path = os.path.join(ctx.deps.workspace_path, file_path)
            
            if not os.path.exists(full_path):
                return f"File not found: {file_path}"
            
            # Use Python's compile function to check syntax
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            try:
                compile(content, full_path, 'exec')
                return f"Syntax validation passed: {file_path}"
            except SyntaxError as e:
                return f"Syntax error in {file_path}: {str(e)}"
        except Exception as e:
            return f"Error validating syntax: {str(e)}"
    
    async def run_tests(
        self,
        ctx: RunContext[CoderDependencies],
        test_path: str = None
    ) -> str:
        """Run tests for the code"""
        try:
            # Default to running all tests in the workspace
            if test_path is None:
                test_path = ctx.deps.workspace_path
            else:
                test_path = os.path.join(ctx.deps.workspace_path, test_path)
            
            # Run pytest
            result = subprocess.run(
                ['python', '-m', 'pytest', test_path, '-v'],
                capture_output=True,
                text=True,
                cwd=ctx.deps.workspace_path
            )
            
            if result.returncode == 0:
                return f"All tests passed\n{result.stdout}"
            else:
                return f"Tests failed\n{result.stderr}"
        except Exception as e:
            return f"Error running tests: {str(e)}"
    
    async def generate_documentation(
        self,
        ctx: RunContext[CoderDependencies],
        file_path: str
    ) -> str:
        """Generate documentation for code"""
        try:
            full_path = os.path.join(ctx.deps.workspace_path, file_path)
            
            if not os.path.exists(full_path):
                return f"File not found: {file_path}"
            
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple documentation generation (extract functions and classes)
            lines = content.split('\n')
            documentation = []
            
            for line in lines:
                stripped = line.strip()
                if stripped.startswith('def ') or stripped.startswith('class '):
                    documentation.append(f"- {stripped}")
            
            if documentation:
                return f"Documentation for {file_path}:\n" + '\n'.join(documentation)
            else:
                return f"No functions or classes found in {file_path}"
        except Exception as e:
            return f"Error generating documentation: {str(e)}"
    
    async def analyze_code_quality(
        self,
        ctx: RunContext[CoderDependencies],
        code: str
    ) -> Dict[str, Any]:
        """Analyze code quality metrics"""
        try:
            # Simple quality metrics
            lines = code.split('\n')
            
            metrics = {
                'total_lines': len(lines),
                'non_empty_lines': len([line for line in lines if line.strip()]),
                'comment_lines': len([line for line in lines if line.strip().startswith('#')]),
                'function_count': len([line for line in lines if line.strip().startswith('def ')]),
                'class_count': len([line for line in lines if line.strip().startswith('class ')]),
                'avg_line_length': sum(len(line) for line in lines) / len(lines) if lines else 0
            }
            
            # Calculate comment ratio
            if metrics['non_empty_lines'] > 0:
                metrics['comment_ratio'] = metrics['comment_lines'] / metrics['non_empty_lines']
            else:
                metrics['comment_ratio'] = 0
            
            return metrics
        except Exception as e:
            return {'error': str(e)}
    
    async def suggest_improvements(
        self,
        ctx: RunContext[CoderDependencies],
        code: str
    ) -> List[str]:
        """Suggest code improvements"""
        suggestions = []
        
        # Check for common issues
        if 'TODO' in code:
            suggestions.append("Address TODO comments in the code")
        
        if 'print(' in code:
            suggestions.append("Consider using proper logging instead of print statements")
        
        if 'except:' in code:
            suggestions.append("Use specific exception types instead of bare except clauses")
        
        lines = code.split('\n')
        long_lines = [i for i, line in enumerate(lines) if len(line) > 100]
        if long_lines:
            suggestions.append(f"Consider breaking down long lines (lines {long_lines})")
        
        # Check for docstrings
        if 'def ' in code and '"""' not in code and "'''" not in code:
            suggestions.append("Add docstrings to functions and classes")
        
        return suggestions

