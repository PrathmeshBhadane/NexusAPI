## 🧠 AI Service

*File: `ai-service/` (app/, Dockerfile, requirements.txt)*  
*Port: 8003*  
*Purpose: LLM integration (Groq, Anthropic), text analysis, caching*

### 🎯 AI Service Concepts Learned

| Concept | Icon | Implementation |
|---------|------|-----------------|
| **LLM API Integration** | 🤖 | Groq + Anthropic SDK for model calls |
| **Response Caching** | 💾 | Redis caching for identical requests |
| **Retry with Exponential Backoff** | 🔄 | tenacity library for resilient API calls |
| **Async Processing** | ⚡ | asyncio for non-blocking LLM calls |
| **Configuration Management** | ⚙️ | Pydantic Settings for API keys |
| **Service Registry** | 📍 | Heartbeat to Redis every 10s |
| **Error Handling** | 🚨 | Graceful fallback for API failures |

### 🏗️ AI Service Architecture

```
┌──────────────────────────────┐
│   AI Service (FastAPI)       │
└────┬──────────────┬──────────┘
     │              │
     ▼              ▼
┌─────────────────────────────┐
│   Caching Layer (Redis)     │
│  {prompt_hash: response}    │
└────────┬────────────────────┘
         │
     ┌───┴──────────────┬──────────────┐
     │                  │              │
     ▼                  ▼              ▼
  ┌──────┐         ┌────────┐    ┌──────────┐
  │ Groq │         │Anthropic    │ Fallback │
  │ API  │         │ API    │    │  Handler │
  └──────┘         └────────┘    └──────────┘
```

### 💬 AI Interaction Flow

```
User Request:
    POST /ai/chat {prompt: "What is ML?"}
    
Step 1: Check Cache
    → hash(prompt) → lookup in Redis
    → if found: return cached response ✅
    
Step 2: Call LLM API (with retry)
    → Use tenacity to retry on failure
    → Max retries: 3, Backoff: exponential
    → Call Groq API
    → Parse response
    
Step 3: Cache Response
    → Store in Redis with TTL
    → Return to user
```

### 💾 Requirements Analysis

```
fastapi==0.111.0
uvicorn[standard]==0.29.0
pydantic-settings==2.2.1
redis==5.0.4                  ← Caching layer
httpx==0.27.0
tenacity==8.3.0               ← Retry with backoff
groq==0.9.0                   ← Groq LLM SDK
anthropic==0.28.0             ← Anthropic Claude SDK
```

---

