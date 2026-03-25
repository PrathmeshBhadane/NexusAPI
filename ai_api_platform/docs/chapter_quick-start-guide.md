## 🚀 Quick Start Guide

**Prerequisites:**
- Docker and Docker Compose installed
- Python 3.11+
- Git

**Clone and Start:**
```bash
# Clone repository
git clone <repo-url>
cd aiplatform

# Start all services
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f gateway
```

**Test the Platform:**
```bash
# 1. Register user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"secure123"}'

# 2. Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"secure123"}'

# 3. Use JWT token to access services
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer <token>"

# 4. Upload dataset
curl -X POST http://localhost:8000/data/upload \
  -H "Authorization: Bearer <token>" \
  -F "file=@data.csv"

# 5. Train ML model
curl -X POST http://localhost:8000/ml/train \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"dataset_id":"<id>","model_type":"random_forest"}'
```

---

