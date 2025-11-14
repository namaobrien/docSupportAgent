# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-11-14

### Added
- Initial release of Documentation Support Agent
- AI-powered documentation issue classification
- Automated documentation search and retrieval
- Deep codebase verification to prevent hallucinations
- Iterative documentation improvement (up to 20 iterations)
- LLM judge with 6-criteria quality rubric
- React frontend with:
  - Issue browser with date range filtering
  - Real-time analysis dashboard
  - Iteration timeline visualization
  - Rubric score charts
  - Review queue for flagged issues
- FastAPI backend with:
  - Issue classification agent
  - Documentation search agent
  - Codebase verification agent
  - Documentation rewriter agent
  - LLM judge agent
  - Orchestrator for workflow management
- PostgreSQL database for storing:
  - Issues and analyses
  - Iterations and rubric scores
  - Review queue items
- Docker Compose setup for easy deployment
- Comprehensive documentation:
  - README with quick start
  - SETUP guide
  - ARCHITECTURE documentation
  - CONTRIBUTING guidelines
- Anti-hallucination safeguards:
  - Codebase verification
  - Source citations
  - Confidence scoring
  - Fact-checking
  - Human review fallback

### Features
- Search GitHub issues by date range (today, last 7/30/90 days)
- Classify documentation issues with confidence scores
- Find relevant documentation via semantic search
- Verify technical claims against source code
- Rewrite documentation with style guide compliance
- Evaluate quality using weighted rubric (Accuracy 30%, Clarity 20%, etc.)
- Iterate up to 20 times with judge feedback
- Flag for human review when improvement fails
- View detailed rubric scores for each iteration
- Compare original vs improved documentation
- Filter and sort review queue

### Technical
- Claude Sonnet 4.5 for all AI operations
- GitHub API integration for issue retrieval
- Web scraping for documentation pages
- Git repository cloning and analysis
- Background task processing
- Real-time status polling
- Responsive UI design following Claude Code style guide

[1.0.0]: https://github.com/yourusername/doc-support-agent/releases/tag/v1.0.0

