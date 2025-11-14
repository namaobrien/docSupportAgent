"""
Documentation Rewriter Agent
Generates improved documentation
"""
from services.claude_client import claude_client
from typing import Dict, Any, Optional

class DocRewriter:
    """Agent for rewriting documentation"""
    
    async def rewrite_documentation(
        self,
        original_doc: str,
        issue_data: Dict[str, Any],
        previous_feedback: Optional[str] = None,
        iteration_number: int = 1
    ) -> Dict[str, Any]:
        """
        Rewrite documentation to address the issue
        
        Args:
            original_doc: Original documentation content
            issue_data: GitHub issue data
            previous_feedback: Feedback from previous iteration
            iteration_number: Current iteration number
            
        Returns:
            Rewrite result with content and metadata
        """
        # Load style guide
        style_guide = self._get_style_guide()
        
        system_prompt = f"""You are an expert technical writer specializing in developer documentation.

Your task is to rewrite documentation to address user issues while maintaining:
- Technical accuracy
- Clarity and readability
- Comprehensive coverage
- Practical code examples
- Proper structure and organization

{style_guide}

Focus on addressing the user's specific concern while improving overall documentation quality."""

        # Build context
        context_parts = [
            f"=== ORIGINAL DOCUMENTATION ===\n{original_doc}\n",
            f"\n=== USER ISSUE ===\nTitle: {issue_data['title']}\n",
            f"Description: {issue_data.get('body', '')[:500]}\n",
        ]
        
        if previous_feedback:
            context_parts.append(f"\n=== FEEDBACK FROM PREVIOUS ITERATION ===\n{previous_feedback}\n")
            context_parts.append(f"\n=== INSTRUCTION ===\nThis is iteration {iteration_number}. Address the feedback above while maintaining improvements from previous version.\n")
        else:
            context_parts.append("\n=== INSTRUCTION ===\nRewrite the documentation to address the user's issue. Focus on clarity, completeness, and accuracy.\n")
        
        user_message = "".join(context_parts)
        
        try:
            rewritten_content = await claude_client.send_message(
                system_prompt=system_prompt,
                user_message=user_message,
                temperature=0.7,
                max_tokens=4096
            )
            
            # Simple improvement note
            improvement_focus = f"Iteration {iteration_number}: Addressing user issue and judge feedback"
            
            return {
                "content": rewritten_content,
                "improvement_focus": improvement_focus,
                "changes_made": []  # Skip detailed change tracking for speed
            }
            
        except Exception as e:
            raise Exception(f"Rewrite failed: {str(e)}")
    
    def _get_style_guide(self) -> str:
        """Get documentation style guide"""
        return """
STYLE GUIDE:
- Use clear, concise language
- Start with most common use cases
- Include working code examples
- Use proper heading hierarchy (# ## ###)
- Use code blocks with language tags
- Cross-reference related documentation
- Address edge cases and common errors
- Include prerequisites and requirements
- Use consistent terminology
- Make content scannable with lists and tables
"""
    
    async def _identify_improvements(
        self,
        original: str,
        rewritten: str,
        issue_data: Dict[str, Any]
    ) -> str:
        """
        Identify what this iteration focused on improving
        
        Args:
            original: Original documentation
            rewritten: Rewritten documentation
            issue_data: Issue data
            
        Returns:
            Description of improvements
        """
        system_prompt = """You are analyzing changes between two versions of documentation.
Identify the key improvements made in 1-2 sentences."""
        
        user_message = f"""Issue being addressed: {issue_data['title']}

What are the key improvements in the rewritten version?
(Consider: added examples, clearer explanations, better structure, more complete information, fixed errors)

Respond in 1-2 sentences."""
        
        try:
            response = await claude_client.send_message(
                system_prompt=system_prompt,
                user_message=user_message,
                temperature=0.3,
                max_tokens=200
            )
            return response.strip()
        except Exception:
            return "Improved documentation to address issue"
    
    def _summarize_changes(self, original: str, rewritten: str) -> list:
        """
        Summarize specific changes made
        
        Args:
            original: Original content
            rewritten: Rewritten content
            
        Returns:
            List of changes
        """
        changes = []
        
        # Check for added code examples
        original_code_blocks = original.count('```')
        rewritten_code_blocks = rewritten.count('```')
        if rewritten_code_blocks > original_code_blocks:
            changes.append(f"Added {rewritten_code_blocks - original_code_blocks} code examples")
        
        # Check for added sections
        original_headers = len([line for line in original.split('\n') if line.startswith('#')])
        rewritten_headers = len([line for line in rewritten.split('\n') if line.startswith('#')])
        if rewritten_headers > original_headers:
            changes.append(f"Added {rewritten_headers - original_headers} new sections")
        
        # Check length change
        length_diff = len(rewritten) - len(original)
        if abs(length_diff) > 500:
            if length_diff > 0:
                changes.append(f"Expanded content by {length_diff} characters")
            else:
                changes.append(f"Condensed content by {-length_diff} characters")
        
        if not changes:
            changes.append("Improved clarity and accuracy")
        
        return changes

# Singleton instance
doc_rewriter = DocRewriter()

