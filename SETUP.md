# Documentation Support Agent - Setup Guide

## Prerequisites

Ensure you have the following installed:
- **Docker** and **Docker Compose** (recommended)
- **Python 3.11+** (for local development)
- **Node.js 18+** (for local development)
- **PostgreSQL 16+** (if running without Docker)

## Quick Start with Docker

### 1. Clone and Setup

```bash
# Copy environment files
make setup

# Edit backend/.env with your API keys
nano backend/.env
```

### 2. Configure API Keys

Edit `backend/.env` and add your keys:

```bash
ANTHROPIC_API_KEY=sk-ant-xxxxx
GITHUB_TOKEN=ghp_xxxxx
```

### 3. Start Services

```bash
make start
```

This will start:
- PostgreSQL database on port 5432
- Backend API on port 8000
- Frontend on port 3000

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Manual Setup (Without Docker)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
nano .env  # Add your API keys

# Start PostgreSQL (if not using Docker)
createdb doc_support_agent

# Run migrations (tables are created automatically on startup)

# Start server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure API URL (optional, defaults to localhost:8000)
echo "VITE_API_URL=http://localhost:8000" > .env

# Start development server
npm run dev
```

## Configuration

### Required Environment Variables

#### Anthropic API Key
Get your API key from https://console.anthropic.com/

```bash
ANTHROPIC_API_KEY=sk-ant-xxxxx
```

#### GitHub Token
Create a personal access token at https://github.com/settings/tokens

Required scopes:
- `repo` (to read issues)
- `read:org` (if analyzing private repos)

```bash
GITHUB_TOKEN=ghp_xxxxx
```

#### PostgreSQL Connection
```bash
POSTGRES_CONNECTION_STRING=postgresql://user:password@host:port/database
```

### Optional Configuration

```bash
# Agent behavior
MAX_ITERATIONS=20
IMPROVEMENT_ITERATIONS=3
CLAUDE_MODEL=claude-sonnet-4-20250514

# Repository settings
CLAUDE_CODE_REPO_URL=https://github.com/anthropics/claude-code
DOCS_BASE_URL=https://code.claude.com/docs/en/
REPO_CACHE_DIR=./cache/repos
```

## Database Setup

### With Docker
Database is automatically initialized when you run `make start`.

### Manual Setup
```bash
# Create database
createdb doc_support_agent

# Tables are created automatically on first run
# Or run migrations manually:
cd backend
python -c "from database.connection import init_db; init_db()"
```

## Troubleshooting

### Database Connection Issues
```bash
# Check if PostgreSQL is running
docker-compose ps

# View database logs
docker-compose logs postgres

# Reset database
make db-reset
```

### Backend Issues
```bash
# View backend logs
docker-compose logs backend

# Restart backend
docker-compose restart backend

# Check if ports are available
lsof -i :8000
```

### Frontend Issues
```bash
# View frontend logs
docker-compose logs frontend

# Restart frontend
docker-compose restart frontend

# Clear npm cache
cd frontend && npm cache clean --force
```

### API Key Issues
- Ensure your Anthropic API key is valid and has sufficient credits
- Verify GitHub token has correct permissions
- Check that environment variables are loaded (restart services after changing .env)

## Development Workflow

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Watching Logs
```bash
# All services
make logs

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Stopping Services
```bash
# Stop all services
make stop

# Stop and remove volumes
make clean
```

## Production Deployment

### Environment Variables
Ensure all production environment variables are set:
- Use strong database passwords
- Use production-grade PostgreSQL instance
- Set proper CORS origins in backend
- Use environment-specific API URLs

### Docker Compose Production
```bash
# Use production docker-compose file
docker-compose -f docker-compose.prod.yml up -d
```

### Scaling
- Backend can be scaled horizontally
- Use Redis for analysis status tracking (instead of in-memory)
- Consider using Celery for background tasks
- Set up load balancer for multiple backend instances

## Next Steps

1. Configure your API keys in `backend/.env`
2. Start the services with `make start`
3. Open http://localhost:3000 in your browser
4. Select a date range to search for documentation issues
5. Analyze issues and view results
6. Check the review queue for flagged items

## Support

For issues or questions:
- Check the logs with `make logs`
- Review the API documentation at http://localhost:8000/docs
- Ensure all prerequisites are installed
- Verify API keys are valid and properly configured

