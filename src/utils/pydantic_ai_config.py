import os
from typing import Optional
from pydantic_ai.models.openai import OpenAIModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_openrouter_model(model_name: Optional[str] = None) -> OpenAIModel:
    """Create an OpenAI model configured for OpenRouter"""
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    
    if not openrouter_api_key:
        raise ValueError("OPENROUTER_API_KEY not found in environment variables")
    
    # Get the model name
    actual_model_name = model_name or get_configured_model_name()
    
    # Create OpenAI model with OpenRouter configuration
    return OpenAIModel(
        model_name=actual_model_name,
        base_url="https://openrouter.ai/api/v1",
        api_key=openrouter_api_key
    )

def get_configured_model_name(model_name: Optional[str] = None) -> str:
    """Get the configured model name for OpenRouter"""
    if model_name:
        return model_name
    
    # Get default model from environment
    default_model = os.getenv("DEFAULT_MODEL", "openai/gpt-4o")
    return default_model

def get_openrouter_model_string(model_name: Optional[str] = None) -> str:
    """Get the model string for use with Pydantic AI Agent"""
    return get_configured_model_name(model_name)

# Test configuration on import
try:
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    if openrouter_api_key:
        print(f"✅ OpenRouter API key configured")
        print(f"📋 Default model: {get_configured_model_name()}")
    else:
        print("⚠️ OPENROUTER_API_KEY not found in environment variables")
        print("Please check your .env file")
except Exception as e:
    print(f"⚠️ Error checking OpenRouter configuration: {e}")
