## 🗺️ Full Service Architecture Map

<div align="center">

### Complete API Endpoint Map

```
🌐 Internet
   │
   ▼
🚪 API Gateway (port 8000) - Auth, routing, rate limiting
   │
   ├── 🔐 /auth/*   → Auth Service (port 8001)
   │   ├── POST /auth/register     - Create account
   │   ├── POST /auth/login        - Get JWT token
   │   ├── GET  /auth/me           - Current user info
   │   ├── POST /auth/validate-token - JWT verification
   │   ├── POST /keys/create       - Generate API key
   │   ├── GET  /keys/list         - List API keys
   │   └── DELETE /keys/{id}       - Revoke API key
   │
   ├── 🤖 /ml/*     → ML Service (port 8002)
   │   ├── POST /ml/train          - Start training job
   │   ├── GET  /ml/jobs/{id}      - Check job status
   │   ├── POST /ml/predict        - Run prediction
   │   ├── GET  /ml/models         - List models
   │   ├── GET  /ml/models/{id}    - Model details
   │   └── DELETE /ml/models/{id}  - Delete model
   │
   ├── 🧠 /ai/*     → AI Service (port 8003)
   │   ├── POST /ai/chat           - Multi-turn conversation
   │   ├── POST /ai/generate       - Text generation
   │   ├── POST /ai/summarize      - Text summarization
   │   ├── POST /ai/sentiment      - Sentiment analysis
   │   └── POST /ai/extract        - Data extraction
   │
   └── 📊 /data/*   → Data Service (port 8004)
       ├── POST /data/upload       - Upload CSV
       ├── GET  /data/datasets     - List datasets
       ├── GET  /data/datasets/{id} - Dataset info
       ├── POST /data/clean/{id}   - Auto data cleaning
       ├── POST /data/transform/{id} - Feature engineering
       └── GET  /data/analyze/{id} - Statistical analysis
```

</div>

---

### 🏗️ Service Dependencies & Data Flow

```
User Request → Gateway → Service → Database/Queue/External API
     │             │         │
     ▼             ▼         ▼
  Auth Check   Routing   Business Logic
  Rate Limit   Logging   Async Processing
  API Key      Monitoring Persistence
```

**Key Technologies per Service:**
- **Auth Service**: JWT tokens, API keys, PostgreSQL
- **ML Service**: scikit-learn, RabbitMQ, joblib, PostgreSQL
- **AI Service**: Groq API, Redis caching, async processing
- **Data Service**: pandas, numpy, PostgreSQL, data validation
- **Gateway**: FastAPI, Redis (rate limiting + service registry)

---

