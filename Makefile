.PHONY: help setup start stop restart logs clean test

help:
	@echo "Documentation Support Agent - Available Commands:"
	@echo ""
	@echo "  make setup     - Initial setup (copy .env, install dependencies)"
	@echo "  make start     - Start all services with Docker Compose"
	@echo "  make stop      - Stop all services"
	@echo "  make restart   - Restart all services"
	@echo "  make logs      - View logs from all services"
	@echo "  make clean     - Remove all containers, volumes, and cache"
	@echo "  make test      - Run tests"
	@echo ""
	@echo "  Development commands:"
	@echo "  make dev-backend   - Run backend locally (without Docker)"
	@echo "  make dev-frontend  - Run frontend locally (without Docker)"

setup:
	@echo "Setting up environment..."
	@if [ ! -f backend/.env ]; then \
		cp backend/.env.example backend/.env; \
		echo "Created backend/.env - Please update with your API keys"; \
	fi
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Created .env - Please update if needed"; \
	fi
	@echo "Setup complete! Please edit backend/.env with your API keys."

start:
	@echo "Starting all services..."
	docker-compose up -d
	@echo "Services started!"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend API: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"

stop:
	@echo "Stopping all services..."
	docker-compose down

restart:
	@echo "Restarting all services..."
	docker-compose restart

logs:
	docker-compose logs -f

clean:
	@echo "Cleaning up..."
	docker-compose down -v
	rm -rf backend/cache
	rm -rf backend/__pycache__
	find backend -type d -name "__pycache__" -exec rm -rf {} +
	@echo "Cleanup complete!"

test:
	@echo "Running tests..."
	cd backend && pytest
	cd frontend && npm test

dev-backend:
	@echo "Starting backend in development mode..."
	cd backend && python -m venv venv && \
	. venv/bin/activate && \
	pip install -r requirements.txt && \
	uvicorn main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	@echo "Starting frontend in development mode..."
	cd frontend && npm install && npm run dev

db-init:
	@echo "Initializing database..."
	docker-compose up -d postgres
	@sleep 5
	@echo "Database ready!"

db-reset:
	@echo "Resetting database..."
	docker-compose down -v postgres
	docker-compose up -d postgres
	@sleep 5
	@echo "Database reset complete!"

