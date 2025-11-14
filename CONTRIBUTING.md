# Contributing to Documentation Support Agent

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## Development Setup

1. Fork and clone the repository
2. Follow the setup instructions in `SETUP.md`
3. Create a new branch for your feature: `git checkout -b feature/my-feature`

## Code Style

### Python (Backend)
- Follow PEP 8
- Use type hints where possible
- Write docstrings for all public functions/classes
- Maximum line length: 100 characters

### JavaScript/React (Frontend)
- Use functional components with hooks
- Follow ESLint configuration
- Use meaningful variable names
- Keep components focused and small

## Testing

### Backend Tests
```bash
cd backend
pytest
pytest --cov  # with coverage
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Commit Messages

Follow conventional commits format:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting)
- `refactor:` Code refactoring
- `test:` Test changes
- `chore:` Build/tooling changes

Example:
```
feat: add iteration comparison view
fix: resolve scoring calculation bug
docs: update setup instructions
```

## Pull Request Process

1. Update documentation if needed
2. Add tests for new features
3. Ensure all tests pass
4. Update CHANGELOG.md
5. Submit PR with clear description

## Project Structure

See `ARCHITECTURE.md` for detailed system architecture.

Key directories:
- `backend/agents/` - AI agent implementations
- `backend/services/` - External service integrations
- `backend/api/` - REST API endpoints
- `frontend/src/components/` - React components
- `frontend/src/services/` - API client

## Adding New Features

### New Agent
1. Create agent file in `backend/agents/`
2. Implement agent class with async methods
3. Add to orchestrator workflow
4. Write tests
5. Update documentation

### New API Endpoint
1. Add route in `backend/api/routes.py`
2. Create Pydantic schema in `database/schemas.py`
3. Update API documentation
4. Add frontend API call in `services/api.js`

### New UI Component
1. Create component in `frontend/src/components/`
2. Create corresponding CSS file
3. Add to router if needed
4. Write component tests

## Code Review

All submissions require review. We use GitHub pull requests for this purpose.

Reviewers will check for:
- Code quality and style
- Test coverage
- Documentation updates
- Performance implications
- Security considerations

## Questions?

Open an issue for:
- Bug reports
- Feature requests
- Questions about implementation
- Suggestions for improvements

Thank you for contributing! 🎉

