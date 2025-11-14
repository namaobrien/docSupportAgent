# Quick Start Guide

Get the Documentation Support Agent running in 5 minutes!

## Prerequisites
- Docker and Docker Compose installed
- Anthropic API key ([get one here](https://console.anthropic.com/))
- GitHub Personal Access Token ([create here](https://github.com/settings/tokens))

## Steps

### 1. Setup Environment

```bash
# Copy environment file
make setup

# Edit backend/.env with your keys
nano backend/.env
```

Add your API keys:
```bash
ANTHROPIC_API_KEY=sk-ant-xxxxx
GITHUB_TOKEN=ghp_xxxxx
```

### 2. Start Services

```bash
make start
```

This starts:
- PostgreSQL database
- FastAPI backend
- React frontend

### 3. Access the Application

Open your browser to: **http://localhost:3000**

API documentation: **http://localhost:8000/docs**

## Using the Application

### Analyze an Issue

1. **Browse Issues**
   - Select time range (today, last 7 days, etc.)
   - View documentation-related issues
   - Click "Analyze Issue" on any issue

2. **Or Enter Issue Number**
   - Enter issue number directly (e.g., 1234)
   - Click "Analyze"

3. **View Results**
   - Real-time progress updates
   - Iteration-by-iteration scores
   - Best iteration highlighted
   - Rubric breakdown
   - Original vs improved comparison

4. **Review Queue**
   - Click "Review Queue" in navigation
   - View flagged issues needing human review
   - Filter by status and sort by score

## Key Features

### Issue Browser
- **Date Range Filtering**: Search issues from today up to 90 days ago
- **Quick Analysis**: Trigger analysis directly from browser
- **Manual Entry**: Analyze specific issue numbers

### Analysis Dashboard
- **Real-time Updates**: See progress as agent works
- **Score Visualization**: Line charts showing improvement over iterations
- **Iteration Timeline**: Click any iteration to see details
- **Rubric Details**: 6-criteria breakdown with feedback
- **Best Iteration**: Automatically highlighted

### Review Queue
- **Smart Filtering**: Filter by status (needs review, resolved)
- **Score Comparison**: See original vs best achieved scores
- **Direct Links**: Jump to analysis or GitHub issue

## Understanding the Results

### Classification
The agent first determines if the issue is documentation-related with a confidence score.

### Gap Types
- **missing**: Documentation doesn't exist
- **incorrect**: Documentation has errors
- **unclear**: Documentation is confusing
- **outdated**: Documentation is obsolete
- **example_needed**: Missing code examples

### Rubric Scores (1-10)
- **Accuracy** (30% weight): Technical correctness
- **Clarity** (20% weight): Readability and flow
- **Completeness** (20% weight): Coverage of topic
- **Examples** (15% weight): Quality of code examples
- **Structure** (10% weight): Organization and hierarchy
- **Discoverability** (5% weight): Searchability

### Iteration Strategy
1. Agent rewrites documentation
2. Judge evaluates with rubric
3. If score improves: Continue for 3 more iterations
4. If score doesn't improve: Use feedback to iterate (max 20 total)
5. If can't beat original: Flag for human review

## Common Issues

### "Analysis not found"
The analysis is still processing. Wait a few seconds and refresh.

### No issues found
- Check your GitHub token has correct permissions
- Verify the time range has documentation issues
- Try searching without label filter

### Slow performance
- Claude API rate limits may be hit
- Repository cloning takes time on first run (cached after)
- Complex issues require more iterations

## Commands

```bash
make start      # Start all services
make stop       # Stop all services
make logs       # View logs
make restart    # Restart services
make clean      # Remove all data and reset
```

## What's Happening Behind the Scenes?

When you click "Analyze Issue":

1. **Classification Agent** determines if it's a doc issue
2. **Search Agent** finds relevant documentation pages
3. **Verification Agent** checks claims against codebase
4. **Rewriter Agent** improves the documentation
5. **Judge Agent** scores the improvement
6. **Repeat steps 4-5** up to 20 times
7. **Flag for review** if improvements don't beat original

All using **Claude Sonnet 4.5** with anti-hallucination safeguards!

## Next Steps

- Read [ARCHITECTURE.md](ARCHITECTURE.md) to understand the system
- Check [SETUP.md](SETUP.md) for detailed configuration
- See [README.md](README.md) for comprehensive documentation

## Support

If you encounter issues:
1. Check logs: `make logs`
2. Verify API keys are correct
3. Ensure Docker is running
4. Review troubleshooting in [SETUP.md](SETUP.md)

Happy analyzing! 🚀

