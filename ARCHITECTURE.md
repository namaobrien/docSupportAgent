# Documentation Support Agent - Architecture

## System Overview

The Documentation Support Agent is an AI-powered system that analyzes GitHub issues, identifies documentation problems, and iteratively improves documentation quality using Claude Sonnet 4.5.

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   React     │─────→│   FastAPI    │─────→│  PostgreSQL │
│  Frontend   │      │   Backend    │      │  Database   │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ├─────→ GitHub API
                            ├─────→ Claude API (Sonnet 4.5)
                            ├─────→ Documentation Scraper
                            └─────→ Repository Analyzer
```

## Component Architecture

### Frontend (React)

**Technology Stack:**
- React 18 with Hooks
- Vite for build tooling
- React Router for navigation
- Recharts for data visualization
- Axios for API calls

**Key Components:**

1. **IssueBrowser** - Search and browse documentation issues
   - Date range filtering
   - Issue list display
   - Direct analysis triggering

2. **AnalysisDashboard** - View analysis results
   - Real-time status updates
   - Iteration-by-iteration scores
   - Documentation comparison
   - Rubric visualization

3. **RubricScoreChart** - Line chart showing score progression
   - Multiple criteria visualization
   - Best iteration highlighting
   - Interactive tooltips

4. **IterationTimeline** - Timeline view of all iterations
   - Clickable iteration cards
   - Score and focus display
   - Best iteration marker

5. **ReviewQueue** - Human review interface
   - Filtering and sorting
   - Analysis details
   - Direct navigation to flagged items

### Backend (Python/FastAPI)

**Technology Stack:**
- FastAPI for API framework
- SQLAlchemy for ORM
- PostgreSQL for database
- Anthropic SDK for Claude API
- PyGithub for GitHub API
- BeautifulSoup for web scraping
- GitPython for repository analysis

**Architecture Layers:**

```
┌─────────────────────────────────────────────────┐
│              API Layer (routes.py)              │
│  - REST endpoints                               │
│  - Request validation                           │
│  - Response formatting                          │
└─────────────────────────────────────────────────┘
                      │
┌─────────────────────────────────────────────────┐
│         Agent Orchestration Layer               │
│  - Orchestrator: Coordinates all agents         │
│  - Workflow management                          │
│  - Iteration control                            │
└─────────────────────────────────────────────────┘
                      │
┌─────────────────────────────────────────────────┐
│              Agent Layer                        │
│  - Issue Classifier                             │
│  - Documentation Searcher                       │
│  - Codebase Verifier                           │
│  - Documentation Rewriter                       │
│  - LLM Judge                                    │
└─────────────────────────────────────────────────┘
                      │
┌─────────────────────────────────────────────────┐
│            Service Layer                        │
│  - Claude Client (API wrapper)                  │
│  - GitHub Service                               │
│  - Documentation Scraper                        │
│  - Repository Analyzer                          │
└─────────────────────────────────────────────────┘
                      │
┌─────────────────────────────────────────────────┐
│           Data Layer                            │
│  - SQLAlchemy Models                            │
│  - Database Connection                          │
│  - Pydantic Schemas                             │
└─────────────────────────────────────────────────┘
```

## Agent Workflow

### 1. Issue Classification Agent

**Purpose:** Determine if an issue is documentation-related

**Process:**
1. Receive issue title, body, and comments
2. Send to Claude with classification prompt
3. Return boolean, confidence score, and gap type

**Output:**
```json
{
  "is_doc_issue": true,
  "confidence": 0.95,
  "gap_type": "incorrect",
  "reasoning": "..."
}
```

### 2. Documentation Search Agent

**Purpose:** Find relevant documentation pages

**Process:**
1. Check if documentation URLs mentioned in issue
2. If not, generate search query using Claude
3. Scrape documentation website
4. Use semantic search to find relevant pages
5. Rank results by relevance

**Output:** List of documentation pages with content

### 3. Codebase Verification Agent

**Purpose:** Verify documentation claims against source code

**Process:**
1. Extract technical claims from documentation
2. Clone/update repository
3. Search codebase for mentioned functions/APIs
4. Verify signatures and implementations
5. Test code examples
6. Generate confidence scores

**Output:**
```json
{
  "overall_confidence": 0.85,
  "claims_verified": 5,
  "claims_passed": 4,
  "verification_results": [...]
}
```

### 4. Documentation Rewriter Agent

**Purpose:** Generate improved documentation

**Process:**
1. Receive original doc, issue context, verification report
2. Apply style guide and best practices
3. Use previous feedback (if iterating)
4. Generate rewritten documentation with citations
5. Identify improvement focus

**Key Constraints:**
- Must cite codebase sources
- Follow style guide
- Maintain accuracy per verification report
- No hallucinations

### 5. LLM Judge Agent

**Purpose:** Evaluate documentation quality using rubric

**Process:**
1. Receive documentation to evaluate
2. Apply 6-criteria rubric
3. Score each criterion (1-10)
4. Calculate weighted total score
5. Provide detailed feedback
6. Suggest improvements

**Rubric:**
- Accuracy & Correctness (30%)
- Clarity & Readability (20%)
- Completeness (20%)
- Code Examples Quality (15%)
- Structure & Organization (10%)
- Discoverability (5%)

### 6. Orchestrator

**Purpose:** Coordinate all agents and manage iteration loop

**Main Workflow:**

```python
1. Get issue from GitHub
2. Classify issue (is it documentation-related?)
3. If not documentation: Stop
4. Find relevant documentation
5. Verify documentation against codebase
6. Evaluate original documentation (get baseline score)

7. ITERATION LOOP (max 20 iterations):
   a. Rewrite documentation
   b. Evaluate rewritten version
   c. Compare scores
   d. If improved:
      - Track as best version
      - Continue for N more iterations
   e. If not improved:
      - Use judge feedback for next iteration
   f. Stop if:
      - 20 iterations reached without beating original
      - N iterations without improvement after beating original

8. If failed to beat original: Flag for human review
9. Save all iterations and scores to database
10. Mark as completed
```

## Database Schema

### Tables

**issues**
- Issue metadata from GitHub
- Stores title, body, comments, labels

**documentation_analysis**
- Analysis record for each issue
- Classification results
- Documentation URL and content
- Verification report
- Status and completion info

**rewrite_iterations**
- Each rewrite attempt
- Rewritten content
- Improvement focus
- Changes made

**rubric_scores**
- Judge evaluation for each iteration
- Individual criterion scores
- Total weighted score
- Detailed feedback
- Improvement/regression tracking

**review_queue**
- Items flagged for human review
- Reason for flagging
- Original vs best scores
- Review status and notes

## API Endpoints

### Issue Management
- `GET /api/issues/search` - Search GitHub issues by date range
- `POST /api/analyze-issue` - Trigger analysis for an issue
- `GET /api/issues` - List all analyzed issues

### Analysis
- `GET /api/analysis/{id}` - Get analysis results with iterations
- Real-time status polling supported

### Review Queue
- `GET /api/review-queue` - Get flagged items with filters

## Anti-Hallucination Safeguards

1. **Codebase Verification**
   - All technical claims cross-checked
   - Function/API existence verified
   - Code examples tested

2. **Source Citations**
   - Rewriter must cite file:line references
   - Verification provides evidence
   - Judge checks for accuracy

3. **Confidence Scoring**
   - Each verification has confidence score
   - Low confidence triggers warnings
   - Confidence considered in final evaluation

4. **Judge Fact-Checking**
   - Accuracy is highest-weighted criterion (30%)
   - Judge specifically checks for correctness
   - False claims heavily penalized

5. **Human Review Fallback**
   - Automatic flagging for suspicious cases
   - Manual review for failed improvements
   - Verification failures trigger review

## Iteration Strategy

### Success Path
1. Beat original score
2. Continue for 3 more iterations
3. Track best version
4. Stop when no improvement for 3 iterations

### Failure Path
1. Reach 20 iterations without beating original
2. Flag for human review with context
3. Provide original vs best achieved score
4. Include detailed reason for failure

### Stopping Conditions
- Max 20 iterations total
- 3 iterations without improvement after success
- Processing error (with retry logic)

## Deployment Architecture

### Development
```
┌─────────────┐
│  Local Dev  │
│             │
│  Frontend:  │
│  npm dev    │
│             │
│  Backend:   │
│  uvicorn    │
│             │
│  Database:  │
│  Docker     │
└─────────────┘
```

### Production (Docker Compose)
```
┌──────────────────────────────────────┐
│         Docker Compose               │
│                                      │
│  ┌──────────┐  ┌──────────┐        │
│  │ Frontend │  │ Backend  │        │
│  │  :3000   │  │  :8000   │        │
│  └──────────┘  └──────────┘        │
│                      │              │
│              ┌──────────┐           │
│              │   DB     │           │
│              │  :5432   │           │
│              └──────────┘           │
└──────────────────────────────────────┘
```

## Performance Considerations

### Bottlenecks
1. Claude API rate limits
2. GitHub API rate limits
3. Repository cloning time
4. Documentation scraping

### Optimizations
1. Repository caching (git pull vs clone)
2. In-memory analysis status tracking
3. Background task processing
4. Concurrent iteration processing (future)
5. Documentation page caching (future)

### Scaling
- Backend is stateless (can scale horizontally)
- Use Redis for distributed status tracking
- Queue system (Celery) for background tasks
- CDN for frontend
- Read replicas for database

## Security Considerations

1. **API Keys**
   - Stored in environment variables
   - Never committed to repository
   - Rotated regularly

2. **Database**
   - Strong passwords
   - Limited network access
   - Regular backups

3. **GitHub Access**
   - Minimal required permissions
   - Personal access token (not OAuth app)
   - Read-only access to issues

4. **CORS**
   - Configured allowed origins
   - Production URLs whitelisted
   - No wildcard in production

## Monitoring & Observability

### Logs
- Structured logging with context
- Log levels: DEBUG, INFO, WARNING, ERROR
- Service-specific log streams

### Metrics (Future)
- Analysis completion rate
- Average iterations to success
- Score improvement distribution
- API latency
- Error rates

### Alerts (Future)
- High error rate
- API quota exceeded
- Long-running analyses
- Database connection issues

