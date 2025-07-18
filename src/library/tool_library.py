from typing import Dict, List, Any, Optional, Callable
from pydantic import BaseModel, Field
import json
import os
from pathlib import Path
import importlib.util
import inspect

class ToolDefinition(BaseModel):
    """Standard tool definition"""
    name: str
    description: str
    parameters: Dict[str, Any]
    implementation: str
    category: str
    tags: List[str]
    mcp_compatible: bool = False
    dependencies: List[str] = []
    version: str = "1.0.0"
    author: str = "Agent Creator"
    example_usage: Optional[str] = None

class ToolCategory(BaseModel):
    """Tool category definition"""
    name: str
    description: str
    icon: str
    tools: List[ToolDefinition] = []

class ToolLibrary:
    """Comprehensive prebuilt tools collection"""
    
    def __init__(self, library_path: str = "src/library/tools"):
        self.library_path = Path(library_path)
        self.library_path.mkdir(exist_ok=True)
        self._tools_cache: Dict[str, ToolDefinition] = {}
        self._categories: Dict[str, ToolCategory] = {}
        self._load_tools()
    
    def _load_tools(self):
        """Load all tools from library directory"""
        categories = [
            ('web_scraping', 'Web Scraping & Data Extraction', '🕷️'),
            ('file_operations', 'File Operations & Management', '📁'),
            ('api_clients', 'API Clients & Integration', '🔌'),
            ('data_processing', 'Data Processing & Analysis', '📊'),
            ('testing', 'Testing & Quality Assurance', '🧪'),
            ('deployment', 'Deployment & DevOps', '🚀'),
            ('monitoring', 'Monitoring & Logging', '📈'),
            ('security', 'Security & Authentication', '🔐'),
            ('ai_ml', 'AI & Machine Learning', '🤖'),
            ('database', 'Database Operations', '🗄️'),
            ('messaging', 'Messaging & Communication', '💬'),
            ('utilities', 'Utilities & Helpers', '🛠️')
        ]
        
        for category_name, description, icon in categories:
            category = ToolCategory(
                name=category_name,
                description=description,
                icon=icon
            )
            self._categories[category_name] = category
            self._load_category_tools(category_name)
    
    def _load_category_tools(self, category: str):
        """Load tools from a specific category"""
        category_path = self.library_path / category
        category_path.mkdir(exist_ok=True)
        
        # Load JSON tool definitions
        for json_file in category_path.glob("*.json"):
            try:
                with open(json_file, 'r') as f:
                    tool_data = json.load(f)
                    tool = ToolDefinition(**tool_data, category=category)
                    self._tools_cache[tool.name] = tool
                    self._categories[category].tools.append(tool)
            except Exception as e:
                print(f"Error loading tool from {json_file}: {e}")
        
        # Load Python tool implementations
        for py_file in category_path.glob("*.py"):
            try:
                self._load_python_tool(py_file, category)
            except Exception as e:
                print(f"Error loading Python tool from {py_file}: {e}")
    
    def _load_python_tool(self, file_path: Path, category: str):
        """Load a Python tool implementation"""
        spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Look for tool functions (functions with @tool decorator or specific naming)
        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj) and (name.startswith('tool_') or hasattr(obj, '_is_tool')):
                tool_def = self._extract_tool_definition(obj, category)
                if tool_def:
                    self._tools_cache[tool_def.name] = tool_def
                    self._categories[category].tools.append(tool_def)
    
    def _extract_tool_definition(self, func: Callable, category: str) -> Optional[ToolDefinition]:
        """Extract tool definition from a function"""
        try:
            sig = inspect.signature(func)
            parameters = {}
            
            for param_name, param in sig.parameters.items():
                if param_name != 'self':
                    parameters[param_name] = {
                        'type': str(param.annotation) if param.annotation != inspect.Parameter.empty else 'Any',
                        'default': param.default if param.default != inspect.Parameter.empty else None
                    }
            
            return ToolDefinition(
                name=func.__name__,
                description=func.__doc__ or "No description available",
                parameters=parameters,
                implementation=inspect.getsource(func),
                category=category,
                tags=getattr(func, '_tags', []),
                mcp_compatible=getattr(func, '_mcp_compatible', False),
                dependencies=getattr(func, '_dependencies', [])
            )
        except Exception as e:
            print(f"Error extracting tool definition: {e}")
            return None
    
    async def get_tools(self, tool_names: List[str]) -> List[ToolDefinition]:
        """Get specific tools by name"""
        return [self._tools_cache[name] for name in tool_names if name in self._tools_cache]
    
    async def list_tools(self, category: Optional[str] = None) -> List[ToolDefinition]:
        """List all available tools, optionally filtered by category"""
        if category:
            return self._categories.get(category, ToolCategory(name=category, description="", icon="")).tools
        return list(self._tools_cache.values())
    
    async def get_categories(self) -> List[ToolCategory]:
        """Get all tool categories"""
        return list(self._categories.values())
    
    async def search_tools(self, query: str, limit: int = 10) -> List[ToolDefinition]:
        """Search tools by description or tags"""
        results = []
        query_lower = query.lower()
        
        for tool in self._tools_cache.values():
            score = 0
            
            # Search in name
            if query_lower in tool.name.lower():
                score += 10
            
            # Search in description
            if query_lower in tool.description.lower():
                score += 5
            
            # Search in tags
            for tag in tool.tags:
                if query_lower in tag.lower():
                    score += 3
            
            # Search in category
            if query_lower in tool.category.lower():
                score += 2
            
            if score > 0:
                results.append((tool, score))
        
        # Sort by score and return top results
        results.sort(key=lambda x: x[1], reverse=True)
        return [tool for tool, _ in results[:limit]]
    
    async def get_recommended_tools(self, requirements: str) -> List[ToolDefinition]:
        """Get recommended tools based on requirements"""
        # Use AI-based recommendation or simple keyword matching
        keywords = requirements.lower().split()
        
        recommendations = []
        for tool in self._tools_cache.values():
            relevance_score = 0
            
            for keyword in keywords:
                if keyword in tool.description.lower():
                    relevance_score += 1
                if keyword in ' '.join(tool.tags).lower():
                    relevance_score += 1
            
            if relevance_score > 0:
                recommendations.append((tool, relevance_score))
        
        # Sort by relevance and return top 10
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return [tool for tool, _ in recommendations[:10]]
    
    async def add_tool(self, tool: ToolDefinition) -> bool:
        """Add a new tool to the library"""
        try:
            # Add to cache
            self._tools_cache[tool.name] = tool
            
            # Add to category
            if tool.category not in self._categories:
                self._categories[tool.category] = ToolCategory(
                    name=tool.category,
                    description=f"Tools for {tool.category}",
                    icon="🔧"
                )
            
            self._categories[tool.category].tools.append(tool)
            
            # Save to file
            category_path = self.library_path / tool.category
            category_path.mkdir(exist_ok=True)
            
            tool_file = category_path / f"{tool.name}.json"
            with open(tool_file, 'w') as f:
                json.dump(tool.model_dump(), f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error adding tool: {e}")
            return False
    
    async def remove_tool(self, tool_name: str) -> bool:
        """Remove a tool from the library"""
        try:
            if tool_name in self._tools_cache:
                tool = self._tools_cache[tool_name]
                
                # Remove from cache
                del self._tools_cache[tool_name]
                
                # Remove from category
                if tool.category in self._categories:
                    self._categories[tool.category].tools = [
                        t for t in self._categories[tool.category].tools 
                        if t.name != tool_name
                    ]
                
                # Remove file
                tool_file = self.library_path / tool.category / f"{tool_name}.json"
                if tool_file.exists():
                    tool_file.unlink()
                
                return True
            return False
        except Exception as e:
            print(f"Error removing tool: {e}")
            return False
    
    async def get_tool_usage_examples(self, tool_name: str) -> Optional[str]:
        """Get usage examples for a specific tool"""
        if tool_name in self._tools_cache:
            tool = self._tools_cache[tool_name]
            return tool.example_usage
        return None
    
    async def validate_tool_dependencies(self, tool_name: str) -> Dict[str, bool]:
        """Validate that all dependencies for a tool are available"""
        if tool_name not in self._tools_cache:
            return {"error": False, "message": "Tool not found"}
        
        tool = self._tools_cache[tool_name]
        validation_results = {}
        
        for dependency in tool.dependencies:
            try:
                importlib.import_module(dependency)
                validation_results[dependency] = True
            except ImportError:
                validation_results[dependency] = False
        
        return validation_results
    
    async def generate_tool_documentation(self, category: Optional[str] = None) -> str:
        """Generate markdown documentation for tools"""
        docs = ["# Tool Library Documentation\n"]
        
        categories = [self._categories[category]] if category else self._categories.values()
        
        for cat in categories:
            docs.append(f"## {cat.icon} {cat.name}\n")
            docs.append(f"{cat.description}\n")
            
            for tool in cat.tools:
                docs.append(f"### {tool.name}\n")
                docs.append(f"**Description:** {tool.description}\n")
                docs.append(f"**Tags:** {', '.join(tool.tags)}\n")
                docs.append(f"**MCP Compatible:** {'Yes' if tool.mcp_compatible else 'No'}\n")
                
                if tool.dependencies:
                    docs.append(f"**Dependencies:** {', '.join(tool.dependencies)}\n")
                
                if tool.example_usage:
                    docs.append(f"**Example Usage:**\n```python\n{tool.example_usage}\n```\n")
                
                docs.append("\n---\n")
        
        return "\n".join(docs)

# Create default tools for common categories
def create_default_tools():
    """Create default tools for the library"""
    default_tools = [
        {
            "name": "web_scraper",
            "description": "Extract data from web pages using BeautifulSoup",
            "parameters": {
                "url": {"type": "str", "description": "URL to scrape"},
                "selector": {"type": "str", "description": "CSS selector for elements"}
            },
            "implementation": """
async def web_scraper(url: str, selector: str) -> List[str]:
    import requests
    from bs4 import BeautifulSoup
    
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    elements = soup.select(selector)
    return [elem.get_text() for elem in elements]
""",
            "category": "web_scraping",
            "tags": ["scraping", "web", "data-extraction"],
            "mcp_compatible": True,
            "dependencies": ["requests", "beautifulsoup4"]
        },
        {
            "name": "file_reader",
            "description": "Read and process various file formats",
            "parameters": {
                "file_path": {"type": "str", "description": "Path to the file"},
                "encoding": {"type": "str", "default": "utf-8"}
            },
            "implementation": """
async def file_reader(file_path: str, encoding: str = 'utf-8') -> str:
    import os
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, 'r', encoding=encoding) as f:
        return f.read()
""",
            "category": "file_operations",
            "tags": ["file", "read", "io"],
            "mcp_compatible": True,
            "dependencies": []
        },
        {
            "name": "api_client",
            "description": "Generic HTTP API client with authentication",
            "parameters": {
                "url": {"type": "str", "description": "API endpoint URL"},
                "method": {"type": "str", "default": "GET"},
                "headers": {"type": "dict", "default": {}},
                "auth_token": {"type": "str", "default": None}
            },
            "implementation": """
async def api_client(url: str, method: str = 'GET', headers: dict = None, auth_token: str = None) -> dict:
    import httpx
    
    headers = headers or {}
    if auth_token:
        headers['Authorization'] = f'Bearer {auth_token}'
    
    async with httpx.AsyncClient() as client:
        response = await client.request(method, url, headers=headers)
        return response.json()
""",
            "category": "api_clients",
            "tags": ["api", "http", "client"],
            "mcp_compatible": True,
            "dependencies": ["httpx"]
        }
    ]
    
    return default_tools

# Global tool library instance
tool_library = ToolLibrary()
