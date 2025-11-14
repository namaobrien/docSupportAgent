"""
LLM Judge Agent
Evaluates documentation quality using rubric
"""
from services.claude_client import claude_client
from typing import Dict, Any

class Judge:
    """Agent for evaluating documentation quality"""
    
    # Rubric weights
    WEIGHTS = {
        'accuracy': 0.30,
        'clarity': 0.20,
        'completeness': 0.20,
        'examples': 0.15,
        'structure': 0.10,
        'discoverability': 0.05
    }
    
    async def evaluate_documentation(
        self,
        documentation: str,
        issue_context: Dict[str, Any],
        is_original: bool = False
    ) -> Dict[str, Any]:
        """
        Evaluate documentation using quality rubric
        
        Args:
            documentation: Documentation content to evaluate
            issue_context: GitHub issue data
            verification_report: Codebase verification results
            is_original: Whether this is the original documentation
            
        Returns:
            Evaluation scores and feedback
        """
        rubric = self._get_rubric()
        
        system_prompt = f"""You are an expert technical documentation evaluator.

Evaluate the provided documentation using this rubric:

{rubric}

Score each criterion from 1-10, where:
- 1-3: Poor (major issues)
- 4-6: Fair (needs improvement)
- 7-8: Good (meets standards)
- 9-10: Excellent (exceptional quality)

Be critical but fair. Consider the issue context."""

        user_message = f"""=== DOCUMENTATION TO EVALUATE ===
{documentation}

=== CONTEXT ===
User Issue: {issue_context['title']}
Issue Description: {issue_context.get('body', '')[:500]}

=== TASK ===
Evaluate this documentation {'(ORIGINAL VERSION)' if is_original else '(REWRITTEN VERSION)'} against the rubric.
Provide scores and specific, actionable feedback for each criterion.

Focus on whether the documentation addresses the user's issue and follows technical documentation best practices."""

        response_schema = {
            "accuracy_score": "float (1-10)",
            "accuracy_feedback": "string - specific feedback on accuracy",
            "clarity_score": "float (1-10)",
            "clarity_feedback": "string - specific feedback on clarity",
            "completeness_score": "float (1-10)",
            "completeness_feedback": "string - specific feedback on completeness",
            "examples_score": "float (1-10)",
            "examples_feedback": "string - specific feedback on examples",
            "structure_score": "float (1-10)",
            "structure_feedback": "string - specific feedback on structure",
            "discoverability_score": "float (1-10)",
            "discoverability_feedback": "string - specific feedback on discoverability",
            "overall_reasoning": "string - 2-3 sentences summarizing the evaluation",
            "improvement_suggestions": ["array", "of", "specific suggestions for next iteration"]
        }
        
        try:
            result = await claude_client.send_structured_message(
                system_prompt=system_prompt,
                user_message=user_message,
                response_schema=response_schema,
                temperature=0.3,
                max_tokens=3000
            )
            
            # Calculate weighted total score
            total_score = (
                result['accuracy_score'] * self.WEIGHTS['accuracy'] +
                result['clarity_score'] * self.WEIGHTS['clarity'] +
                result['completeness_score'] * self.WEIGHTS['completeness'] +
                result['examples_score'] * self.WEIGHTS['examples'] +
                result['structure_score'] * self.WEIGHTS['structure'] +
                result['discoverability_score'] * self.WEIGHTS['discoverability']
            )
            
            result['total_score'] = round(total_score, 2)
            
            # Organize feedback
            result['feedback'] = {
                'accuracy': result['accuracy_feedback'],
                'clarity': result['clarity_feedback'],
                'completeness': result['completeness_feedback'],
                'examples': result['examples_feedback'],
                'structure': result['structure_feedback'],
                'discoverability': result['discoverability_feedback']
            }
            
            return result
            
        except Exception as e:
            raise Exception(f"Evaluation failed: {str(e)}")
    
    def compare_scores(
        self,
        original_score: Dict[str, Any],
        rewritten_score: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compare two evaluations
        
        Args:
            original_score: Original documentation scores
            rewritten_score: Rewritten documentation scores
            
        Returns:
            Comparison analysis
        """
        improvements = []
        regressions = []
        
        criteria = ['accuracy', 'clarity', 'completeness', 'examples', 'structure', 'discoverability']
        
        for criterion in criteria:
            original = original_score.get(f'{criterion}_score', 0)
            rewritten = rewritten_score.get(f'{criterion}_score', 0)
            diff = rewritten - original
            
            if diff > 0.5:
                improvements.append({
                    'criterion': criterion,
                    'improvement': round(diff, 2),
                    'original': original,
                    'new': rewritten
                })
            elif diff < -0.5:
                regressions.append({
                    'criterion': criterion,
                    'regression': round(-diff, 2),
                    'original': original,
                    'new': rewritten
                })
        
        total_improvement = rewritten_score['total_score'] - original_score['total_score']
        
        return {
            'total_improvement': round(total_improvement, 2),
            'improved': total_improvement > 0,
            'improvements': improvements,
            'regressions': regressions,
            'original_total': original_score['total_score'],
            'rewritten_total': rewritten_score['total_score']
        }
    
    def _get_rubric(self) -> str:
        """Get the quality rubric"""
        return """
QUALITY RUBRIC FOR TECHNICAL DOCUMENTATION

1. ACCURACY & CORRECTNESS (30% weight)
   - All technical claims verified against codebase
   - API signatures match actual implementation
   - No outdated or incorrect information
   - Examples are working and tested
   - Version-specific information is clearly marked

2. CLARITY & READABILITY (20% weight)
   - Clear, concise language without jargon overload
   - Proper technical terminology used correctly
   - Logical flow and smooth transitions
   - Complex concepts explained simply
   - Appropriate reading level for target audience

3. COMPLETENESS (20% weight)
   - All necessary information present to accomplish task
   - Edge cases and common errors addressed
   - Prerequisites and requirements mentioned
   - Related concepts cross-referenced
   - No significant information gaps

4. CODE EXAMPLES QUALITY (15% weight)
   - Working, runnable examples provided
   - Examples demonstrate best practices
   - Common use cases covered
   - Examples are well-commented
   - Progressive complexity (simple → advanced)

5. STRUCTURE & ORGANIZATION (10% weight)
   - Proper heading hierarchy
   - Scannable format (lists, tables, callouts)
   - Logical section ordering
   - Appropriate use of formatting
   - Clear visual hierarchy

6. DISCOVERABILITY (5% weight)
   - Searchable keywords present
   - Clear, descriptive titles
   - Proper cross-references and links
   - Tags and metadata appropriate
   - Easy to find via search
"""

# Singleton instance
judge = Judge()

