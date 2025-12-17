# 🎯 Quick Reference Card - API Provider Setup

## Current Setup (Groq - FREE)

```
┌─────────────────────────────────────────┐
│  FORGE AI Backend Generator             │
│                                         │
│  Provider: GROQ (Default)              │
│  Model: llama-3.3-70b-versatile        │
│  Cost: FREE ✅                          │
│  Speed: Ultra Fast ⚡⚡⚡                 │
└─────────────────────────────────────────┘
```

### Setup in 3 Steps:

```bash
# 1. Get key from: https://console.groq.com/keys

# 2. Set environment variable
$env:GROQ_API_KEY="your_key_here"

# 3. Test it
python setup_groq.py
```

---

## Future Setup (OpenAI)

```
┌─────────────────────────────────────────┐
│  FORGE AI Backend Generator             │
│                                         │
│  Provider: OPENAI                       │
│  Model: gpt-4o-mini                     │
│  Cost: $0.15/1M tokens                  │
│  Speed: Fast ⚡⚡                         │
└─────────────────────────────────────────┘
```

### Switch in 2 Steps:

```bash
# 1. Set OpenAI key
$env:OPENAI_API_KEY="sk-your_key"

# 2. Change provider
$env:BACKEND_AGENT_LLM_PROVIDER="openai"
```

---

## Quick Commands

### Check Current Provider
```bash
python -c "from backend_agent.config import BackendAgentConfig; print(BackendAgentConfig().llm.provider)"
```

### Test Groq
```bash
python -c "from backend_agent.utils.llm_factory import create_llm; create_llm({'provider':'groq'}); print('✓')"
```

### Test OpenAI
```bash
python -c "from backend_agent.utils.llm_factory import create_llm; create_llm({'provider':'openai'}); print('✓')"
```

### Generate Backend
```bash
python forge_pipeline.py ./your-frontend
```

---

## Available Models

### Groq (FREE)
- `llama-3.3-70b-versatile` ⭐ Best
- `llama-3.1-70b-versatile` Fast
- `mixtral-8x7b-32768` Long context

### OpenAI
- `gpt-4o` ⭐ Best quality
- `gpt-4o-mini` Fast & cheap
- `gpt-4-turbo` High quality

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| No API key | `$env:GROQ_API_KEY="key"` |
| Wrong provider | Check `backend-config.yaml` |
| Import error | `pip install langchain-groq` |
| Test failed | Run `python setup_groq.py` |

---

## File Locations

- **Config**: `backend-config.yaml`
- **Environment**: `.env`
- **Setup Script**: `setup_groq.py`
- **Full Guide**: `DUAL_PROVIDER_COMPLETE.md`

---

**Current**: Groq (FREE) ⚡  
**Future**: OpenAI (Ready) 🚀  
**Switching**: 1 line change ⚙️
