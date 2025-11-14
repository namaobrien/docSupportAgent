"""
GitHub API client service
"""
from github import Github
from github.Issue import Issue as GithubIssue
from config import settings
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

class GitHubService:
    """Service for interacting with GitHub API"""
    
    def __init__(self):
        self.client = None
        self.repo = None
        self.repo_url = settings.claude_code_repo_url
        # Extract owner/repo from URL
        parts = self.repo_url.rstrip('/').split('/')
        self.repo_name = f"{parts[-2]}/{parts[-1]}"
    
    def _ensure_initialized(self):
        """Lazy initialization of GitHub client"""
        if self.client is None:
            self.client = Github(settings.github_token)
            self.repo = self.client.get_repo(self.repo_name)
    
    def search_issues(
        self,
        days: int = 30,
        label: Optional[str] = "documentation",
        state: str = "all"
    ) -> List[Dict[str, Any]]:
        """
        Search for issues in the repository
        
        Args:
            days: Number of days to look back
            label: Filter by label (None for all)
            state: Issue state (open, closed, all)
            
        Returns:
            List of issue dictionaries
        """
        self._ensure_initialized()
        since_date = datetime.now() - timedelta(days=days)
        
        # Build query
        query_parts = [
            f"repo:{self.repo_name}",
            f"is:issue",
            f"created:>={since_date.strftime('%Y-%m-%d')}"
        ]
        
        if label:
            query_parts.append(f"label:{label}")
        
        if state != "all":
            query_parts.append(f"state:{state}")
        
        query = " ".join(query_parts)
        
        # Search issues
        issues = self.client.search_issues(query, sort="created", order="desc")
        
        result = []
        for issue in issues:
            result.append(self._format_issue(issue))
        
        return result
    
    def get_issue(self, issue_number: int) -> Dict[str, Any]:
        """
        Get a specific issue by number
        
        Args:
            issue_number: Issue number
            
        Returns:
            Issue dictionary
        """
        self._ensure_initialized()
        issue = self.repo.get_issue(issue_number)
        return self._format_issue(issue)
    
    def _format_issue(self, issue: GithubIssue) -> Dict[str, Any]:
        """
        Format GitHub issue object to dictionary
        
        Args:
            issue: GitHub issue object
            
        Returns:
            Formatted issue dictionary
        """
        # Get comments
        comments = []
        for comment in issue.get_comments():
            comments.append({
                "author": comment.user.login if comment.user else "unknown",
                "body": comment.body,
                "created_at": comment.created_at.isoformat() if comment.created_at else None,
                "url": comment.html_url
            })
        
        # Get labels
        labels = [label.name for label in issue.labels]
        
        return {
            "issue_number": issue.number,
            "title": issue.title,
            "body": issue.body or "",
            "url": issue.html_url,
            "state": issue.state,
            "labels": labels,
            "comments": comments,
            "created_at": issue.created_at.isoformat() if issue.created_at else None,
            "updated_at": issue.updated_at.isoformat() if issue.updated_at else None,
            "author": issue.user.login if issue.user else "unknown"
        }
    
    def extract_doc_urls_from_issue(self, issue_data: Dict[str, Any]) -> List[str]:
        """
        Extract documentation URLs mentioned in issue or comments
        
        Args:
            issue_data: Issue dictionary
            
        Returns:
            List of documentation URLs found
        """
        import re
        
        doc_base = settings.docs_base_url
        url_pattern = re.compile(r'https?://code\.claude\.com/docs/[^\s\)]+')
        
        urls = set()
        
        # Check issue body
        if issue_data.get("body"):
            urls.update(url_pattern.findall(issue_data["body"]))
        
        # Check comments
        for comment in issue_data.get("comments", []):
            if comment.get("body"):
                urls.update(url_pattern.findall(comment["body"]))
        
        return list(urls)

# Singleton instance
github_service = GitHubService()

