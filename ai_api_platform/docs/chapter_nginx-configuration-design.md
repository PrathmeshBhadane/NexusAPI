## 🎨 Nginx Configuration Design

*File: `nginx/nginx.conf`*

### 🎯 Nginx Concepts Learned

| Concept | Icon | Implementation |
|---------|------|-----------------|
| **Reverse Proxy Pattern** | 🔄 | upstream block routing to gateway |
| **Load Balancing** | ⚖️ | Can add multiple gateway servers |
| **Header Preservation** | 📨 | proxy_set_header for client info |
| **Timeout Configuration** | ⏱️ | 60s for long-running requests |
| **SSL/TLS Termination** | 🔐 | Can add SSL certificate handling |
| **Gzip Compression** | 📦 | Can add gzip for response compression |

### 🏗️ Nginx Request Flow

```
┌─────────────────────────────────────┐
│      Internet Client Request        │
│      (127.0.0.1:80 or :443)        │
└────────────────┬────────────────────┘
                 │
                 ▼
        ┌─────────────────┐
        │  Nginx Server   │  Port 80
        │  worker_conn:1K │
        └────────┬────────┘
                 │
    ┌────────────┼────────────┐
    │     Proxy Pass          │
    │  to:gateway:8000        │
    └────────────┼────────────┘
                 │
    ┌────────────▼─────────────────┐
    │  Add Headers:                │
    │  • Host: original host        │
    │  • X-Real-IP: client IP       │
    │  • X-Forwarded-For: full path │
    │  • X-Forwarded-Proto: http/s  │
    └────────────┬──────────────────┘
                 │
                 ▼
        ┌────────────────┐
        │ Gateway Service│ Port 8000
        └────────────────┘
```

### 💾 Nginx Configuration Analysis

```nginx
events {
    worker_connections 1024;  ← Max concurrent connections per worker
}

http {
    upstream gateway {
        server gateway:8000;   ← Can add multiple for load balancing
                               ← Example: server gateway:8000 weight=50;
    }

    server {
        listen 80;             ← Port that external world accesses
        
        location / {
            proxy_pass http://gateway;            ← Forward to gateway
            proxy_set_header Host $host;          ← Preserve original host
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_read_timeout 60s;   ← Wait 60s for response
            proxy_connect_timeout 60s; ← Wait 60s to connect
        }
    }
}
```

---

