"""
Simple, fast documentation improvement agent
ONE Claude call, ONE result
"""
from services.claude_client import claude_client
from services.github_service import github_service
from services.doc_scraper import doc_scraper
from typing import Dict, Any

class SimpleAgent:
    """Fast, simple documentation improvement agent"""
    
    async def improve_documentation(self, issue_number: int) -> Dict[str, Any]:
        """
        Improve documentation for an issue - FAST and SIMPLE
        
        Returns:
            {
                'issue_number': int,
                'issue_title': str,
                'improved_docs': str,
                'score': float,
                'time_taken': float
            }
        """
        import time
        start = time.time()
        
        print(f"[SimpleAgent] Starting fast analysis for issue #{issue_number}")
        
        # Get issue
        issue_data = github_service.get_issue(issue_number)
        print(f"[SimpleAgent] Got issue: {issue_data['title']}")
        
        # Find relevant documentation page using keyword matching
        try:
            print(f"[SimpleAgent] Searching for relevant docs...")
            
            body_text = issue_data.get('body', '') or ''
            title_text = issue_data.get('title', '') or ''
            full_text = (title_text + ' ' + body_text).lower()
            
            # Look for doc URLs in issue first
            import re
            doc_urls = re.findall(r'https://code\.claude\.com/docs/[^\s\)]+', body_text + ' ' + title_text)
            if doc_urls:
                doc_url = doc_urls[0]
                print(f"[SimpleAgent] Found doc URL in issue: {doc_url}")
            else:
                # Comprehensive doc page mapping with keywords
                doc_pages = {
                    'installation': ['install', 'setup', 'download', 'winget', 'brew', 'apt', 'package manager'],
                    'quickstart': ['getting started', 'first time', 'quick start', 'begin', 'tutorial'],
                    'common-workflows': ['workflow', 'how to', 'guide', 'example', 'use case'],
                    'troubleshooting': ['error', 'issue', 'problem', 'fix', 'not working', 'crash', 'bug', 'failed'],
                    'ide-setup': ['vscode', 'ide', 'editor', 'cursor', 'jetbrains', 'vim', 'emacs'],
                    'cli-reference': ['command', 'cli', 'flag', 'option', 'argument', 'terminal'],
                    'interactive-mode': ['interactive', 'repl', 'chat', 'conversation'],
                    'slash-commands': ['slash command', '/command', 'command list'],
                    'mcp': ['mcp', 'model context protocol', 'integration', 'tool'],
                    'sub-agents': ['agent', 'sub-agent', 'delegation', 'agentic'],
                    'settings': ['config', 'setting', 'preference', 'configuration', '.claude'],
                    'hooks': ['hook', 'lifecycle', 'event', 'trigger'],
                    'plugins-reference': ['plugin', 'extension', 'addon'],
                    'checkpointing': ['checkpoint', 'save', 'restore', 'state'],
                    'third-party-integrations': ['integration', 'third party', 'external'],
                    'setup': ['admin', 'deployment', 'enterprise', 'team'],
                }
                
                # Score each page based on keyword matches
                scores = {}
                for page, keywords in doc_pages.items():
                    score = sum(1 for keyword in keywords if keyword in full_text)
                    if score > 0:
                        scores[page] = score
                
                # Get highest scoring page
                if scores:
                    best_page = max(scores, key=scores.get)
                    doc_url = f"https://code.claude.com/docs/en/{best_page}"
                    print(f"[SimpleAgent] Matched keywords → {best_page} (score: {scores[best_page]})")
                else:
                    # No keywords matched, default to overview
                    doc_url = "https://code.claude.com/docs/en/overview"
                    print(f"[SimpleAgent] No keyword matches, using overview")
            
            # Scrape the relevant page
            doc_data = await doc_scraper.scrape_page(doc_url)
            original_docs = doc_data['content']
            print(f"[SimpleAgent] Got {len(original_docs)} chars from {doc_url}")
            
        except Exception as e:
            print(f"[SimpleAgent] Error getting docs: {e}")
            # Fallback to overview
            doc_url = "https://code.claude.com/docs/en/overview"
            try:
                doc_data = await doc_scraper.scrape_page(doc_url)
                original_docs = doc_data['content']
            except:
                original_docs = "Documentation not available"
        
        # ONE Claude call to do everything
        system_prompt = """You are a technical documentation expert. 

Your task: Review the issue and its comments and the original documentation, then suggest targeted improvements to address the user's feedback.

Focus on:
- Understanding the specific problem or gap the user identified
- Proposing clear, actionable improvements to the relevant section(s)
- Adding missing information, examples, or clarifications
- Improving structure or wording where needed

Provide:
1. Targeted documentation improvements (markdown format) - focus on the relevant sections
2. Quality scores for 6 criteria (1-10 each): Accuracy, Clarity, Completeness, Examples, Structure, Discoverability
3. Brief explanation of what you improved and why"""

        # Format comments
        comments_text = ""
        comments = issue_data.get('comments', [])
        if comments:
            comments_text = "\n\nCOMMENTS:\n"
            for i, comment in enumerate(comments[:5], 1):  # Limit to 5 comments
                comments_text += f"\n{i}. {comment['author']}:\n{comment['body'][:300]}\n"
        
        user_message = f"""ISSUE: {issue_data['title']}

DESCRIPTION: {issue_data.get('body', 'N/A')[:500]}{comments_text}

ORIGINAL DOCUMENTATION:
{original_docs[:5000]}

Based on this issue and its comments, suggest targeted improvements to the documentation. Focus on addressing the user's specific feedback.

Format your response as:

IMPROVED_DOCS:
[your targeted documentation improvements in markdown format]

RUBRIC_SCORES:
Accuracy: [1-10]
Clarity: [1-10]
Completeness: [1-10]
Examples: [1-10]
Structure: [1-10]
Discoverability: [1-10]

EXPLANATION: [brief explanation of what you improved and why]"""

        print(f"[SimpleAgent] Calling Claude...")
        response = await claude_client.send_message(
            system_prompt=system_prompt,
            user_message=user_message,
            temperature=0.7,
            max_tokens=3000  # Enough for targeted improvements
        )
        print(f"[SimpleAgent] Got response")
        
        # Parse response
        improved_docs = response
        explanation = ""
        
        # Extract improved docs
        if "IMPROVED_DOCS:" in response:
            parts = response.split("IMPROVED_DOCS:", 1)
            if len(parts) > 1:
                docs_section = parts[1].split("RUBRIC_SCORES:", 1)[0] if "RUBRIC_SCORES:" in parts[1] else parts[1].split("EXPLANATION:", 1)[0]
                improved_docs = docs_section.strip()
        
        # Parse rubric scores
        rubric_scores = {
            'accuracy': 8.0,
            'clarity': 8.0,
            'completeness': 8.0,
            'examples': 8.0,
            'structure': 8.0,
            'discoverability': 8.0
        }
        
        if "RUBRIC_SCORES:" in response:
            try:
                scores_section = response.split("RUBRIC_SCORES:")[1].split("EXPLANATION:")[0]
                for line in scores_section.split('\n'):
                    for key in rubric_scores.keys():
                        if key.capitalize() in line and ':' in line:
                            score_str = line.split(':')[1].strip()
                            rubric_scores[key] = float(score_str.split()[0])
            except Exception as e:
                print(f"[SimpleAgent] Warning: Could not parse all rubric scores: {e}")
        
        # Extract explanation
        if "EXPLANATION:" in response:
            explanation = response.split("EXPLANATION:")[1].strip()
        
        # Calculate total score
        total_score = sum(rubric_scores.values()) / len(rubric_scores)
        
        elapsed = time.time() - start
        print(f"[SimpleAgent] ✓ Complete in {elapsed:.1f}s - Score: {total_score:.1f}/10")
        
        return {
            'issue_number': issue_number,
            'issue_title': issue_data['title'],
            'issue_url': issue_data['url'],
            'doc_url': doc_url,
            'original_docs': original_docs,
            'improved_docs': improved_docs,
            'rubric_scores': rubric_scores,
            'total_score': round(total_score, 2),
            'explanation': explanation,
            'time_taken': round(elapsed, 1),
            'status': 'completed'
        }

# Singleton
simple_agent = SimpleAgent()

