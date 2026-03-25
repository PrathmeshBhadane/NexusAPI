# AI Developer Portal (Frontend)

This is the official Next.js 15 (App Router) Developer Hub for the AI Microservices Platform, wrapped in a customized **Space Blue Glassmorphism** Tailwind CSS v4 design system.

## 🌟 Core Features

- **Service-Scoped Keys**: Students and developers can generate specialized API keys locked explicitly to specific microservices (e.g. `Machine Learning Jobs Only` or `Data Processing Engine`).
- **Real-Time Bandwidth Analytics**: The dashboard interfaces directly with the backend API Gateway's Redis pipeline to display live visual gauges of API Key usage (Hourly limit vs. Lifetime hits).
- **Interactive Documentation**: Auto-generating `cURL` commands for the AI, ML, and Data microservices seamlessly powered by the user's generated active Bearer tokens.
- **Secure Sub-Routing**: Native Next.js API interceptors detect orphaned or dead `401 Unauthorized` sessions, instantly wiping local cache and cleanly redirecting to the login flow.

## 🛠️ Technology Stack
- **Framework**: Next.js 15 (React 19)
- **Styling**: Tailwind CSS v4
- **Language**: TypeScript
- **Auth**: JWT (Bearer Tokens) + LocalStorage
- **Animations**: Tailwind `animate-in`, native smooth drops.

## 🚀 Getting Started

### 1. Requirements
Ensure the Python API Gateway backend is actively running on `localhost:8000`.

### 2. Installation
Navigate to the `frontend` directory and install pure Node packages:

```bash
npm install
```

### 3. Launch Development Server
```bash
npm run dev
```

Navigate your browser to [http://localhost:3000](http://localhost:3000). If you haven't yet, follow the "Get Started" prompt to hit the Auth-Service and securely register a new User Account in PostgreSQL!
