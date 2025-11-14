"""
Documentation Search Agent
Finds relevant documentation for an issue
"""
from services.doc_scraper import doc_scraper
from services.github_service import github_service
from services.claude_client import claude_client
from typing import Dict, Any, List

class DocSearcher:
    """Agent for finding relevant documentation"""
    
    async def find_relevant_docs(
        self,
        issue_data: Dict[str, Any],
        classification: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Find documentation relevant to the issue
        
        Args:
            issue_data: GitHub issue data
            classification: Classification result
            
        Returns:
            List of relevant documentation pages
        """
        # First, check if doc URLs are mentioned in the issue
        doc_urls = github_service.extract_doc_urls_from_issue(issue_data)
        
        results = []
        
        # If URLs are found, scrape those pages
        if doc_urls:
            for url in doc_urls[:3]:  # Limit to 3
                try:
                    page_data = await doc_scraper.scrape_page(url)
                    page_data['source'] = 'mentioned_in_issue'
                    results.append(page_data)
                except Exception as e:
                    print(f"Error scraping mentioned URL {url}: {e}")
        
        # If no URLs or need more context, use semantic search
        if len(results) < 2:
            print(f"[DocSearcher] No doc URLs in issue, using default docs page")
            
            try:
                # Fast path: use overview page directly (no extra Claude calls)
                mock_url = "https://code.claude.com/docs/en/overview"
                page_data = await doc_scraper.scrape_page(mock_url)
                page_data['source'] = 'default'
                results.append(page_data)
                print(f"[DocSearcher] ✓ Got documentation from {mock_url}")
                    
            except Exception as e:
                print(f"[DocSearcher] ✗ Error fetching documentation: {e}")
                import traceback
                traceback.print_exc()
        
        # Skip ranking for speed - just return what we found
        return results[:1]  # Return first result only for speed
    
    async def _generate_search_query(
        self,
        issue_data: Dict[str, Any],
        classification: Dict[str, Any]
    ) -> str:
        """
        Generate optimal search query for documentation
        
        Args:
            issue_data: Issue data
            classification: Classification result
            
        Returns:
            Search query string
        """
        system_prompt = """You are an expert at creating search queries to find relevant documentation.
Generate a concise search query that will find the most relevant documentation page."""
        
        user_message = f"""Issue Title: {issue_data['title']}

Issue Body: {issue_data.get('body', '')[:500]}

Gap Type: {classification.get('gap_type', 'unknown')}

Generate a search query (2-5 words) to find the relevant documentation page."""
        
        try:
            response = await claude_client.send_message(
                system_prompt=system_prompt,
                user_message=user_message,
                temperature=0.3
            )
            
            # Extract just the query (remove any explanation)
            query = response.strip().split('\n')[0]
            return query
            
        except Exception:
            # Fallback to issue title
            return issue_data['title']
    
    async def _rank_results(
        self,
        issue_data: Dict[str, Any],
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Use Claude to rank documentation results by relevance
        
        Args:
            issue_data: Issue data
            results: List of documentation pages
            
        Returns:
            Ranked list of results
        """
        system_prompt = """You are an expert at determining which documentation pages are most relevant to an issue.
Rank the provided documentation pages by relevance."""
        
        # Prepare results summary
        results_summary = "\n\n".join([
            f"Page {i+1}:\nTitle: {r['title']}\nURL: {r['url']}\nExcerpt: {r['content'][:300]}..."
            for i, r in enumerate(results)
        ])
        
        user_message = f"""Issue: {issue_data['title']}
Issue Description: {issue_data.get('body', '')[:300]}

Documentation Pages:
{results_summary}

Rank these pages by relevance (most relevant first). Respond with just the page numbers in order, comma-separated (e.g., "2,1,3")."""
        
        try:
            response = await claude_client.send_message(
                system_prompt=system_prompt,
                user_message=user_message,
                temperature=0.2
            )
            
            # Parse ranking
            ranking_str = response.strip().split('\n')[0]
            rankings = [int(x.strip()) - 1 for x in ranking_str.split(',') if x.strip().isdigit()]
            
            # Reorder results
            ranked_results = []
            for idx in rankings:
                if 0 <= idx < len(results):
                    ranked_results.append(results[idx])
            
            # Add any missing results at the end
            for i, result in enumerate(results):
                if i not in rankings:
                    ranked_results.append(result)
            
            return ranked_results
            
        except Exception:
            # If ranking fails, return original order
            return results

# Singleton instance
doc_searcher = DocSearcher()

