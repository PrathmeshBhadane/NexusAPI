## 🛠️ Dockerfiles & Containerization

### 🎯 Dockerfile Concepts Learned

| Concept | Icon | Explanation |
|---------|------|-------------|
| **Multi-stage Builds** | 🏢 | Separate builder and runtime stages |
| **Slim Base Images** | 🔍 | python:3.x-slim for reduced size |
| **Layer Caching** | 💾 | requirements.txt copied first for cache hits |
| **Non-root User** | 🔒 | app user instead of root for security |
| **Health Checks** | ❤️ | curl commands to verify service health |
| **Environment Variables** | ⚙️ | Set defaults for runtime configuration |
| **Volume Mounts** | 📂 | /app/uploads for persistent storage |
| **Port Exposure** | 🔌 | Service ports documented in EXPOSE |

### 📋 Typical Dockerfile Pattern

```dockerfile
# Stage 1: Builder
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim
WORKDIR /app
RUN useradd -m -u 1000 appuser

# Copy built dependencies from builder
COPY --from=builder /root/.local /home/appuser/.local
ENV PATH=/home/appuser/.local/bin:$PATH

COPY app/ ./app/

USER appuser
EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 🔧 Key Dockerfile Optimizations

```
1. Layer Caching Strategy
   ❌ BAD: COPY . . then pip install (cache busted on any change)
   ✅ GOOD: COPY requirements.txt, pip install, then COPY app/

2. Image Size Reduction
   ❌ BAD: python:3.11 (1GB+)
   ✅ GOOD: python:3.11-slim (300MB)

3. Security
   ❌ BAD: Run as root user
   ✅ GOOD: Create non-root appuser

4. Health Checks
   ❌ BAD: Docker assumes running = healthy
   ✅ GOOD: Health check that validates actual readiness

5. Build Speed
   ❌ BAD: Complex dependencies in single stage
   ✅ GOOD: Multi-stage build with builder stage
```

---

