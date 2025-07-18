from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import json
import os
from pathlib import Path

class AgentTemplate(BaseModel):
    """Agent template definition"""
    id: str
    name: str
    description: str
    category: str
    system_prompt: str
    required_dependencies: List[str]
    recommended_tools: List[str]
    output_schema: Dict[str, Any]
    configuration: Dict[str, Any]
    example_usage: str
    tags: List[str]

class AgentTemplateLibrary:
    """Agent templates library for rapid development"""
    
    def __init__(self, templates_path: str = "src/library/templates"):
        self.templates_path = Path(templates_path)
        self.templates_path.mkdir(exist_ok=True)
        self._templates_cache: Dict[str, AgentTemplate] = {}
        self._load_templates()
    
    def _load_templates(self):
        """Load all agent templates"""
        template_categories = [
            'coding_agents', 'research_agents', 'analysis_agents',
            'automation_agents', 'testing_agents', 'devops_agents',
            'data_agents', 'content_agents', 'support_agents'
        ]
        
        for category in template_categories:
            category_path = self.templates_path / category
            if os.path.exists(category_path):
                self._load_category_templates(category, category_path)
    
    def _load_category_templates(self, category: str, path: Path):
        """Load templates from a specific category"""
        for file_name in os.listdir(path):
            if file_name.endswith('.json'):
                template_path = path / file_name
                with open(template_path, 'r') as f:
                    template_data = json.load(f)
                    template = AgentTemplate(**template_data, category=category)
                    self._templates_cache[template.id] = template
    
    async def get_template(self, template_id: str) -> Optional[AgentTemplate]:
        """Get a specific template by ID"""
        return self._templates_cache.get(template_id)
    
    async def list_templates(self, category: Optional[str] = None) -> List[AgentTemplate]:
        """List all available templates, optionally filtered by category"""
        templates = list(self._templates_cache.values())
        if category:
            templates = [t for t in templates if t.category == category]
        return templates
    
    async def search_templates(self, query: str) -> List[AgentTemplate]:
        """Search templates by description or tags"""
        results = []
        query_lower = query.lower()
        
        for template in self._templates_cache.values():
            if (query_lower in template.description.lower() or 
                any(query_lower in tag.lower() for tag in template.tags)):
                results.append(template)
        
        return results

# Global agent template library instance
template_library = AgentTemplateLibrary()
