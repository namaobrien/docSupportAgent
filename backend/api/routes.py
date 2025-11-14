"""
API Routes for Documentation Support Agent
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional

from database.connection import get_db
from database import models, schemas
from services.github_service import github_service
from agents.orchestrator import orchestrator

router = APIRouter()

# In-memory store for tracking analysis status (in production, use Redis)
analysis_status = {}

@router.get("/issues/search", response_model=schemas.IssueSearchResponse)
async def search_issues(
    days: int = 30,
    label: Optional[str] = "documentation",
    db: Session = Depends(get_db)
):
    """
    Search GitHub issues by date range and label
    
    Args:
        days: Number of days to look back (1-365)
        label: Filter by label (default: "documentation")
        db: Database session
        
    Returns:
        List of issues with analysis status
    """
    try:
        # Validate days parameter
        if days < 1 or days > 365:
            raise HTTPException(status_code=400, detail="Days must be between 1 and 365")
        
        # Search GitHub
        github_issues = github_service.search_issues(days=days, label=label, state="all")
        
        # Get existing analyses from database
        issue_numbers = [issue['issue_number'] for issue in github_issues]
        existing_issues = db.query(models.Issue).filter(
            models.Issue.issue_number.in_(issue_numbers)
        ).all()
        
        has_analysis = {}
        for db_issue in existing_issues:
            has_analysis[db_issue.issue_number] = len(db_issue.analyses) > 0
        
        # Format response
        issues_response = []
        for issue in github_issues:
            # Create or get from DB
            db_issue = db.query(models.Issue).filter(
                models.Issue.issue_number == issue['issue_number']
            ).first()
            
            if not db_issue:
                db_issue = models.Issue(
                    issue_number=issue['issue_number'],
                    title=issue['title'],
                    url=issue['url'],
                    body=issue.get('body', ''),
                    comments=issue.get('comments', []),
                    labels=issue.get('labels', []),
                    status=issue.get('state', 'open')
                )
                db.add(db_issue)
                db.commit()
                db.refresh(db_issue)
            
            issues_response.append(schemas.IssueResponse.from_orm(db_issue))
        
        return schemas.IssueSearchResponse(
            issues=issues_response,
            total=len(issues_response),
            has_analysis=has_analysis
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-issue")
async def analyze_issue(request: schemas.AnalysisRequest):
    """
    FAST SIMPLE analysis - ONE Claude call, immediate results
    
    Args:
        request: Analysis request with issue number
        
    Returns:
        Complete analysis results immediately
    """
    try:
        print(f"\n{'='*60}")
        print(f"[FAST ANALYSIS] Issue #{request.issue_number}")
        print(f"{'='*60}\n")
        
        from agents.simple_agent import simple_agent
        result = await simple_agent.improve_documentation(request.issue_number)
        
        print(f"\n{'='*60}")
        print(f"[FAST ANALYSIS] ✓ Done in {result['time_taken']:.1f}s")
        print(f"{'='*60}\n")
        
        return result
        
    except Exception as e:
        print(f"[FAST ANALYSIS] ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

def run_analysis_task(issue_number: int, temp_id: str):
    """
    Background task wrapper to run analysis (synchronous for BackgroundTasks)
    
    Args:
        issue_number: GitHub issue number
        temp_id: Temporary analysis ID
    """
    import asyncio
    
    try:
        print(f"[Analysis] Starting analysis for issue #{issue_number}")
        
        # Create new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Run the async analysis
        analysis_id = loop.run_until_complete(run_analysis(issue_number, temp_id))
        
        loop.close()
        
        print(f"[Analysis] Completed analysis for issue #{issue_number}, analysis_id: {analysis_id}")
        
    except Exception as e:
        print(f"[Analysis] FAILED for issue #{issue_number}: {e}")
        import traceback
        traceback.print_exc()
        analysis_status[temp_id] = f"failed: {str(e)}"

async def run_analysis(issue_number: int, temp_id: str):
    """
    Run analysis with its own database session
    
    Args:
        issue_number: GitHub issue number
        temp_id: Temporary analysis ID
        
    Returns:
        Real analysis ID from database
    """
    from database.connection import SessionLocal
    
    db = SessionLocal()
    try:
        print(f"[Analysis] Running orchestrator for issue #{issue_number}")
        
        # Run orchestrator
        analysis_id = await orchestrator.analyze_issue(issue_number, db)
        
        # Update status mapping
        analysis_status[temp_id] = "completed"
        analysis_status[analysis_id] = "completed"
        
        print(f"[Analysis] Success! Analysis ID: {analysis_id}")
        return analysis_id
        
    except Exception as e:
        print(f"[Analysis] Exception in run_analysis: {e}")
        import traceback
        traceback.print_exc()
        analysis_status[temp_id] = f"failed: {str(e)}"
        raise
    finally:
        db.close()

@router.get("/analysis/{analysis_id}", response_model=schemas.AnalysisDetailResponse)
async def get_analysis(
    analysis_id: str,
    db: Session = Depends(get_db)
):
    """
    Get analysis results by ID
    
    Args:
        analysis_id: Analysis ID
        db: Database session
        
    Returns:
        Detailed analysis with iterations and scores
    """
    # Check if it's a temp ID that's still processing
    if analysis_id in analysis_status:
        status = analysis_status[analysis_id]
        if status == "processing":
            raise HTTPException(
                status_code=202,
                detail="Analysis still processing"
            )
    
    # Get analysis from database with eager loading
    from sqlalchemy.orm import joinedload
    
    analysis = db.query(models.DocumentationAnalysis).options(
        joinedload(models.DocumentationAnalysis.iterations).joinedload(models.RewriteIteration.rubric_score),
        joinedload(models.DocumentationAnalysis.issue),
        joinedload(models.DocumentationAnalysis.review_item)
    ).filter(
        models.DocumentationAnalysis.id == analysis_id
    ).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    # Get issue
    issue = analysis.issue
    
    print(f"[API] Analysis {analysis_id} has {len(analysis.iterations)} iterations")
    
    # Get iterations with scores
    iterations = []
    for iteration in sorted(analysis.iterations, key=lambda x: x.iteration_number):
        print(f"[API] Processing iteration {iteration.iteration_number}")
        iteration_data = schemas.IterationResponse.from_orm(iteration)
        iterations.append(iteration_data)
    
    print(f"[API] Built {len(iterations)} iteration responses")
    
    # Check if flagged for review
    review_item = analysis.review_item
    flagged = review_item is not None
    review_reason = review_item.detailed_reason if review_item else None
    
    # Build response
    analysis_response = schemas.AnalysisResponse(
        id=analysis.id,
        issue_id=analysis.issue_id,
        is_doc_issue=analysis.is_doc_issue,
        classification_confidence=analysis.classification_confidence,
        gap_type=analysis.gap_type,
        doc_url=analysis.doc_url,
        original_doc_content=analysis.original_doc_content,
        verification_report=analysis.verification_report,
        verification_confidence=analysis.verification_confidence,
        status=analysis.status,
        best_iteration_number=analysis.best_iteration_number,
        total_iterations=analysis.total_iterations,
        created_at=analysis.created_at,
        completed_at=analysis.completed_at,
        iterations=iterations
    )
    
    issue_response = schemas.IssueResponse.from_orm(issue)
    
    return schemas.AnalysisDetailResponse(
        analysis=analysis_response,
        issue=issue_response,
        flagged_for_review=flagged,
        review_reason=review_reason
    )

@router.get("/issues", response_model=List[schemas.AnalysisDetailResponse])
async def list_analyses(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    List all analyses
    
    Args:
        limit: Maximum number of results
        offset: Offset for pagination
        db: Database session
        
    Returns:
        List of analyses
    """
    analyses = db.query(models.DocumentationAnalysis)\
        .order_by(models.DocumentationAnalysis.created_at.desc())\
        .limit(limit)\
        .offset(offset)\
        .all()
    
    results = []
    for analysis in analyses:
        # Get iterations
        iterations = []
        for iteration in sorted(analysis.iterations, key=lambda x: x.iteration_number):
            iteration_data = schemas.IterationResponse.from_orm(iteration)
            iterations.append(iteration_data)
        
        # Check review status
        review_item = analysis.review_item
        flagged = review_item is not None
        review_reason = review_item.detailed_reason if review_item else None
        
        analysis_response = schemas.AnalysisResponse(
            id=analysis.id,
            issue_id=analysis.issue_id,
            is_doc_issue=analysis.is_doc_issue,
            classification_confidence=analysis.classification_confidence,
            gap_type=analysis.gap_type,
            doc_url=analysis.doc_url,
            verification_confidence=analysis.verification_confidence,
            status=analysis.status,
            best_iteration_number=analysis.best_iteration_number,
            total_iterations=analysis.total_iterations,
            created_at=analysis.created_at,
            completed_at=analysis.completed_at,
            iterations=iterations
        )
        
        issue_response = schemas.IssueResponse.from_orm(analysis.issue)
        
        results.append(schemas.AnalysisDetailResponse(
            analysis=analysis_response,
            issue=issue_response,
            flagged_for_review=flagged,
            review_reason=review_reason
        ))
    
    return results

@router.get("/review-queue", response_model=List[schemas.ReviewQueueResponse])
async def get_review_queue(
    status: Optional[str] = "needs_review",
    sort_by: str = "date",
    db: Session = Depends(get_db)
):
    """
    Get review queue with filters
    
    Args:
        status: Filter by status (needs_review, resolved)
        sort_by: Sort by (score_diff, date)
        db: Database session
        
    Returns:
        List of items in review queue
    """
    query = db.query(models.ReviewQueue)
    
    # Filter by status
    if status:
        query = query.filter(models.ReviewQueue.status == status)
    
    # Sort
    if sort_by == "score_diff":
        query = query.order_by(
            (models.ReviewQueue.best_achieved_score - models.ReviewQueue.original_score).desc()
        )
    else:  # date
        query = query.order_by(models.ReviewQueue.created_at.desc())
    
    review_items = query.all()
    
    results = []
    for item in review_items:
        # Get full analysis data
        analysis = item.analysis
        
        # Get iterations
        iterations = []
        for iteration in sorted(analysis.iterations, key=lambda x: x.iteration_number):
            iteration_data = schemas.IterationResponse.from_orm(iteration)
            iterations.append(iteration_data)
        
        analysis_response = schemas.AnalysisResponse(
            id=analysis.id,
            issue_id=analysis.issue_id,
            is_doc_issue=analysis.is_doc_issue,
            classification_confidence=analysis.classification_confidence,
            gap_type=analysis.gap_type,
            doc_url=analysis.doc_url,
            verification_confidence=analysis.verification_confidence,
            status=analysis.status,
            best_iteration_number=analysis.best_iteration_number,
            total_iterations=analysis.total_iterations,
            created_at=analysis.created_at,
            completed_at=analysis.completed_at,
            iterations=iterations
        )
        
        review_response = schemas.ReviewQueueResponse(
            id=item.id,
            analysis_id=item.analysis_id,
            reason=item.reason,
            detailed_reason=item.detailed_reason,
            original_score=item.original_score,
            best_achieved_score=item.best_achieved_score,
            iterations_attempted=item.iterations_attempted,
            status=item.status,
            reviewer_notes=item.reviewer_notes,
            resolution=item.resolution,
            created_at=item.created_at,
            resolved_at=item.resolved_at,
            analysis=analysis_response
        )
        
        results.append(review_response)
    
    return results

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "documentation-support-agent"}

@router.get("/test-github/{issue_number}")
async def test_github(issue_number: int):
    """Test if GitHub API is working"""
    try:
        print(f"[TEST] Fetching issue #{issue_number} from GitHub")
        issue_data = github_service.get_issue(issue_number)
        print(f"[TEST] ✓ Success!")
        return {
            "status": "success",
            "issue": {
                "number": issue_data['issue_number'],
                "title": issue_data['title'],
                "labels": issue_data.get('labels', [])
            }
        }
    except Exception as e:
        print(f"[TEST] ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

@router.get("/test-claude")
async def test_claude():
    """Test if Claude API is working"""
    try:
        print(f"[TEST] Testing Claude API")
        from services.claude_client import claude_client
        response = await claude_client.send_message(
            system_prompt="You are a helpful assistant.",
            user_message="Say 'Hello!'",
            temperature=0.7,
            max_tokens=50
        )
        print(f"[TEST] ✓ Claude response: {response[:50]}")
        return {
            "status": "success",
            "response": response
        }
    except Exception as e:
        print(f"[TEST] ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

@router.post("/analyze-issue-sync")
async def analyze_issue_sync(
    request: schemas.AnalysisRequest,
    db: Session = Depends(get_db)
):
    """SYNCHRONOUS analysis for immediate testing and debugging"""
    try:
        print(f"\n{'='*60}")
        print(f"[SYNC ANALYSIS] Starting for issue #{request.issue_number}")
        print(f"{'='*60}\n")
        
        from agents import orchestrator
        analysis_id = await orchestrator.analyze_issue(request.issue_number, db)
        
        print(f"\n{'='*60}")
        print(f"[SYNC ANALYSIS] ✓ COMPLETE! Analysis ID: {analysis_id}")
        print(f"{'='*60}\n")
        
        return schemas.StatusResponse(
            analysis_id=analysis_id,
            status="completed",
            message="Analysis completed successfully"
        )
        
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"[SYNC ANALYSIS] ✗ FAILED: {e}")
        print(f"{'='*60}\n")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

