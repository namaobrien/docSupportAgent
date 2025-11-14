# Documentation Support Agent

An AI-powered system that analyzes GitHub issues, identifies documentation problems, and iteratively improves documentation quality using Claude Sonnet 4.5.

## Features

- **Intelligent Issue Analysis**: Automatically identifies documentation-related issues
- **Documentation Search**: Finds relevant documentation pages on code.claude.com
- **Codebase Verification**: Deep analysis to prevent hallucinations
- **Iterative Improvement**: Up to 20 iterations with LLM judge feedback
- **Quality Rubric**: 6-criteria evaluation system for technical documentation
- **Review Queue**: Flags issues requiring human intervention
- **React Dashboard**: Clean, actionable metrics and visualizations

## Architecture

- **Backend**: Python FastAPI + PostgreSQL + Anthropic Claude API
- **Frontend**: React with Vite
- **Database**: PostgreSQL with SQLAlchemy ORM
- **AI Model**: Claude Sonnet 4.5 for all agents

## Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 16+
- Docker & Docker Compose (optional)

### Environment Variables

Copy `backend/.env.example` to `backend/.env` and fill in:

```bash
ANTHROPIC_API_KEY=your_key_here
GITHUB_TOKEN=your_github_token_here
POSTGRES_CONNECTION_STRING=postgresql://user:pass@localhost:5432/doc_support_agent
```

### Quick Start with Docker

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Access:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Manual Setup

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

#### Database

```bash
# Create database
createdb doc_support_agent

# Migrations will run automatically on startup
```

## Usage

1. Open the frontend at http://localhost:3000
2. Select a date range to search for issues (today, last 7/30 days, etc.)
3. Click on an issue or manually enter an issue number
4. Click "Analyze Issue" to start the agent
5. Watch real-time progress as the agent:
   - Classifies the issue
   - Searches for relevant documentation
   - Verifies against codebase
   - Rewrites documentation
   - Gets judge feedback
   - Iterates up to 20 times
6. View results with rubric scores for each iteration
7. Check the review queue for flagged issues

## Quality Rubric

Documentation is scored on:

1. **Accuracy & Correctness** (30%) - Verified against codebase
2. **Clarity & Readability** (20%) - Clear language and flow
3. **Completeness** (20%) - All necessary information
4. **Code Examples** (15%) - Working, practical examples
5. **Structure** (10%) - Organization and hierarchy
6. **Discoverability** (5%) - Keywords and cross-references

## Project Structure

```
.
├── backend/
│   ├── agents/          # AI agents (classifier, rewriter, judge, etc.)
│   ├── api/             # FastAPI routes
│   ├── database/        # SQLAlchemy models and connection
│   ├── services/        # External services (GitHub, docs scraper, etc.)
│   ├── main.py          # FastAPI app entry point
│   └── config.py        # Configuration
├── frontend/
│   └── src/
│       ├── components/  # React components
│       ├── services/    # API client
│       └── styles/      # Theme and styling
└── docker-compose.yml   # Docker setup
```

## Development

### Running Tests

```bash
cd backend
pytest

cd ../frontend
npm test
```

### Database Migrations

```bash
cd backend
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## License

MIT

