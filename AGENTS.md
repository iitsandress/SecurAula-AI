# Repository Guidelines

## Project Structure & Module Organization

EduMon is organized into distinct components: `edumon/backend/` contains the FastAPI server with API endpoints, models, and services; `edumon/agent/` houses the PyQt6 client application with core logic and UI components; `edumon/docker/` provides containerization configs; and `edumon/server/` contains the standalone server implementation. Root-level scripts `run_server.py` and `run_agent.py` provide easy entry points for both components.

## Build, Test, and Development Commands

```bash
# Install dependencies and run development server
make install-dev
make run-dev

# Run agent in development mode
make run-agent

# Run tests with coverage
make test-coverage

# Build agent executable
make build-agent

# Docker deployment
make build-docker
make run-prod
```

## Coding Style & Naming Conventions

- **Indentation**: 4 spaces (Python standard)
- **File naming**: snake_case for Python files, kebab-case for configs
- **Function/variable naming**: snake_case following PEP 8
- **Class naming**: PascalCase for classes, descriptive names for models
- **Linting**: Uses black for formatting, flake8 for linting, mypy for type checking

## Testing Guidelines

- **Framework**: pytest for both backend and agent components
- **Test files**: Located in `backend/tests/` and `agent/tests/`, following `test_*.py` pattern
- **Running tests**: `make test` for all tests, `make test-coverage` for coverage reports
- **Coverage**: HTML reports generated in `backend/htmlcov/`

## Commit & Pull Request Guidelines

- **Commit format**: Descriptive messages focusing on educational monitoring features
- **PR process**: Include tests for new features, ensure all checks pass
- **Branch naming**: feature/description or bugfix/description pattern
- **Code review**: Focus on privacy compliance and educational use case alignment

---

# Repository Tour

## 🎯 What This Repository Does

EduMon is an educational monitoring system with explicit consent, designed for computer classrooms. It allows teachers to obtain a basic overview of equipment status during classes while respecting privacy and maintaining complete transparency.

**Key responsibilities:**
- Real-time monitoring of student computers (CPU, RAM, disk, network metrics)
- Consent-based data collection with full transparency
- Web dashboard for teachers to monitor classroom status
- PyQt6 agent application for students with modern interface

---

## 🏗️ Architecture Overview

### System Context
```
[Student Computers] → [EduMon Agent (PyQt6)] → [FastAPI Backend] → [SQLite/PostgreSQL]
                                                      ↓
[Teacher Dashboard] ← [Web Interface] ← [REST API + WebSockets]
```

### Key Components
- **FastAPI Backend** - REST API server handling registration, heartbeats, and metrics collection
- **PyQt6 Agent** - Student-side application collecting system metrics with consent management
- **Web Dashboard** - Teacher interface for real-time monitoring and classroom management
- **Storage Layer** - JSON-based storage (development) or PostgreSQL (production)

### Data Flow
1. Student runs agent and provides explicit consent for monitoring
2. Agent registers with server and begins sending heartbeat metrics every 15 seconds
3. Server stores metrics and provides real-time status via web dashboard
4. Teacher monitors classroom status through responsive web interface
5. Students can stop monitoring at any time, data is automatically cleaned up

---

## 📁 Project Structure [Partial Directory Tree]

```
edumon/
├── backend/                # FastAPI server application
│   ├── app/
│   │   ├── api/           # REST API endpoints
│   │   ├── core/          # Configuration, database, security
│   │   ├── models/        # SQLAlchemy models and Pydantic schemas
│   │   ├── services/      # Business logic and data services
│   │   ├── templates/     # Jinja2 HTML templates
│   │   └── main.py        # FastAPI application entry point
│   └── tests/             # Backend unit tests
├── agent/                 # PyQt6 student agent
│   ├── core/              # Agent core logic and metrics collection
│   ├── ui/                # PyQt6 GUI components
│   ├── main.py            # Agent entry point with CLI options
│   └── config.example.json # Agent configuration template
├── docker/                # Docker deployment configuration
│   ├── docker-compose.yml # Multi-service orchestration
│   ├── Dockerfile.backend # Backend container definition
│   └── .env.example       # Environment variables template
├── server/                # Standalone server implementation
├── scripts/               # Utility and deployment scripts
├── Makefile              # Development and build commands
├── pyproject.toml        # Python project configuration
└── requirements-*.txt    # Dependency specifications
```

### Key Files to Know

| File | Purpose | When You'd Touch It |
|------|---------|---------------------|
| `backend/app/main.py` | FastAPI application entry point | Adding new API endpoints |
| `backend/app/core/config.py` | Server configuration settings | Changing API keys or data paths |
| `agent/main.py` | Agent application entry point | Modifying agent startup behavior |
| `agent/core/agent_core.py` | Core agent functionality | Changing metrics collection logic |
| `pyproject.toml` | Project metadata and dependencies | Adding new Python packages |
| `Makefile` | Development commands | Adding new build or test targets |
| `docker/docker-compose.yml` | Production deployment setup | Configuring containerized deployment |

---

## 🔧 Technology Stack

### Core Technologies
- **Language:** Python 3.11+ - Modern Python with type hints and async support
- **Backend Framework:** FastAPI 0.110+ - High-performance async web framework with automatic API docs
- **GUI Framework:** PyQt6 6.5+ - Modern cross-platform GUI toolkit for the agent
- **Database:** SQLite (development) / PostgreSQL (production) - Flexible data storage options

### Key Libraries
- **pydantic** - Data validation and settings management with type safety
- **SQLAlchemy** - Python SQL toolkit and ORM for database operations
- **psutil** - Cross-platform system and process monitoring
- **uvicorn** - ASGI server for running FastAPI applications
- **requests** - HTTP library for agent-server communication

### Development Tools
- **pytest** - Testing framework with fixtures and coverage reporting
- **black** - Code formatting for consistent Python style
- **flake8** - Linting for code quality and PEP 8 compliance
- **mypy** - Static type checking for Python
- **Docker** - Containerization for consistent deployment

---

## 🌐 External Dependencies

### Required Services
- **HTTP Server** - FastAPI backend serves REST API and web dashboard
- **System Metrics** - psutil library provides cross-platform system monitoring
- **File Storage** - JSON files (development) or PostgreSQL database (production)

### Optional Integrations
- **Docker** - Container orchestration for production deployment
- **Prometheus + Grafana** - Advanced monitoring and visualization (production profile)
- **Redis** - Caching and session storage (production profile)

### Environment Variables

```bash
# Required
EDUMON_API_KEY=          # API key for agent authentication (default: S1R4X)
SECRET_KEY=              # JWT secret key for secure sessions
DATABASE_URL=            # Database connection string

# Optional
DEBUG=                   # Enable debug mode (default: false)
DATA_RETENTION_DAYS=     # How long to keep metrics data (default: 30)
SSL_CERTFILE=            # SSL certificate path for HTTPS
SSL_KEYFILE=             # SSL private key path for HTTPS
```

---

## 🔄 Common Workflows

### Student Agent Registration and Monitoring
1. Student runs agent (`python agent/main.py` or executable)
2. Agent displays consent dialog with clear data collection terms
3. Upon consent, agent registers with server using device ID and classroom info
4. Agent begins sending heartbeat with system metrics every 15 seconds
5. Student can stop monitoring at any time via GUI or Ctrl+C

**Code path:** `agent/main.py` → `agent/core/agent_core.py` → `backend/app/main.py` → `backend/app/services/storage.py`

### Teacher Dashboard Monitoring
1. Teacher starts server (`python run_server.py` or `make run-dev`)
2. Accesses dashboard at `http://localhost:8000/dashboard?api_key=S1R4X`
3. Views real-time metrics from connected students
4. Can filter by classroom and view individual client details
5. Monitors connectivity status and system performance metrics

**Code path:** `backend/app/main.py` → `backend/app/templates/dashboard.html` → `/api/v1/clients/status` endpoint

---

## 📈 Performance & Scale

### Performance Considerations
- **Heartbeat Interval:** 15-second intervals balance real-time monitoring with server load
- **Data Retention:** Configurable cleanup of old metrics to manage storage growth
- **Async Processing:** FastAPI's async capabilities handle multiple concurrent agent connections

### Monitoring
- **Health Endpoint:** `/health` provides server status and configuration validation
- **Client Status API:** Real-time endpoint showing online/offline status and metrics
- **Audit Logging:** Complete audit trail of all registration, heartbeat, and unregistration events

---

## 🚨 Things to Be Careful About

### 🔒 Security Considerations
- **API Key Authentication:** All agent communications require valid API key (configurable, default: S1R4X)
- **Consent Management:** Explicit user consent required before any data collection begins
- **Data Minimization:** Only collects essential system metrics, never personal data or file contents
- **Audit Trail:** Complete logging of all actions for transparency and compliance

### Privacy by Design
- **No Screenshots:** System never captures screen content or visual data
- **No Keylogging:** No keyboard or mouse input monitoring
- **No File Access:** Only system metrics, never file contents or personal data
- **Transparent Collection:** Clear disclosure of exactly what data is collected
- **User Control:** Students can stop monitoring at any time without consequences

*Updated at: 2024-12-19 UTC*