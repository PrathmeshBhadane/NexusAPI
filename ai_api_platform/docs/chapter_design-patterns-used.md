## 🎯 Design Patterns Used

### 1️⃣ **Microservices Pattern**
```
Single monolithic app → Multiple independent services
Benefits:
  ✅ Scale each service independently
  ✅ Different tech stacks per service
  ✅ Easier to deploy updates
  ✅ Fault isolation (1 service down ≠ all down)
```

### 2️⃣ **API Gateway Pattern**
```
Clients → Many internal services

Becomes:

Clients → Gateway → {many internal services}

Benefits:
  ✅ Single entry point
  ✅ Centralized auth
  ✅ Rate limiting at gateway level
  ✅ Client doesn't know internal service URLs
```

### 3️⃣ **Service Discovery Pattern**
```
Version 1: Hardcoded URLs in environment variables
    ENV AUTH_SERVICE_URL=http://auth-service:8001

Version 2: Redis service registry (implemented here)
    auth-service registers: redis.hset("registry:auth", {...})
    gateway discovers: redis.hgetall("registry:auth")
    Benefits:
      ✅ Services can move/restart without config change
      ✅ Gateway detects service failures
      ✅ Dynamic scaling
```

### 4️⃣ **Async Job Queue Pattern**
```
User request → Queue → Worker processes in background

Example:
    POST /ml/train → RabbitMQ → worker picks up → training
    
Benefits:
    ✅ Immediate response to user (job_id)
    ✅ No HTTP timeout for long operations
    ✅ Can restart worker without losing jobs
    ✅ Horizontal scaling of workers
```

### 5️⃣ **Cache-Aside Pattern**
```
Check cache → cache hit? return cached
              cache miss? → fetch from source → cache result → return

Used in AI Service:
    GET /ai/chat?prompt="What is ML?"
    → hash prompt
    → check Redis
    → if Redis hit: return cached response (2ms)
    → if Redis miss: call Groq API (800ms), cache, return
```

### 6️⃣ **Circuit Breaker Pattern**
```
Call external service
  → Success: count = 0
  → Failure: count ++
  → If count >= threshold: STOP calling (open circuit)
  → After timeout: try again (half-open)
  → If succeeds: reset (closed)

Example: Tenacity library with retries
```

### 7️⃣ **Strangler Fig Pattern**
```
Old system → New microservice gradually replaces it

Today:
    ✅ All routing through gateway
    ✅ Each service is independent
    
Tomorrow:
    + Add new service
    + Gateway routes some requests to new service
    + Old service still handles rest
    + Eventually migrate completely
```

### 8️⃣ **Health Check Pattern**
```
Docker checks each service:
    every 10 seconds: run healthcheck command
    if fails 5 times: mark unhealthy
    
Benefits:
    ✅ Gateway knows which services are available
    ✅ Docker won't start dependent services too early
    ✅ Automatic detection of failures
```

---

