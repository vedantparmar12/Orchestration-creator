from pydantic_ai import Agent, RunContext
from .base_agent import BaseAgent
from .dependencies import AdvisorDependencies
from .models import ContextOutput
from typing import List, Dict, Any
import asyncio

class AdvisorAgent(BaseAgent[AdvisorDependencies, ContextOutput]):
    """Context and examples provider agent using Pydantic AI"""
    
    def __init__(self, model: str = "openai:gpt-4o", **kwargs):
        super().__init__(
            model=model,
            deps_type=AdvisorDependencies,
            result_type=ContextOutput,
            **kwargs
        )
        
        # Register tools
        self.agent.tool(self.search_vector_knowledge)
        self.agent.tool(self.find_relevant_examples)
        self.agent.tool(self.analyze_context_relevance)
    
    def get_system_prompt(self) -> str:
        return """You are an expert advisor that provides relevant context and examples.
        
        Your role is to:
        1. Search vector knowledge bases for relevant information
        2. Find code examples that match the user's needs
        3. Provide specific, actionable recommendations
        4. Assess confidence in your recommendations
        
        Focus on providing high-quality, relevant context that will help other agents
        make better decisions and generate better solutions."""
    
    async def search_vector_knowledge(
        self,
        ctx: RunContext[AdvisorDependencies],
        query: str,
        limit: int = 5
    ) -> List[str]:
        """Search vector knowledge base for relevant information"""
        try:
            # Use the Supabase vector client from dependencies
            client = ctx.deps.vector_client
            
            # Perform vector similarity search
            # This is a simplified implementation - in practice you'd use embeddings
            response = client.table('documents').select('content').textSearch(
                'content', query, {'type': 'websearch', 'config': {'english': {'tsv': True}}}
            ).limit(limit).execute()
            
            return [doc['content'] for doc in response.data]
        except Exception as e:
            return [f"Error searching knowledge base: {str(e)}"]
    
    async def find_relevant_examples(
        self,
        ctx: RunContext[AdvisorDependencies],
        topic: str
    ) -> List[str]:
        """Find relevant code examples from examples directory"""
        import os
        import glob
        
        examples_path = ctx.deps.examples_path
        examples = []
        
        try:
            # Search for relevant files in examples directory
            pattern = os.path.join(examples_path, "**/*.py")
            for file_path in glob.glob(pattern, recursive=True):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if topic.lower() in content.lower():
                        examples.append(f"File: {file_path}\n{content[:500]}...")
                        if len(examples) >= ctx.deps.context_limit:
                            break
        except Exception as e:
            examples.append(f"Error reading examples: {str(e)}")
        
        return examples
    
    async def analyze_context_relevance(
        self,
        ctx: RunContext[AdvisorDependencies],
        context: str,
        user_query: str
    ) -> float:
        """Analyze how relevant the context is to the user query"""
        # Simple relevance scoring based on keyword overlap
        query_words = set(user_query.lower().split())
        context_words = set(context.lower().split())
        
        if not query_words:
            return 0.0
        
        overlap = len(query_words.intersection(context_words))
        relevance = overlap / len(query_words)
        
        return min(relevance, 1.0)

