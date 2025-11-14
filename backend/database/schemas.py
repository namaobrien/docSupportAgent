"""
Pydantic schemas for API request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Issue Schemas
class IssueBase(BaseModel):
    issue_number: int
    title: str
    url: str
    body: Optional[str] = None
    comments: Optional[List[Dict[str, Any]]] = None
    labels: Optional[List[str]] = None
    status: str = "open"

class IssueCreate(IssueBase):
    pass

class IssueResponse(IssueBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Rubric Score Schemas
class RubricScoreBase(BaseModel):
    accuracy_score: float
    clarity_score: float
    completeness_score: float
    examples_score: float
    structure_score: float
    discoverability_score: float
    total_score: float
    feedback: Dict[str, str]
    judge_reasoning: Optional[str] = None
    improvement_areas: Optional[List[str]] = None
    regression_areas: Optional[List[str]] = None

class RubricScoreResponse(RubricScoreBase):
    id: str
    iteration_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Iteration Schemas
class IterationBase(BaseModel):
    iteration_number: int
    rewritten_content: str
    improvement_focus: Optional[str] = None
    changes_made: Optional[List[str]] = None

class IterationResponse(IterationBase):
    id: str
    analysis_id: str
    created_at: datetime
    rubric_score: Optional[RubricScoreResponse] = None
    
    class Config:
        from_attributes = True

# Analysis Schemas
class AnalysisRequest(BaseModel):
    issue_number: int

class AnalysisBase(BaseModel):
    is_doc_issue: bool
    classification_confidence: Optional[float] = None
    gap_type: Optional[str] = None
    doc_url: Optional[str] = None
    status: str = "processing"

class AnalysisResponse(AnalysisBase):
    id: str
    issue_id: str
    original_doc_content: Optional[str] = None
    verification_report: Optional[Dict[str, Any]] = None
    verification_confidence: Optional[float] = None
    best_iteration_number: Optional[int] = None
    total_iterations: int = 0
    created_at: datetime
    completed_at: Optional[datetime] = None
    iterations: List[IterationResponse] = []
    
    class Config:
        from_attributes = True

class AnalysisDetailResponse(BaseModel):
    """Detailed analysis response with issue and iterations"""
    analysis: AnalysisResponse
    issue: IssueResponse
    flagged_for_review: bool = False
    review_reason: Optional[str] = None
    
    class Config:
        from_attributes = True

# Review Queue Schemas
class ReviewQueueBase(BaseModel):
    reason: str
    detailed_reason: Optional[str] = None
    original_score: Optional[float] = None
    best_achieved_score: Optional[float] = None
    iterations_attempted: Optional[int] = None
    status: str = "needs_review"

class ReviewQueueResponse(ReviewQueueBase):
    id: str
    analysis_id: str
    reviewer_notes: Optional[str] = None
    resolution: Optional[str] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None
    analysis: AnalysisResponse
    
    class Config:
        from_attributes = True

# Issue Search Schema
class IssueSearchRequest(BaseModel):
    days: int = Field(default=30, ge=1, le=365)
    label: Optional[str] = "documentation"

class IssueSearchResponse(BaseModel):
    issues: List[IssueResponse]
    total: int
    has_analysis: Dict[int, bool]  # Map of issue_number to whether analysis exists

# Status Response
class StatusResponse(BaseModel):
    analysis_id: str
    status: str
    message: Optional[str] = None

