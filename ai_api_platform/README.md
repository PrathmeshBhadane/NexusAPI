# 🚀 AI Platform Architecture Deep Dive

> A comprehensive guide to understanding the microservices architecture, Docker orchestration, design patterns, and key concepts learned from each configuration file.

---

## 🏗️ High-Level System Workflow

```mermaid
graph TD
    Client([Client / User]) -->|HTTP Port 80| Nginx[Nginx Reverse Proxy]
    Nginx -->|Routes to Port 8000| Gateway{API Gateway}
    
    Gateway -->|Validates Token| Auth[🔐 Auth Service]
    Gateway -->|Trains Models| ML[🤖 ML Service]
    Gateway -->|Generates Text| AI[🧠 AI Service]
    Gateway -->|Processes CSV| Data[📊 Data Service]
    
    Auth --> AuthDB[(PostgreSQL: Auth)]
    Data --> DataDB[(PostgreSQL: Data)]
    ML --> MLDB[(PostgreSQL: ML)]
    
    Gateway -.->|Rate Limiting & Analytics| Redis[(Redis Analytics Pipeline)]
    AI -.->|Cached Prompts| Redis
    ML -.->|Async Jobs| RabbitMQ>RabbitMQ Queue]
```

## 🔑 Service-Scoped API Keys & Analytics
The backend architecture integrates natively with the frontend **Developer Hub**. 
- **Isolated Service Scopes**: The API Gateway actively intercepts the `X-API-Key` headers on all reverse proxies. It natively identifies if a token belongs to `ML`, `AI`, `Data`, or `All` and immediately blocks (`403 Forbidden`) cross-service access attempts.
- **High-Performance Redis Telemetry**: The `rate_limiter.py` middleware tracks absolute cumulative system load natively into `Redis`, isolating sliding 1-hour quotas and absolute lifetime analytics specifically to the isolated `key_id` level.

---

## 📋 Book Chapters

| Chapter | Description | Link |
| :---: | :--- | :---: |
| 1 | 🏗️ docker-compose.yml | [Read](docs/01-docker-orchestration.md) |
| 2 | 🤖 ML Service | [Read](docs/02-ml-service.md) |
| 3 | 🗺️ Full Service Architecture Map | [Read](docs/03-architecture.md) |
| 4 | 📈 Production Deployment Architecture | [Read](docs/04-deployment.md) |
| 5 | 📚 Key Concepts Summary | [Read](docs/05-concepts.md) |
| 6 | 🔧 Quick Reference | [Read](docs/06-quick-reference.md) |
| 7 | 🚪 Gateway Service | [Read](docs/07-gateway-service.md) |
| 8 | 🔐 Auth Service | [Read](docs/08-auth-service.md) |
| 9 | 🧠 AI Service | [Read](docs/10-ai-service.md) |
| 10 | 📊 Data Service | [Read](docs/09-data-service.md) |
| 11 | 🛠️ Dockerfiles & Containerization | [Read](docs/chapter_dockerfiles---containerization.md) |
| 12 | 🎨 Nginx Configuration Design | [Read](docs/chapter_nginx-configuration-design.md) |
| 13 | 🎯 Design Patterns Used | [Read](docs/chapter_design-patterns-used.md) |
| 14 | 📈 Complete System Workflow Diagram | [Read](docs/chapter_complete-system-workflow-diagram.md) |
| 15 | 🏛️ Overall Architecture Diagram | [Read](docs/chapter_overall-architecture-diagram.md) |
| 16 | 📋 Service Communication Map | [Read](docs/chapter_service-communication-map.md) |
| 17 | 🔐 Security Layers | [Read](docs/chapter_security-layers.md) |
| 18 | 📊 Data Models | [Read](docs/chapter_data-models.md) |
| 19 | 🚀 Quick Start Guide | [Read](docs/chapter_quick-start-guide.md) |
| 20 | 🎓 Key Takeaways | [Read](docs/chapter_key-takeaways.md)


---
*This README automatically references the detailed chapters in the `docs/` directory.*
