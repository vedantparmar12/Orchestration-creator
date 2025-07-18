# 🚀 Enhanced Agentic Workflow with OpenRouter Support

This project now supports **OpenRouter**, which means you can use **any model** available through OpenRouter's API, including:

- **OpenAI Models**: GPT-4o, GPT-4o-mini, GPT-4-turbo, GPT-3.5-turbo
- **Anthropic Models**: Claude-3.5-sonnet, Claude-3.5-haiku, Claude-3-opus
- **Google Models**: Gemini-pro, Gemini-flash
- **Meta Models**: Llama-3.1-70b, Llama-3.1-8b
- **Other Models**: Qwen-2.5-72b, DeepSeek-chat, Yi-large, Mixtral-8x7b
- **And many more!**

## 🔧 Quick Setup

### 1. Get OpenRouter API Key

1. Go to [OpenRouter.ai](https://openrouter.ai)
2. Create an account or sign in
3. Navigate to [API Keys](https://openrouter.ai/keys)
4. Create a new API key
5. Copy the key (starts with `sk-or-`)

### 2. Configure Environment

Update your `.env` file with your OpenRouter API key:

```bash
# OpenRouter API key - supports any model from OpenRouter
OPENROUTER_API_KEY=sk-or-your-actual-openrouter-api-key-here

# Default model to use (can be any OpenRouter model)
DEFAULT_MODEL=openai/gpt-4o

# Optional: Other configurations
LOGFIRE_TOKEN=your_logfire_token_here
```

### 3. Available Models

You can use any model from OpenRouter. Here are some popular options:

#### OpenAI Models
- `openai/gpt-4o` - Latest GPT-4o model
- `openai/gpt-4o-mini` - Smaller, faster GPT-4o
- `openai/gpt-4-turbo` - GPT-4 Turbo
- `openai/gpt-3.5-turbo` - GPT-3.5 Turbo

#### Anthropic Models
- `anthropic/claude-3.5-sonnet` - Claude 3.5 Sonnet
- `anthropic/claude-3.5-haiku` - Claude 3.5 Haiku
- `anthropic/claude-3-opus` - Claude 3 Opus

#### Google Models
- `google/gemini-pro` - Gemini Pro
- `google/gemini-flash-1.5` - Gemini Flash

#### Meta Models
- `meta-llama/llama-3.1-70b-instruct` - Llama 3.1 70B
- `meta-llama/llama-3.1-8b-instruct` - Llama 3.1 8B

#### Other Models
- `qwen/qwen-2.5-72b-instruct` - Qwen 2.5 72B
- `deepseek/deepseek-chat` - DeepSeek Chat
- `01-ai/yi-large` - Yi Large
- `mistralai/mixtral-8x7b-instruct` - Mixtral 8x7B

## 🧪 Testing the Configuration

Run the test script to verify everything is working:

```bash
python test_openrouter_config.py
```

This will:
1. ✅ Check environment variables
2. ✅ Test model configuration
3. ✅ Test orchestrator initialization  
4. ✅ Test question generation with actual API call

## 🎯 Usage Examples

### 1. Basic Grok Heavy Mode

```bash
# Interactive mode
python make_it_heavy.py

# Direct query
python make_it_heavy.py "Who is Elon Musk?"

# With different model (set in .env)
# DEFAULT_MODEL=anthropic/claude-3.5-sonnet
python make_it_heavy.py "Explain quantum computing"
```

### 2. Change Models on the Fly

You can change the model by updating the `DEFAULT_MODEL` in your `.env` file:

```bash
# Use Claude 3.5 Sonnet
DEFAULT_MODEL=anthropic/claude-3.5-sonnet

# Use Gemini Pro
DEFAULT_MODEL=google/gemini-pro

# Use Llama 3.1 70B
DEFAULT_MODEL=meta-llama/llama-3.1-70b-instruct
```

### 3. FastAPI Service

Start the API service:

```bash
uvicorn src.api.fastapi_service:app --reload --host 0.0.0.0 --port 8080
```

### 4. Streamlit Dashboard

Launch the comprehensive UI:

```bash
streamlit run src/ui/streamlit_dashboard.py
```

## 🔍 How It Works

### OpenRouter Configuration

The system uses OpenRouter as an OpenAI-compatible endpoint:

```python
from src.utils.pydantic_ai_config import create_openrouter_model

# Creates OpenAI model configured for OpenRouter
openrouter_model = create_openrouter_model()

# Uses OpenRouter API with any model
agent = Agent(
    model=openrouter_model,
    result_type=YourOutputType,
    system_prompt="Your system prompt here"
)
```

### Multi-Agent Orchestration

The system creates 4 specialized agents in parallel:

1. **Research Agent**: Gathers factual background information
2. **Analysis Agent**: Evaluates achievements and contributions  
3. **Perspective Agent**: Explores alternative viewpoints
4. **Verification Agent**: Fact-checks and validates information

All agents use the same OpenRouter model configuration but with different system prompts.

## 📊 Live Progress Display

The system shows real-time progress:

```
🎯 Analyzing: Who is Elon Musk?

┌─ Research Agent ──┐  ┌─ Analysis Agent ──┐  ┌─ Perspective Agent ─┐  ┌─ Verification Agent ┐
│ 🔄 Researching... │  │ ✅ Analysis Done  │  │ 🔄 Finding views... │  │ ⏳ Waiting...       │
│ Professional bg   │  │ Achievements found│  │ Multiple perspectives│  │                    │
└───────────────────┘  └───────────────────┘  └────────────────────┘  └────────────────────┘

🔄 Intelligent Synthesis: Combining all perspectives...
```

## 🛠️ Advanced Configuration

### Custom Model Selection

You can specify different models for different agents by modifying the orchestrator:

```python
# In src/grok_heavy/orchestrator.py
research_model = create_openrouter_model("anthropic/claude-3.5-sonnet")
analysis_model = create_openrouter_model("openai/gpt-4o")
```

### Model Pricing

OpenRouter shows pricing for each model. Popular options:

- **GPT-4o**: $5/$15 per 1M tokens (input/output)
- **Claude-3.5-sonnet**: $3/$15 per 1M tokens
- **Gemini-pro**: $0.5/$1.5 per 1M tokens
- **Llama-3.1-70b**: $0.59/$0.79 per 1M tokens

## 🚨 Troubleshooting

### Common Issues

1. **Invalid API Key Error**
   ```
   Error: Incorrect API key provided
   ```
   **Solution**: Check your OpenRouter API key in `.env`

2. **Model Not Found**
   ```
   Error: Model not found
   ```
   **Solution**: Check available models at [OpenRouter Models](https://openrouter.ai/models)

3. **Rate Limiting**
   ```
   Error: Rate limit exceeded
   ```
   **Solution**: Wait a moment or upgrade your OpenRouter plan

### Debug Mode

Run with debug information:

```bash
export LOGFIRE_TOKEN=your_token_here
python make_it_heavy.py "Your query here"
```

## 🎉 Success Indicators

When everything is working correctly, you should see:

```
✅ OpenRouter API key configured
📋 Default model: openai/gpt-4o
🚀 GROK HEAVY MODE
Deep Multi-Agent Analysis System

🎯 Analyzing: Your query here
🎯 Generating Research Questions: Generating specialized research questions...
⚡ Live Agent Execution Status:
✅ All agents completed successfully
🔄 Intelligent Synthesis: Comprehensive analysis complete!
```

## 📚 Further Reading

- [OpenRouter Documentation](https://openrouter.ai/docs)
- [Available Models](https://openrouter.ai/models)
- [Pricing](https://openrouter.ai/pricing)
- [Pydantic AI Documentation](https://ai.pydantic.dev/)

---

**Happy multi-agent analyzing! 🚀**
