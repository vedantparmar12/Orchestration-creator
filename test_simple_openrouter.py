#!/usr/bin/env python3
"""Simple OpenRouter test without complex tool usage"""

import asyncio
import os
from src.utils.pydantic_ai_config import create_openrouter_model
from pydantic_ai import Agent
from pydantic import BaseModel

class SimpleResponse(BaseModel):
    """Simple response model"""
    answer: str
    confidence: float

async def test_simple_openrouter():
    """Test OpenRouter with simple agent"""
    print("🧪 Testing Simple OpenRouter Configuration")
    print("=" * 50)
    
    # Test 1: Check environment variables
    print("\n1. Environment Variables:")
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    default_model = os.getenv("DEFAULT_MODEL", "openai/gpt-4o-mini")
    
    if openrouter_key and not openrouter_key.startswith("sk-or-your-"):
        print(f"✅ OPENROUTER_API_KEY: Configured ({openrouter_key[:15]}...)")
    else:
        print(f"❌ OPENROUTER_API_KEY: Not configured")
        return False
    
    print(f"✅ DEFAULT_MODEL: {default_model}")
    
    # Test 2: Create simple agent
    print("\n2. Creating Simple Agent:")
    try:
        model = create_openrouter_model()
        print(f"✅ OpenRouter model created: {type(model)}")
        
        # Create simple agent without tools
        agent = Agent(
            model=model,
            result_type=SimpleResponse,
            system_prompt="You are a helpful assistant. Answer questions concisely."
        )
        print(f"✅ Simple agent created: {type(agent)}")
        
    except Exception as e:
        print(f"❌ Agent creation failed: {e}")
        return False
    
    # Test 3: Simple query
    print("\n3. Testing Simple Query:")
    try:
        test_query = "What is 2+2? Just give the answer."
        print(f"Testing query: {test_query}")
        
        result = await agent.run(test_query)
        
        print(f"✅ Query successful!")
        print(f"📋 Response: {result.data.answer}")
        print(f"🎯 Confidence: {result.data.confidence}")
        
    except Exception as e:
        print(f"❌ Query failed: {e}")
        return False
    
    print("\n🎉 Simple OpenRouter test passed!")
    return True

if __name__ == "__main__":
    asyncio.run(test_simple_openrouter())
