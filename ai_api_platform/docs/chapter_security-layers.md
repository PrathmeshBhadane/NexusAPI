## 🔐 Security Layers

```
Layer 1: TLS/SSL
┌─────────────────────────────────────┐
│ Nginx terminates SSL (future)        │
│ Encrypts: Internet ↔ Nginx           │
└─────────────────────────────────────┘

Layer 2: API Gateway Auth
┌─────────────────────────────────────┐
│ Gateway validates every request:     │
│ • JWT token (Bearer) or              │
│ • API key (X-API-Key header)         │
│ Rejects: 401/403 if invalid         │
└─────────────────────────────────────┘

Layer 3: Rate Limiting
┌─────────────────────────────────────┐
│ Gateway tracks requests per API key  │
│ • Max 100 requests/hour              │
│ • Reject: 429 if exceeded           │
│ • Prevents: Brute force attacks      │
└─────────────────────────────────────┘

Layer 4: Password Hashing
┌─────────────────────────────────────┐
│ Auth Service uses bcrypt:            │
│ • Never stores plain passwords       │
│ • Verify: bcrypt.checkpw()           │
│ • Compare user input vs stored hash  │
└─────────────────────────────────────┘

Layer 5: JWT Tokens
┌─────────────────────────────────────┐
│ Stateless token authentication:      │
│ • Token expires in 30 minutes        │
│ • Signed with SECRET_KEY             │
│ • Cannot be forged without key       │
│ • Gateway verifies signature         │
└─────────────────────────────────────┘

Layer 6: Database Passwords
┌─────────────────────────────────────┐
│ PostgreSQL protected by:             │
│ • Network isolation (Docker bridge)  │
│ • Username + password authentication │
│ • Each service has own DB + creds    │
│ • No cross-service DB access        │
└─────────────────────────────────────┘

Layer 7: Service Isolation
┌─────────────────────────────────────┐
│ Services run in own containers:      │
│ • Network: isolated bridge network   │
│ • Filesystem: read-only root         │
│ • No privilege escalation            │
│ • Resource limits (CPU, memory)      │
└─────────────────────────────────────┘
```

---

