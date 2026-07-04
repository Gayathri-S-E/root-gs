# ROOTGS — AI Operating System for Smart Agriculture

ROOTGS is a production-grade, hackathon-winning AI operating system for smart agriculture, designed to act like a personal AI scientist on every farm. It integrates computer vision for crop diagnostics, real-time weather alerts, smart water calculations, government schemes matchmaking, and chatbot assistance.

## 🚀 Quick Start with Docker Compose

You can launch the complete ecosystem (FastAPI, React web application, PostgreSQL database, Redis, and Nginx reverse proxy) in a single command.

### Prerequisites

1. Install [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/).
2. Copy the example environment file and configure your API keys (optional but recommended for real AI processing):
   ```bash
   cp .env.example .env
   ```

### Running the Project

Run the following command to build and run the services:
```bash
docker-compose up --build
```

Access the systems at:
- **Frontend Dashboard**: `http://localhost:3000` (or proxy on port `80` / `http://localhost`)
- **API Server & Interactive Swagger Docs**: `http://localhost:8000/docs`
- **Nginx Entrypoint**: `http://localhost/`

---

## 🛠️ Tech Stack & Folders

### 1. Backend (`backend/`)
- **FastAPI (Python)**: High performance async endpoints.
- **SQLAlchemy (ORM)**: Database models.
- **Alembic**: Database schema migrations.
- **Google Gemini 1.5 Pro**: Vision analysis and chatbot reasoning.

### 2. Frontend (`frontend/`)
- **React + TypeScript + Vite**: Responsive Single Page App.
- **Zustand**: Clean state management.
- **React Query**: API request caching and hook binding.
- **Framer Motion**: Smooth agricultural theme micro-animations.

### 3. Mobile (`mobile/`)
- **Flutter**: Android and iOS apps.
- **Riverpod**: Architecture state providers.
- **Dio**: HTTP networking client.

---

## 👨‍🌾 Database Seeding

Populate the database with default crop indexes, government schemes, and market prices.

```bash
docker-compose exec backend python scripts/seed.py
```

### Demo Login credentials
- **Email**: `farmer@rootgs.demo`
- **Password**: `demo1234`
