# 🖥️ InfraMonitor SRE

Real-time local infrastructure monitoring system with an agent-based architecture. Built as an SRE portfolio project demonstrating observability, alerting, and data-driven decision making.

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=flat&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat&logo=typescript&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat&logo=postgresql&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)

## Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Agent      │────▶│  Backend API │◀────│   Frontend   │
│  (Python)    │     │  (FastAPI)   │     │ (React + TS) │
│              │     │              │     │              │
│ • CPU        │     │ • REST API   │     │ • Dashboard  │
│ • Memory     │     │ • Analysis   │     │ • Charts     │
│ • Disk       │     │ • Alerting   │     │ • Time Range │
│ • Processes  │     │ • Storage    │     │ • Insights   │
└──────────────┘     └──────┬───────┘     └──────────────┘
                            │
                     ┌──────▼───────┐
                     │  PostgreSQL  │
                     │  (or SQLite) │
                     └──────────────┘
```

## Features

- **Real-time Monitoring** — CPU, Memory, and Disk utilization collected every 5 seconds
- **Time Range Selector** — View data across 1H, 6H, 24H, 3D, 7D, or 14D windows
- **Automated Insights** — Threshold-based analysis with severity levels (INFO, WARNING, CRITICAL)
- **Interactive Dashboard** — Responsive charts with sparklines and area gradients
- **Data Retention** — Automatic cleanup of data older than 14 days
- **Graceful Fallback** — Frontend works with mock data when backend is unavailable

## Quick Start

### 1. Start the Database (Optional — falls back to SQLite)

```bash
docker compose up -d
```

### 2. Start the Backend API

```bash
pip install -r backend/requirements.txt
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Start the Monitoring Agent

```bash
pip install -r agent/requirements.txt
python -m agent.main
```

### 4. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

## Tech Stack

| Layer     | Technology                        |
|-----------|-----------------------------------|
| Frontend  | React 19, TypeScript, Recharts, Tailwind CSS, Lucide Icons |
| Backend   | FastAPI, SQLAlchemy, Pydantic     |
| Agent     | Python, psutil                    |
| Database  | PostgreSQL 16 (Docker) / SQLite   |

## Project Structure

```
infra-monitor/
├── agent/                  # System monitoring agent
│   ├── collectors/         # CPU, Memory, Disk, Process collectors
│   ├── clients/            # API client for backend communication
│   ├── core/               # Agent orchestrator
│   └── config.yaml         # Agent configuration
├── backend/                # FastAPI REST API
│   ├── core/               # Configuration
│   ├── models/             # SQLAlchemy ORM models
│   ├── schemas/            # Pydantic request/response schemas
│   └── services/           # Storage, Analysis, Alerting engines
├── frontend/               # React + TypeScript dashboard
│   └── src/
│       └── App.tsx         # Main dashboard component
└── docker-compose.yml      # PostgreSQL container
```

## License

MIT
