"""
Issue Classification Agent
Determines if an issue is documentation-related
"""
from services.claude_client import claude_client
from typing import Dict, Any

class IssueClassifier:
    """Agent for classifying documentation issues"""
    
    async def classify_issue(self, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify if an issue is documentation-related
        
        Args:
            issue_data: GitHub issue data
            
        Returns:
            Classification result with confidence and gap type
        """
        system_prompt = """You are an expert at analyzing GitHub issues to determine if they are documentation-related.

Documentation issues include:
- Missing documentation
- Incorrect or outdated documentation
- Unclear or confusing documentation
- Missing code examples
- Documentation bugs or typos
- Requests for better documentation

NOT documentation issues:
- Feature requests (unless specifically asking for docs)
- Bug reports about the software itself
- Questions that should be answered by existing docs but aren't asking for doc improvements"""

        # Prepare issue context
        comments_text = "\n\n".join([
            f"Comment by {c['author']}: {c['body']}"
            for c in issue_data.get('comments', [])[:5]  # Limit to first 5 comments
        ])
        
        user_message = f"""Analyze this GitHub issue and determine if it's documentation-related:

Title: {issue_data['title']}

Body: {issue_data.get('body', 'No description provided')}

Comments (first 5):
{comments_text if comments_text else 'No comments'}

Classify this issue and identify the type of documentation gap if applicable."""

        response_schema = {
            "is_doc_issue": "boolean",
            "confidence": "float (0-1)",
            "gap_type": "string (one of: missing, incorrect, unclear, outdated, example_needed, or null)",
            "reasoning": "string explaining your decision"
        }
        
        try:
            result = await claude_client.send_structured_message(
                system_prompt=system_prompt,
                user_message=user_message,
                response_schema=response_schema,
                temperature=0.3  # Lower temperature for more consistent classification
            )
            
            return result
            
        except Exception as e:
            raise Exception(f"Classification failed: {str(e)}")

# Singleton instance
issue_classifier = IssueClassifier()

