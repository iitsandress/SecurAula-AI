# EduMon Project Makefile

.PHONY: help install install-dev test test-coverage lint format clean build-agent build-docker run-dev run-prod stop-dev docs

# Default target
help:
	@echo "EduMon Project Commands:"
	@echo ""
	@echo "Development:"
	@echo "  install       Install production dependencies"
	@echo "  install-dev   Install development dependencies"
	@echo "  run-dev       Run development server"
	@echo "  run-agent     Run agent in development mode"
	@echo ""
	@echo "Testing:"
	@echo "  test          Run tests"
	@echo "  test-coverage Run tests with coverage report"
	@echo "  lint          Run linting checks"
	@echo "  format        Format code"
	@echo ""
	@echo "Building:"
	@echo "  build-agent   Build agent executable"
	@echo "  build-docker  Build Docker images"
	@echo ""
	@echo "Production:"
	@echo "  run-prod      Run production environment"
	@echo "  stop-prod     Stop production environment"
	@echo ""
	@echo "Utilities:"
	@echo "  clean         Clean build artifacts"
	@echo "  docs          Generate documentation"

# Installation
install:
	cd backend && pip install -r requirements.txt
	cd agent && pip install -r requirements.txt

install-dev: install
	cd backend && pip install pytest pytest-cov black flake8 mypy
	cd agent && pip install pytest black flake8

# Development
run-dev:
	cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-agent:
	cd agent && python main.py

# Testing
test:
	cd backend && python -m pytest tests/ -v
	cd agent && python -m pytest tests/ -v

test-coverage:
	cd backend && python -m pytest tests/ --cov=app --cov-report=html --cov-report=term
	@echo "Coverage report generated in backend/htmlcov/"

# Code quality
lint:
	cd backend && flake8 app/ tests/
	cd agent && flake8 *.py core/ ui/

format:
	cd backend && black app/ tests/
	cd agent && black *.py core/ ui/

# Building
build-agent:
	cd agent && pyinstaller --onedir --windowed --name EduMonAgent main.py
	@echo "Agent executable built in agent/dist/"

build-docker:
	docker-compose -f docker/docker-compose.yml build

# Production
run-prod:
	docker-compose -f docker/docker-compose.yml --profile production up -d

stop-prod:
	docker-compose -f docker/docker-compose.yml down

# Utilities
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf backend/htmlcov/
	rm -rf agent/dist/
	rm -rf agent/build/
	rm -f backend/test.db
	rm -f agent/test.db

docs:
	@echo "Generating documentation..."
	@echo "API documentation available at http://localhost:8000/docs when server is running"

# Database management
db-init:
	cd backend && python -c "from app.core.database import create_tables; create_tables()"

db-reset:
	cd backend && python -c "from app.core.database import drop_tables, create_tables; drop_tables(); create_tables()"

# Security
security-check:
	cd backend && pip install safety bandit
	cd backend && safety check
	cd backend && bandit -r app/

# Performance testing
load-test:
	@echo "Running load tests..."
	@echo "Install locust first: pip install locust"
	# locust -f tests/load_test.py --host=http://localhost:8000

# Backup
backup:
	@echo "Creating backup..."
	mkdir -p backups
	tar -czf backups/edumon-backup-$(shell date +%Y%m%d-%H%M%S).tar.gz \
		--exclude='.git' \
		--exclude='__pycache__' \
		--exclude='*.pyc' \
		--exclude='node_modules' \
		--exclude='dist' \
		--exclude='build' \
		.

# Environment setup
setup-env:
	cp docker/.env.example docker/.env
	@echo "Environment file created. Please edit docker/.env with your settings."

# SSL certificate generation (for development)
generate-ssl:
	mkdir -p ssl
	openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes \
		-subj "/C=ES/ST=Madrid/L=Madrid/O=EduMon/CN=localhost"
	@echo "SSL certificates generated in ssl/ directory"