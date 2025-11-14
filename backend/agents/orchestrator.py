"""
Orchestrator Agent
Coordinates all agents and manages the iterative improvement process
"""
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime

from agents.issue_classifier import issue_classifier
from agents.doc_searcher import doc_searcher
from agents.doc_rewriter import doc_rewriter
from agents.judge import judge

from database import models
from config import settings

class Orchestrator:
    """Main orchestrator for the documentation improvement workflow"""
    
    def __init__(self):
        self.max_iterations = settings.max_iterations
        self.improvement_iterations = settings.improvement_iterations
    
    async def analyze_issue(
        self,
        issue_number: int,
        db: Session
    ) -> str:
        """
        Run complete analysis workflow for an issue
        
        Args:
            issue_number: GitHub issue number
            db: Database session
            
        Returns:
            Analysis ID
        """
        from services.github_service import github_service
        
        # Get or create issue in database
        issue_data = github_service.get_issue(issue_number)
        db_issue = self._get_or_create_issue(db, issue_data)
        
        # Create analysis record
        analysis = models.DocumentationAnalysis(
            issue_id=db_issue.id,
            is_doc_issue=False,  # Will be updated
            status="processing"
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        
        try:
            # Step 1: Classify issue
            print(f"[Orchestrator] Step 1: Classifying issue #{issue_number}")
            classification = await issue_classifier.classify_issue(issue_data)
            print(f"[Orchestrator] Classification result: {classification['is_doc_issue']}")
            
            analysis.is_doc_issue = classification['is_doc_issue']
            analysis.classification_confidence = classification.get('confidence', 0)
            analysis.gap_type = classification.get('gap_type')
            db.commit()
            
            if not classification['is_doc_issue']:
                print(f"[Orchestrator] Not a doc issue, skipping analysis")
                analysis.status = "completed"
                db.commit()
                return analysis.id
            
            # Step 2: Find relevant documentation
            print(f"[Orchestrator] Step 2: Finding relevant documentation")
            doc_results = await doc_searcher.find_relevant_docs(issue_data, classification)
            print(f"[Orchestrator] Found {len(doc_results) if doc_results else 0} documentation pages")
            
            if not doc_results:
                analysis.status = "failed"
                db.commit()
                self._flag_for_review(
                    db,
                    analysis.id,
                    "no_docs_found",
                    "Could not find relevant documentation pages"
                )
                return analysis.id
            
            # Use the most relevant documentation
            best_doc = doc_results[0]
            analysis.doc_url = best_doc['url']
            analysis.original_doc_content = best_doc['content']
            db.commit()
            print(f"[Orchestrator] Using doc: {best_doc['url']}")
            
            # Step 3: Evaluate original documentation (NO CODEBASE VERIFICATION)
            print(f"[Orchestrator] Step 3: Evaluating original documentation")
            original_evaluation = await judge.evaluate_documentation(
                best_doc['content'],
                issue_data,
                is_original=True
            )
            
            original_score = original_evaluation['total_score']
            print(f"[Orchestrator] Original doc score: {original_score}/10")
            
            # Step 4: Iterative improvement loop
            print(f"[Orchestrator] Step 4: Starting iterative improvement (max {self.max_iterations} iterations)")
            best_iteration = None
            best_score = original_score
            iterations_since_improvement = 0
            previous_feedback = None
            
            for iteration_num in range(1, self.max_iterations + 1):
                print(f"[Orchestrator] --- Iteration {iteration_num}/{self.max_iterations} ---")
                # Rewrite documentation
                rewrite_result = await doc_rewriter.rewrite_documentation(
                    original_doc=best_doc['content'],
                    issue_data=issue_data,
                    previous_feedback=previous_feedback,
                    iteration_number=iteration_num
                )
                
                # Create iteration record
                iteration = models.RewriteIteration(
                    analysis_id=analysis.id,
                    iteration_number=iteration_num,
                    rewritten_content=rewrite_result['content'],
                    improvement_focus=rewrite_result.get('improvement_focus'),
                    changes_made=rewrite_result.get('changes_made', [])
                )
                db.add(iteration)
                db.commit()
                db.refresh(iteration)
                
                # Evaluate rewritten documentation
                print(f"[Orchestrator] Evaluating rewrite iteration {iteration_num}")
                evaluation = await judge.evaluate_documentation(
                    rewrite_result['content'],
                    issue_data,
                    is_original=False
                )
                
                # Create rubric score record
                rubric_score = models.RubricScore(
                    iteration_id=iteration.id,
                    accuracy_score=evaluation['accuracy_score'],
                    clarity_score=evaluation['clarity_score'],
                    completeness_score=evaluation['completeness_score'],
                    examples_score=evaluation['examples_score'],
                    structure_score=evaluation['structure_score'],
                    discoverability_score=evaluation['discoverability_score'],
                    total_score=evaluation['total_score'],
                    feedback=evaluation['feedback'],
                    judge_reasoning=evaluation.get('overall_reasoning')
                )
                
                # Compare with original
                comparison = judge.compare_scores(original_evaluation, evaluation)
                rubric_score.improvement_areas = [imp['criterion'] for imp in comparison.get('improvements', [])]
                rubric_score.regression_areas = [reg['criterion'] for reg in comparison.get('regressions', [])]
                
                db.add(rubric_score)
                db.commit()
                
                # Track best iteration
                current_score = evaluation['total_score']
                print(f"[Orchestrator] Iteration {iteration_num} score: {current_score}/10 (best so far: {best_score}/10)")
                
                if current_score > best_score:
                    best_score = current_score
                    best_iteration = iteration_num
                    iterations_since_improvement = 0
                    print(f"[Orchestrator] ✓ New best score!")
                else:
                    iterations_since_improvement += 1
                    print(f"[Orchestrator] No improvement (attempts since last improvement: {iterations_since_improvement})")
                
                # Update analysis
                analysis.total_iterations = iteration_num
                analysis.best_iteration_number = best_iteration
                db.commit()
                
                # Check stopping conditions
                if current_score > original_score:
                    # If we've beaten original score, continue for N more iterations
                    if iterations_since_improvement >= self.improvement_iterations:
                        # No improvement in last N iterations, stop
                        break
                else:
                    # Haven't beaten original yet
                    if iteration_num >= self.max_iterations:
                        # Reached max iterations without beating original
                        self._flag_for_review(
                            db,
                            analysis.id,
                            "failed_to_improve",
                            f"Could not improve documentation after {self.max_iterations} iterations",
                            original_score=original_score,
                            best_score=best_score,
                            iterations=iteration_num
                        )
                        break
                
                # Prepare feedback for next iteration
                if evaluation.get('improvement_suggestions'):
                    previous_feedback = "\n".join(evaluation['improvement_suggestions'][:3])
                else:
                    previous_feedback = evaluation.get('overall_reasoning', '')
            
            # Mark as completed
            analysis.status = "completed" if best_score > original_score else "flagged"
            analysis.completed_at = datetime.utcnow()
            db.commit()
            
            print(f"[Orchestrator] ✓ Analysis complete!")
            print(f"[Orchestrator] Final score: {best_score}/10 ({best_score*10:.0f}%) • Original: {original_score}/10 ({original_score*10:.0f}%)")
            print(f"[Orchestrator] Improvement: +{(best_score - original_score)*10:.1f} percentage points")
            print(f"[Orchestrator] Status: {analysis.status}")
            print(f"[Orchestrator] Analysis ID: {analysis.id}")
            
            return analysis.id
            
        except Exception as e:
            print(f"[Orchestrator] ✗ Error during analysis: {e}")
            import traceback
            traceback.print_exc()
            
            analysis.status = "failed"
            db.commit()
            
            self._flag_for_review(
                db,
                analysis.id,
                "processing_error",
                f"Error during analysis: {str(e)}"
            )
            
            raise e
    
    def _get_or_create_issue(self, db: Session, issue_data: Dict[str, Any]) -> models.Issue:
        """
        Get existing issue or create new one
        
        Args:
            db: Database session
            issue_data: Issue data from GitHub
            
        Returns:
            Issue model
        """
        issue = db.query(models.Issue).filter(
            models.Issue.issue_number == issue_data['issue_number']
        ).first()
        
        if issue:
            # Update existing issue
            issue.title = issue_data['title']
            issue.url = issue_data['url']
            issue.body = issue_data.get('body', '')
            issue.comments = issue_data.get('comments', [])
            issue.labels = issue_data.get('labels', [])
            issue.status = issue_data.get('state', 'open')
        else:
            # Create new issue
            issue = models.Issue(
                issue_number=issue_data['issue_number'],
                title=issue_data['title'],
                url=issue_data['url'],
                body=issue_data.get('body', ''),
                comments=issue_data.get('comments', []),
                labels=issue_data.get('labels', []),
                status=issue_data.get('state', 'open')
            )
            db.add(issue)
        
        db.commit()
        db.refresh(issue)
        return issue
    
    def _flag_for_review(
        self,
        db: Session,
        analysis_id: str,
        reason: str,
        detailed_reason: str,
        original_score: float = None,
        best_score: float = None,
        iterations: int = None
    ):
        """
        Flag analysis for human review
        
        Args:
            db: Database session
            analysis_id: Analysis ID
            reason: Short reason code
            detailed_reason: Detailed explanation
            original_score: Original documentation score
            best_score: Best achieved score
            iterations: Number of iterations attempted
        """
        review_item = models.ReviewQueue(
            analysis_id=analysis_id,
            reason=reason,
            detailed_reason=detailed_reason,
            original_score=original_score,
            best_achieved_score=best_score,
            iterations_attempted=iterations,
            status="needs_review"
        )
        db.add(review_item)
        db.commit()

# Singleton instance
orchestrator = Orchestrator()

