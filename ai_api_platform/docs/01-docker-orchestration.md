## 🏗️ docker-compose.yml

*File: `docker-compose.yml`*  
*Purpose: Orchestrates the entire AI Platform microservices ecosystem*

### 1. Networks

```yaml
networks:
  aiplatform-network:
    driver: bridge
```

**🎯 What it is:**
A Docker network is a private virtual network that exists only inside Docker. All containers connected to the same network can talk to each other by container name instead of IP address.

**🌉 Why bridge:**
Bridge is the default network driver for single-host setups. It creates an isolated network on your machine. Containers inside can talk to each other. Outside world cannot reach them directly.

**🏢 Real world analogy:**
Think of it like a private office LAN. All computers in the office can talk to each other by name. People outside the office cannot access any computer directly — they have to go through the reception (Nginx).

**⚙️ How it works in our project:**
```
auth-service wants to talk to auth-db
Instead of: postgresql://172.18.0.3:5432  ← fragile, IP changes
It uses:    postgresql://auth-db:5432      ← stable, always works
Docker automatically resolves auth-db to whatever IP that container has.
```

### 2. Volumes

```yaml
volumes:
  auth_postgres_data:
  ml_postgres_data:
  redis_data:
  rabbitmq_data:
```

**💾 What it is:**
A volume is persistent storage that lives outside the container. When a container is deleted or restarted, its internal filesystem is wiped. Volumes survive that.

**❓ Why we need it:**
Without volumes:
```
docker compose down → PostgreSQL container deleted → ALL YOUR DATA GONE ❌
```
With volumes:
```
docker compose down → PostgreSQL container deleted → data survives in volume ✅
docker compose up  → PostgreSQL container recreated → data is still there ✅
```

**🚗 Real world analogy:**
The container is like a rental car. You return it and it gets wiped. The volume is like your USB drive — you take it with you regardless of which car you use.

**📁 Two types of volumes in our file:**

- **Named volumes** — managed by Docker:
  ```yaml
  volumes:
    - auth_postgres_data:/var/lib/postgresql/data
  ```
  Docker stores this somewhere on your machine automatically.

- **Bind mounts** — you control the path:
  ```yaml
  volumes:
    - ./ml-service/saved_models:/app/saved_models
  ```
  This maps a folder on your laptop directly into the container. Changes on your laptop instantly appear inside the container and vice versa. We use this for ML model files and uploaded CSVs so they persist on your actual machine.

### 3. Each Service Block

```yaml
auth-db:
  image: postgres:16
  environment:
    POSTGRES_DB: auth_db
    POSTGRES_USER: auth_user
    POSTGRES_PASSWORD: auth_pass
```

**🐳 Key Components:**
- `image: postgres:16` — Pull this from Docker Hub. postgres:16 means official PostgreSQL version 16. Docker downloads it automatically the first time.
- `environment:` These are environment variables injected into the container at runtime. PostgreSQL reads these on first startup to create the database and user automatically. You never have to run CREATE DATABASE manually.

**🏛️ Why one database per service:**
This is the core microservices principle — database per service. Auth service owns auth_db. ML service owns ml_db. They never touch each other's database directly. This means:

- ✅ Auth team can change their schema without breaking ML team
- ✅ If auth-db crashes, ml-db still works
- ✅ You can use a completely different database type per service if needed

### 4. Health Checks

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U auth_user -d auth_db"]
  interval: 10s
  timeout: 5s
  retries: 5
```

**❤️ What it is:**
Docker runs this command inside the container every 10 seconds. If it succeeds the container is `healthy`. If it fails 5 times in a row the container is `unhealthy`.

**🚨 Why it matters — the depends_on problem:**
Without health checks:
```
docker compose up
→ auth-db starts (takes 3 seconds to be ready)
→ auth-service starts immediately
→ auth-service tries to connect to auth-db
→ auth-db not ready yet → CONNECTION REFUSED → crash ❌
```
With health checks:
```yaml
depends_on:
  auth-db:
    condition: service_healthy
```
```
→ auth-db starts
→ Docker waits until auth-db passes health check
→ only then starts auth-service
→ connection succeeds every time ✅
```

**🍳 Real world analogy:**
You don't open the restaurant doors until the kitchen is actually ready. Health checks are the kitchen saying "we're ready".

### 5. depends_on

```yaml
depends_on:
  auth-db:
    condition: service_healthy
  redis:
    condition: service_healthy
```

**🔗 What it is:**
Defines startup order. Auth service won't start until both `auth-db` AND `redis` are healthy.

**📊 The full startup order in our project:**
```
1. auth-db, ml-db, data-db start simultaneously
2. redis starts
3. rabbitmq starts
4. Once all DBs + redis + rabbitmq are healthy:
   → auth-service, ml-service, ai-service, data-service start
5. Once all services are healthy:
   → gateway starts
6. Once gateway starts:
   → nginx starts
```
This guarantees nothing starts before its dependencies are ready.

### 6. Ports

```yaml
ports:
  - "8000:8000"
```

**🔌 Format:** `host_port:container_port`

**🌐 What it means:**
Map port 8000 on your laptop to port 8000 inside the container. When you go to localhost:8000 on your laptop, Docker forwards that to port 8000 inside the gateway container.

**🚫 Notice what does NOT have ports exposed:**
- `auth-service:`   # no ports section
- `ml-service:`     # no ports section
- `auth-db:`        # no ports section
- `redis:`          # no ports section

These are internal only. You cannot reach `auth-service` directly from your browser. You can only reach it through the gateway. This is the **API Gateway pattern** — single entry point.

**🌍 Only these are exposed to outside:**
```
gateway:   8000  ← your app's API
nginx:     80    ← web traffic
rabbitmq:  15672 ← management dashboard (so you can monitor queues)
```

### 7. The Services Themselves

```yaml
gateway:
  build: ./gateway
  environment:
    AUTH_SERVICE_URL: http://auth-service:8001
    ML_SERVICE_URL: http://ml-service:8002
```

**🔨 Key Points:**
- `build: ./gateway` — instead of pulling an image from Docker Hub, build our own image using the `Dockerfile` inside the `./gateway` folder.
- `environment with service URLs` — this is service discovery the simple way. The gateway knows where every service is via environment variables. When a request comes in for `/ml/train`, the gateway reads `ML_SERVICE_URL` and forwards the request there.

**🔄 Future Upgrade:**
Later we'll upgrade this to dynamic service discovery using Redis — services register themselves and the gateway looks them up. But environment variables are the foundation.

### 8. The API Gateway Pattern

```
Internet
   │
   ▼
Nginx (port 80)
   │
   ▼
Gateway (port 8000)      ← THE ONLY SERVICE THE OUTSIDE WORLD TALKS TO
   │
   ├── auth-service:8001
   ├── ml-service:8002
   ├── ai-service:8003
   └── data-service:8004
```

**⚡ What the gateway does on every request:**
```
1. 📨 Receive request from client
2. 🔐 Validate JWT or API key
3. ⏱️ Check rate limit in Redis
4. 🗺️ Look up which service handles this route
5. ➡️ Forward request to that service
6. 📨 Get response back
7. 📝 Log the request to Redis
8. 📤 Return response to client
```

**💪 Why this is powerful:**
- 🔒 Auth logic lives in ONE place — the gateway
- 🚫 Services don't need to handle auth themselves
- ➕ You can add a new service without changing client code
- 📊 You can monitor all traffic in one place
- 🛡️ Services are completely hidden from the internet

### 9. RabbitMQ — Message Queue

```yaml
rabbitmq:
  image: rabbitmq:3-management-alpine
  environment:
    RABBITMQ_DEFAULT_USER: rabbit_user
    RABBITMQ_DEFAULT_PASS: rabbit_pass
```

**📬 What it is:**
A message broker. Services put messages in queues. Other services pick them up and process them.

**🤖 Why we need it for ML training:**
ML training takes 30 seconds to 5 minutes. You can't make the user wait with an open HTTP connection that long.

**❌ Without RabbitMQ:**
```
User: POST /ml/train
Gateway: forwards to ML service
ML service: starts training...
[30 seconds pass]
[HTTP connection times out]
User gets an error even though training succeeded
```

**✅ With RabbitMQ:**
```
User: POST /ml/train
Gateway: forwards to ML service
ML service: publishes {job_id: "abc", data: ...} to queue
ML service: immediately returns {job_id: "abc", status: "queued"}
[User gets response in 50ms]

ML Worker: picks up job from queue
ML Worker: trains model (30 seconds)
ML Worker: updates job status in database to "complete"

User: GET /ml/jobs/abc
ML service: returns {status: "complete", model_id: "xyz"}
```

**🍽️ Real world analogy:**
You place an order at a restaurant. Waiter takes your order (50ms), gives you a ticket number, and walks away. Kitchen processes your order (20 minutes). You don't stand at the counter for 20 minutes — you sit down and check back later.

### 10. Redis — Three roles in our project

```yaml
redis:
  image: redis:7-alpine
```

**🔄 Redis does three completely different jobs in our architecture:**

**1️⃣ Role 1 — Cache:**
```
AI service gets same prompt twice
First time: calls Groq API (800ms) → stores result in Redis
Second time: reads from Redis (2ms) → 400x faster 🚀
```

**2️⃣ Role 2 — Rate Limiting:**
```
Redis stores: {api_key: "abc123", requests_this_hour: 47}
Gateway checks this before every request
If > 100: return 429 Too Many Requests 🛑
```

**3️⃣ Role 3 — Service Registry:**
```
auth-service on startup:
redis.hset("registry:auth-service", {
    url: "http://auth-service:8001",
    status: "healthy",
    last_seen: "2026-03-21T09:00:00"
})

Every 10 seconds: updates last_seen (heartbeat)

Gateway before routing:
service = redis.hgetall("registry:ml-service")
if service is None or last_seen > 30s ago:
    return 503 Service Unavailable
else:
    forward request to service.url
```

---

