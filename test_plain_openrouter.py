#!/usr/bin/env python3
"""Test OpenRouter with plain text output (no structured output)"""

import asyncio
import os
from src.utils.pydantic_ai_config import create_openrouter_model
from pydantic_ai import Agent

async def test_plain_openrouter():
    """Test OpenRouter with plain text agent"""
    print("🧪 Testing Plain OpenRouter Configuration")
    print("=" * 50)
    
    # Test 1: Check environment variables
    print("\n1. Environment Variables:")
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    default_model = os.getenv("DEFAULT_MODEL", "moonshotai/kimi-k2:free")
    
    if openrouter_key and not openrouter_key.startswith("sk-or-your-"):
        print(f"✅ OPENROUTER_API_KEY: Configured ({openrouter_key[:15]}...)")
    else:
        print(f"❌ OPENROUTER_API_KEY: Not configured")
        return False
    
    print(f"✅ DEFAULT_MODEL: {default_model}")
    
    # Test 2: Create plain text agent
    print("\n2. Creating Plain Text Agent:")
    try:
        model = create_openrouter_model()
        print(f"✅ OpenRouter model created: {type(model)}")
        
        # Create agent with plain text output (no structured result)
        agent = Agent(
            model=model,
            system_prompt="You are a helpful assistant. Answer questions concisely and directly."
        )
        print(f"✅ Plain text agent created: {type(agent)}")
        
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
        print(f"📋 Response: {result.data}")
        
    except Exception as e:
        print(f"❌ Query failed: {e}")
        return False
    
    print("\n🎉 Plain OpenRouter test passed!")
    return True

if __name__ == "__main__":
    asyncio.run(test_plain_openrouter())
