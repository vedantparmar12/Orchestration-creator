import os
from typing import Optional, Dict, Any
from pydantic import BaseModel
from dotenv import load_dotenv
import httpx

# Load environment variables
load_dotenv()

class OpenRouterConfig(BaseModel):
    """Configuration for OpenRouter API"""
    api_key: str
    base_url: str = "https://openrouter.ai/api/v1"
    default_model: str = "openai/gpt-4o"
    app_name: str = "Enhanced Agentic Workflow"
    site_url: str = "https://github.com/your-repo/agent-creator"

class OpenRouterClient:
    """OpenRouter API client wrapper"""
    
    def __init__(self, config: Optional[OpenRouterConfig] = None):
        self.config = config or self._get_default_config()
        self.client = httpx.AsyncClient(
            base_url=self.config.base_url,
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "HTTP-Referer": self.config.site_url,
                "X-Title": self.config.app_name,
                "Content-Type": "application/json"
            }
        )
    
    def _get_default_config(self) -> OpenRouterConfig:
        """Get default OpenRouter configuration from environment"""
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables")
        
        return OpenRouterConfig(
            api_key=api_key,
            default_model=os.getenv("DEFAULT_MODEL", "openai/gpt-4o")
        )
    
    async def get_available_models(self) -> Dict[str, Any]:
        """Get list of available models from OpenRouter"""
        try:
            response = await self.client.get("/models")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Failed to get available models: {str(e)}")
    
    async def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get information about a specific model"""
        models = await self.get_available_models()
        for model in models.get("data", []):
            if model.get("id") == model_name:
                return model
        raise ValueError(f"Model {model_name} not found")
    
    def get_model_for_pydantic_ai(self, model_name: Optional[str] = None) -> str:
        """Get the model string formatted for Pydantic AI"""
        model = model_name or self.config.default_model
        return f"openai:{model}"
    
    def get_openai_compatible_config(self) -> Dict[str, Any]:
        """Get OpenAI-compatible configuration for Pydantic AI"""
        return {
            "api_key": self.config.api_key,
            "base_url": self.config.base_url,
            "default_headers": {
                "HTTP-Referer": self.config.site_url,
                "X-Title": self.config.app_name,
            }
        }
    
    async def test_connection(self) -> bool:
        """Test the OpenRouter API connection"""
        try:
            await self.get_available_models()
            return True
        except Exception:
            return False

# Global OpenRouter client instance
_openrouter_client: Optional[OpenRouterClient] = None

def get_openrouter_client() -> OpenRouterClient:
    """Get or create global OpenRouter client"""
    global _openrouter_client
    if _openrouter_client is None:
        _openrouter_client = OpenRouterClient()
    return _openrouter_client

def get_model_string(model_name: Optional[str] = None) -> str:
    """Get model string for Pydantic AI"""
    client = get_openrouter_client()
    return client.get_model_for_pydantic_ai(model_name)

async def list_available_models() -> Dict[str, Any]:
    """List all available models from OpenRouter"""
    client = get_openrouter_client()
    return await client.get_available_models()

# Model categories for easy selection
POPULAR_MODELS = {
    "gpt-4o": "openai/gpt-4o",
    "gpt-4o-mini": "openai/gpt-4o-mini", 
    "claude-3.5-sonnet": "anthropic/claude-3.5-sonnet",
    "claude-3.5-haiku": "anthropic/claude-3.5-haiku",
    "gemini-pro": "google/gemini-pro",
    "gemini-flash": "google/gemini-flash-1.5",
    "llama-3.1-70b": "meta-llama/llama-3.1-70b-instruct",
    "llama-3.1-8b": "meta-llama/llama-3.1-8b-instruct",
    "qwen-2.5-72b": "qwen/qwen-2.5-72b-instruct",
    "deepseek-chat": "deepseek/deepseek-chat",
    "yi-large": "01-ai/yi-large",
    "mixtral-8x7b": "mistralai/mixtral-8x7b-instruct"
}

def get_popular_models() -> Dict[str, str]:
    """Get dictionary of popular models"""
    return POPULAR_MODELS.copy()
