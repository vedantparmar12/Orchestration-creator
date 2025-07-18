#!/usr/bin/env python3
"""Test script to verify OpenRouter configuration"""

import asyncio
import os
from src.utils.pydantic_ai_config import create_openrouter_model, get_configured_model_name
from src.grok_heavy.orchestrator import GrokHeavyOrchestrator

async def test_openrouter_config():
    """Test OpenRouter configuration"""
    print("🧪 Testing OpenRouter Configuration")
    print("=" * 50)
    
    # Test 1: Check environment variables
    print("\n1. Environment Variables:")
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    default_model = os.getenv("DEFAULT_MODEL", "openai/gpt-4o")
    
    if openrouter_key and openrouter_key != "sk-or-your-openrouter-api-key-here":
        print(f"✅ OPENROUTER_API_KEY: Configured ({openrouter_key[:10]}...)")
    else:
        print(f"❌ OPENROUTER_API_KEY: {openrouter_key or 'Not set'}")
        print("   Please set your OpenRouter API key in the .env file")
        return False
    
    print(f"✅ DEFAULT_MODEL: {default_model}")
    
    # Test 2: Test model configuration
    print("\n2. Model Configuration:")
    try:
        model_name = get_configured_model_name()
        print(f"✅ Configured model: {model_name}")
        
        openrouter_model = create_openrouter_model()
        print(f"✅ OpenRouter model created: {type(openrouter_model)}")
        
    except Exception as e:
        print(f"❌ Model configuration failed: {e}")
        return False
    
    # Test 3: Test orchestrator initialization
    print("\n3. Orchestrator Initialization:")
    try:
        orchestrator = GrokHeavyOrchestrator()
        print(f"✅ Orchestrator created: {type(orchestrator)}")
        print(f"✅ Model name: {orchestrator.model_name}")
        print(f"✅ OpenRouter model: {type(orchestrator.openrouter_model)}")
        
    except Exception as e:
        print(f"❌ Orchestrator initialization failed: {e}")
        return False
    
    # Test 4: Test a simple question generation (if API key is valid)
    print("\n4. Simple Question Generation Test:")
    try:
        test_query = "What is the capital of France?"
        print(f"Testing query: {test_query}")
        
        # This will make an actual API call if the key is valid
        result = await orchestrator.question_generator.run(
            f"Generate 4 specialized research questions for: {test_query}"
        )
        
        print(f"✅ Question generation successful!")
        print(f"📋 Generated questions: {result.data}")
        
    except Exception as e:
        print(f"❌ Question generation failed: {e}")
        print("   This might be due to invalid API key or network issues")
        return False
    
    print("\n🎉 All tests passed! OpenRouter configuration is working correctly.")
    return True

if __name__ == "__main__":
    asyncio.run(test_openrouter_config())
