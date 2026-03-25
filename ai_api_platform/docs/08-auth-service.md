## 🔐 Auth Service

*File: `auth-service/` (app/, Dockerfile, requirements.txt)*  
*Port: 8001*  
*Purpose: User authentication, JWT tokens, API key management*

### 🎯 Auth Service Concepts Learned

| Concept | Icon | Implementation |
|---------|------|-----------------|
| **JWT Token Generation** | 🎫 | python-jose library for secure token creation |
| **Password Hashing** | 🔒 | bcrypt for secure password storage |
| **SQLAlchemy ORM** | 🗄️ | Declarative models for User & API Key tables |
| **Async Database** | ⚡ | asyncpg for non-blocking PostgreSQL |
| **Database Migrations** | 📚 | Alembic for schema version control |
| **Service Registry** | 💾 | Self-registers in Redis on startup |
| **Token Expiration** | ⏰ | JWT tokens expire in 30 minutes |
| **Lifespan Context** | 🔄 | Manages DB engine lifecycle |
| **Two Auth Methods** | 🔑 | JWT tokens + API keys for different client types |

### 🏗️ Auth Service Architecture

```
┌─────────────────────────────────────┐
│    Auth Service (FastAPI)           │
└──────┬──────────────────────────────┘
       │
   ┌───┴────────┬──────────────┐
   │            │              │
   ▼            ▼              ▼
┌──────┐   ┌────────┐   ┌─────────┐
│ User │   │ API    │   │ Crypto  │
│ Mgmt │   │ Keys   │   │ Ops     │
└──┬───┘   └───┬────┘   └────┬────┘
   │           │             │
   └─────┬─────┴─────┬───────┘
         │           │
         ▼           ▼
    ┌─────────────────────────┐
    │   PostgreSQL auth_db    │
    │                         │
    │ Tables:                 │
    │ • users (id, email)     │
    │ • api_keys (key, perms) │
    └─────────────────────────┘
```

### 🔑 Authentication Flow

```
Register Flow:
    POST /auth/register {email, password}
    → Hash password with bcrypt
    → Create user in auth_db
    → Return user_id

Login Flow:
    POST /auth/login {email, password}
    → Find user in auth_db
    → Compare password with bcrypt
    → Generate JWT token (expires 30 min)
    → Return token

Token Validation Flow:
    POST /auth/validate-token {token}
    → Verify JWT signature
    → Check expiration
    → Decode payload
    → Return user_id + permissions
    
API Key Validation:
    POST /keys/validate {api_key}
    → Lookup key in api_keys table
    → Check if active
    → Return permissions
```

### 💾 Requirements Analysis

```
fastapi==0.111.0
uvicorn[standard]==0.29.0
sqlalchemy==2.0.30              ← ORM for database models
asyncpg==0.29.0                 ← PostgreSQL async driver
alembic==1.13.1                 ← Database migrations
pydantic-settings==2.2.1
pydantic[email]==2.7.1         ← Email validation
python-jose[cryptography]      ← JWT token creation/verification
passlib==1.7.4                 ← Password hashing library
bcrypt==4.0.1                  ← Secure password hashing
redis==5.0.4
httpx==0.27.0
python-multipart==0.0.9
```

---

