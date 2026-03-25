## 📋 Service Communication Map

```
Services Communicate Through These Paths:

1. GATEWAY talks to:
   ├─ Auth-Service     → /auth/validate-token (JWT validation)
   ├─ Auth-Service     → /keys/validate (API key validation)
   ├─ Auth-Service     → (check service registry in Redis)
   ├─ ML-Service       → /ml/train (proxy request)
   ├─ ML-Service       → /ml/jobs/{id} (check status)
   ├─ ML-Service       → /ml/predict (run inference)
   ├─ AI-Service       → /ai/chat (LLM requests)
   ├─ Data-Service     → /data/upload (file upload)
   ├─ Data-Service     → /data/analyze (analysis)
   └─ Redis            → rate limit checks

2. AUTH-SERVICE talks to:
   ├─ auth_db          → User queries
   ├─ auth_db          → API key queries
   └─ Redis            → Register service health

3. ML-SERVICE talks to:
   ├─ ml_db            → Job tracking
   ├─ data_db          → Get datasets
   ├─ RabbitMQ         → Publish training jobs
   ├─ ML Worker        → Receive completed models
   ├─ saved_models/    → Load/save .pkl files
   └─ Redis            → Register service health

4. AI-SERVICE talks to:
   ├─ Groq API         → LLM requests
   ├─ Anthropic API    → Fallback LLM
   ├─ Redis            → Cache responses
   └─ Redis            → Register service health

5. DATA-SERVICE talks to:
   ├─ data_db          → Dataset metadata
   ├─ uploads/         → Store CSV files
   ├─ pandas/numpy     → Data processing
   └─ Redis            → Register service health

6. ML-WORKER talks to:
   ├─ RabbitMQ         → Pick jobs from queue
   ├─ ml_db            → Update job status
   ├─ data_db          → Get dataset info
   ├─ uploads/         → Read input files
   └─ saved_models/    → Save trained models

7. REDIS (Multi-role):
   ├─ Rate limit store
   ├─ Service registry (heartbeats)
   ├─ AI response cache
   └─ Session storage (future)

8. RABBITMQ (Job Queue):
   ├─ ml_service publishes training jobs
   └─ ml_worker consumes and processes
```

---

