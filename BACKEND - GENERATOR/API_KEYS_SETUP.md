# 🔑 API Key Setup Guide

## Quick Setup (Using Groq - Current Default)

1. **Get your Groq API key:**
   - Visit: https://console.groq.com/keys
   - Sign up/login
   - Create a new API key

2. **Set the environment variable:**

   **Windows (PowerShell):**
   ```powershell
   $env:GROQ_API_KEY="your_groq_api_key_here"
   ```

   **Or create `.env` file:**
   ```bash
   GROQ_API_KEY=your_groq_api_key_here
   BACKEND_AGENT_LLM_PROVIDER=groq
   ```

3. **Test it:**
   ```bash
   python -c "import os; print('✓ Groq API Key set' if os.getenv('GROQ_API_KEY') else '✗ Not set')"
   ```

## Future: Switching to OpenAI

When you want to switch to OpenAI:

1. **Get OpenAI API key:**
   - Visit: https://platform.openai.com/api-keys
   - Create API key

2. **Update configuration:**

   **Option A: Environment Variable**
   ```powershell
   $env:OPENAI_API_KEY="sk-your_openai_key"
   $env:BACKEND_AGENT_LLM_PROVIDER="openai"
   ```

   **Option B: Update `.env` file**
   ```bash
   OPENAI_API_KEY=sk-your_openai_key
   BACKEND_AGENT_LLM_PROVIDER=openai
   ```

   **Option C: Update `backend-config.yaml`**
   ```yaml
   llm:
     provider: "openai"
     model: "gpt-4o-mini"
   ```

## Both Keys Together

You can set both keys and switch between them anytime:

```bash
# .env file
GROQ_API_KEY=your_groq_key
OPENAI_API_KEY=your_openai_key
BACKEND_AGENT_LLM_PROVIDER=groq  # Change to 'openai' to switch
```

## Available Models

### Groq (Current - Fast & Free)
- `llama-3.3-70b-versatile` (Default) ⚡ Best quality
- `llama-3.1-70b-versatile` ⚡ Very fast
- `llama-3.1-8b-instant` ⚡⚡ Ultra fast
- `mixtral-8x7b-32768` ⚡ Long context
- `gemma2-9b-it` ⚡ Fast

### OpenAI (Future)
- `gpt-4o` 🎯 Best quality
- `gpt-4o-mini` (Default) ⚡ Fast & cheap
- `gpt-4-turbo` 🎯 High quality
- `gpt-4` 🎯 Premium

## Verify Setup

```bash
# Test Groq
python -c "from backend_agent.utils.llm_factory import create_llm; llm = create_llm({'provider': 'groq', 'model': 'llama-3.3-70b-versatile'}); print('✓ Groq working!')"

# Test OpenAI (when ready)
python -c "from backend_agent.utils.llm_factory import create_llm; llm = create_llm({'provider': 'openai', 'openai_model': 'gpt-4o-mini'}); print('✓ OpenAI working!')"
```

## Configuration File Examples

### backend-config.yaml (Groq - Current)
```yaml
llm:
  provider: "groq"
  model: "llama-3.3-70b-versatile"
  temperature: 0.1
```

### backend-config.yaml (OpenAI - Future)
```yaml
llm:
  provider: "openai"
  openai_model: "gpt-4o-mini"
  temperature: 0.1
```

## Troubleshooting

### "Groq API key not found"
```powershell
# Check if set
echo $env:GROQ_API_KEY

# Set it
$env:GROQ_API_KEY="your_key"
```

### "langchain-groq not installed"
```bash
pip install langchain-groq
```

### Switch providers on the fly
```python
from backend_agent.config import BackendAgentConfig

config = BackendAgentConfig()
config.llm.provider = "openai"  # Switch to OpenAI
config.llm.provider = "groq"    # Switch back to Groq
```

## Cost Comparison

| Provider | Model | Cost | Speed |
|----------|-------|------|-------|
| **Groq** | llama-3.3-70b | FREE ✅ | Ultra Fast ⚡⚡⚡ |
| OpenAI | gpt-4o-mini | $0.15/1M | Fast ⚡⚡ |
| OpenAI | gpt-4o | $2.50/1M | Medium ⚡ |

**Recommendation:** Start with Groq (free + fast), switch to OpenAI when needed for specific quality requirements.

---

**Current Setup:** ✅ Configured for Groq  
**Future Ready:** ✅ OpenAI support available
