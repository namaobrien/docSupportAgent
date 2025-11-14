"""
Documentation scraper for code.claude.com
"""
import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from config import settings
import re
import html2text

class DocScraper:
    """Service for scraping Claude Code documentation"""
    
    def __init__(self):
        self.base_url = settings.docs_base_url.rstrip('/')
        self.timeout = 30.0
    
    async def scrape_page(self, url: str) -> Dict[str, str]:
        """
        Scrape a documentation page
        
        Args:
            url: Full URL to documentation page
            
        Returns:
            Dictionary with title, content, and url
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'lxml')
                
                # Remove script and style elements
                for script in soup(["script", "style", "nav", "footer"]):
                    script.decompose()
                
                # Get title
                title = ""
                title_tag = soup.find('h1')
                if title_tag:
                    title = title_tag.get_text(strip=True)
                elif soup.title:
                    title = soup.title.get_text(strip=True)
                
                # Get main content
                # Try to find main content area
                main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
                
                # Remove navigation and UI elements before conversion
                if main_content:
                    # Remove common navigation elements
                    for element in main_content.find_all(['nav', 'header', 'footer']):
                        element.decompose()
                    # Remove language selector
                    for element in main_content.find_all('img', alt=re.compile(r'^[A-Z]{2}$')):
                        element.decompose()
                    # Remove logo images
                    for element in main_content.find_all('img', src=re.compile(r'logo')):
                        element.decompose()
                
                # Convert HTML to clean markdown
                h = html2text.HTML2Text()
                h.ignore_links = False
                h.ignore_images = True  # Ignore images - they're usually UI elements
                h.ignore_emphasis = False
                h.body_width = 0  # Don't wrap lines
                h.ignore_tables = False
                
                if main_content:
                    content = h.handle(str(main_content))
                else:
                    content = h.handle(str(soup))
                
                # Clean up markdown - remove navigation artifacts
                content = re.sub(r'Skip to main content\n+', '', content)
                content = re.sub(r'\n\n\n+', '\n\n', content)  # Remove excessive blank lines
                content = re.sub(r'⌘[A-Z]', '', content)  # Remove keyboard shortcuts
                content = content.strip()
                
                return {
                    "title": title,
                    "content": content,
                    "url": url,
                    "format": "markdown"
                }
                
            except Exception as e:
                raise Exception(f"Failed to scrape {url}: {str(e)}")
    
    async def search_documentation(
        self,
        query: str,
        max_results: int = 5
    ) -> List[Dict[str, str]]:
        """
        Search documentation for relevant pages
        
        Args:
            query: Search query (issue title/description)
            max_results: Maximum number of results
            
        Returns:
            List of relevant documentation pages
        """
        # This is a simplified search - in production, you'd want to:
        # 1. Use site search API if available
        # 2. Build a search index
        # 3. Use embeddings for semantic search
        
        # For now, we'll scrape the overview page and follow links
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                # Get overview/index page
                overview_url = f"{self.base_url}/overview"
                response = await client.get(overview_url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'lxml')
                
                # Find all documentation links
                links = []
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if href.startswith('/docs/'):
                        full_url = f"https://code.claude.com{href}"
                        links.append(full_url)
                    elif href.startswith('http') and 'code.claude.com/docs/' in href:
                        links.append(href)
                
                # Remove duplicates
                links = list(set(links))[:max_results * 2]  # Get extra for filtering
                
                # Scrape each page and score relevance
                results = []
                query_lower = query.lower()
                
                for link in links[:max_results * 2]:  # Limit to avoid too many requests
                    try:
                        page_data = await self.scrape_page(link)
                        
                        # Simple relevance scoring
                        content_lower = page_data['content'].lower()
                        title_lower = page_data['title'].lower()
                        
                        score = 0
                        # Check for query terms
                        query_terms = query_lower.split()
                        for term in query_terms:
                            if len(term) > 3:  # Ignore short words
                                score += content_lower.count(term) * 1
                                score += title_lower.count(term) * 5
                        
                        if score > 0:
                            page_data['relevance_score'] = score
                            results.append(page_data)
                        
                    except Exception as e:
                        print(f"Error scraping {link}: {e}")
                        continue
                
                # Sort by relevance and return top results
                results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
                return results[:max_results]
                
            except Exception as e:
                raise Exception(f"Failed to search documentation: {str(e)}")
    
    async def get_common_doc_pages(self) -> List[str]:
        """
        Get list of common documentation page URLs
        
        Returns:
            List of common doc URLs
        """
        base = self.base_url
        return [
            f"{base}/overview",
            f"{base}/getting-started",
            f"{base}/installation",
            f"{base}/usage",
            f"{base}/commands",
            f"{base}/configuration",
            f"{base}/troubleshooting",
            f"{base}/faq",
        ]

# Singleton instance
doc_scraper = DocScraper()

