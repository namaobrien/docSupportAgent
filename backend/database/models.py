"""
SQLAlchemy database models
"""
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.connection import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class Issue(Base):
    """GitHub issue metadata"""
    __tablename__ = "issues"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    issue_number = Column(Integer, unique=True, nullable=False, index=True)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    body = Column(Text)
    comments = Column(JSON)  # Stored as list of comment dicts
    labels = Column(JSON)  # List of label strings
    status = Column(String, default="open")  # open, closed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    analyses = relationship("DocumentationAnalysis", back_populates="issue", cascade="all, delete-orphan")

class DocumentationAnalysis(Base):
    """Analysis results for a documentation issue"""
    __tablename__ = "documentation_analysis"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    issue_id = Column(String, ForeignKey("issues.id"), nullable=False, index=True)
    
    # Classification results
    is_doc_issue = Column(Boolean, nullable=False)
    classification_confidence = Column(Float)
    gap_type = Column(String)  # missing, incorrect, unclear, outdated, example_needed
    
    # Documentation found
    doc_url = Column(String)
    original_doc_content = Column(Text)
    
    # Verification results
    verification_report = Column(JSON)
    verification_confidence = Column(Float)
    
    # Status tracking
    status = Column(String, default="processing")  # processing, completed, flagged, failed
    best_iteration_number = Column(Integer)
    total_iterations = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    issue = relationship("Issue", back_populates="analyses")
    iterations = relationship("RewriteIteration", back_populates="analysis", cascade="all, delete-orphan")
    review_item = relationship("ReviewQueue", back_populates="analysis", uselist=False, cascade="all, delete-orphan")

class RewriteIteration(Base):
    """Each documentation rewrite attempt"""
    __tablename__ = "rewrite_iterations"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    analysis_id = Column(String, ForeignKey("documentation_analysis.id"), nullable=False, index=True)
    iteration_number = Column(Integer, nullable=False)
    
    # Rewritten content
    rewritten_content = Column(Text, nullable=False)
    
    # Improvement notes
    improvement_focus = Column(Text)  # What this iteration tried to improve
    changes_made = Column(JSON)  # List of specific changes
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    analysis = relationship("DocumentationAnalysis", back_populates="iterations")
    rubric_score = relationship("RubricScore", back_populates="iteration", uselist=False, cascade="all, delete-orphan")

class RubricScore(Base):
    """LLM judge evaluation scores"""
    __tablename__ = "rubric_scores"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    iteration_id = Column(String, ForeignKey("rewrite_iterations.id"), nullable=False, unique=True, index=True)
    
    # Individual criterion scores (1-10)
    accuracy_score = Column(Float, nullable=False)
    clarity_score = Column(Float, nullable=False)
    completeness_score = Column(Float, nullable=False)
    examples_score = Column(Float, nullable=False)
    structure_score = Column(Float, nullable=False)
    discoverability_score = Column(Float, nullable=False)
    
    # Weighted total score (max 10.0)
    total_score = Column(Float, nullable=False)
    
    # Detailed feedback
    feedback = Column(JSON)  # Dict with feedback for each criterion
    judge_reasoning = Column(Text)  # Overall reasoning from judge
    
    # Comparison with original
    improvement_areas = Column(JSON)  # List of areas that improved
    regression_areas = Column(JSON)  # List of areas that got worse
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    iteration = relationship("RewriteIteration", back_populates="rubric_score")

class ReviewQueue(Base):
    """Issues flagged for human review"""
    __tablename__ = "review_queue"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    analysis_id = Column(String, ForeignKey("documentation_analysis.id"), nullable=False, unique=True, index=True)
    
    # Flagging details
    reason = Column(String, nullable=False)  # failed_to_improve, verification_failed, conflicting_info
    detailed_reason = Column(Text)
    
    # Context
    original_score = Column(Float)
    best_achieved_score = Column(Float)
    iterations_attempted = Column(Integer)
    
    # Review status
    status = Column(String, default="needs_review")  # needs_review, in_progress, resolved
    reviewer_notes = Column(Text)
    resolution = Column(String)  # approved, rejected, modified
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True))
    
    # Relationships
    analysis = relationship("DocumentationAnalysis", back_populates="review_item")

