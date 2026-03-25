## 🚪 Gateway Service

*File: `gateway/` (main.py, Dockerfile, requirements.txt)*  
*Port: 8000*  
*Purpose: Reverse proxy, request routing, authentication, rate limiting*

### 🎯 Gateway Concepts Learned

| Concept | Icon | Implementation |
|---------|------|-----------------|
| **Service Discovery via Environment** | 🔍 | Service URLs injected as environment variables |
| **Health Check Routing** | ❤️ | Gateway checks service health before routing |
| **JWT Token Validation** | 🔐 | Delegates to auth-service for token verification |
| **API Key Validation** | 🔑 | Validates api_key headers before routing |
| **Rate Limiting Pattern** | ⏱️ | Uses Redis to count requests per API key |
| **Async HTTP Client** | 🔄 | httpx.AsyncClient for non-blocking external calls |
| **Service Registry Heartbeat** | 💓 | Registers self in Redis with 30s TTL |
| **Middleware Pattern** | 🛡️ | Auth and rate limiting as middleware layers |
| **Proxy Pass Headers** | 📨 | Preserves original request headers (Host, IP, etc.) |

### 🏗️ Gateway Architecture Pattern

```
┌─────────────────────────────────────────────┐
│           Client Request                    │
│         (with JWT or API Key)               │
└──────────────┬──────────────────────────────┘
               │
               ▼
        ┌──────────────┐
        │   Nginx      │  Port 80
        │ (Front Door) │
        └──────┬───────┘
               │
               ▼
        ┌──────────────────────┐
        │   Gateway Service    │  Port 8000
        │      (FastAPI)       │
        └──────┬───────┬───────┘
               │       │
        ┌──────▼─┐   ┌─┴──────────┐
        │ Auth   │   │ Rate Limit │
        │Middleware  │ Middleware │
        └──────┬─┘   └─┴──────────┘
               │
     ┌─────────┼─────────┬────────────┐
     │         │         │            │
     ▼         ▼         ▼            ▼
┌─────────┐ ┌────────┐ ┌─────────┐ ┌──────────┐
│ Auth    │ │  ML    │ │   AI    │ │  Data    │
│Service  │ │Service │ │Service  │ │Service   │
│ :8001   │ │ :8002  │ │ :8003   │ │ :8004    │
└─────────┘ └────────┘ └─────────┘ └──────────┘
   │           │          │          │
   ▼           ▼          ▼          ▼
┌──────────────────────────────────────────────┐
│        Shared Infrastructure                 │
│    (Redis, RabbitMQ, Databases)             │
└──────────────────────────────────────────────┘
```

### 🔐 Authentication Flow in Gateway

```python
async def validate_request(request: Request) -> dict:
    # 1. Check for Bearer token (JWT)
    if Authorization: Bearer <token>
        → call auth-service /auth/validate-token
        → if valid: extract user_id, permissions
        
    # 2. Check for API Key
    elif X-API-Key: <api_key>
        → call auth-service /keys/validate
        → if valid: extract api_key_id, permissions
        
    # 3. Neither found or invalid
        → return 401 Unauthorized
```

### ⏱️ Rate Limiting Pattern

```
Redis Storage:
    key: ratelimit:{api_key}
    value: { count: 47, reset_time: 1234567890 }

Check before each request:
    1. Get current count from Redis
    2. If count >= RATE_LIMIT_REQUESTS (100)
    3. Return 429 Too Many Requests
    4. Otherwise: increment count, renew TTL
```

### 💾 Requirements Analysis

```
fastapi==0.111.0              ← Web framework, async support
uvicorn[standard]==0.29.0     ← ASGI server, production ready
pydantic-settings==2.2.1      ← Environment config loading
redis==5.0.4                  ← Rate limiting + service registry
httpx==0.27.0                 ← Async HTTP client for service calls
python-multipart==0.0.9       ← Parse multipart form data
```

---

