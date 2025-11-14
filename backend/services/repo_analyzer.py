"""
Repository analyzer for code verification
"""
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
from config import settings
import re
import json

class RepoAnalyzer:
    """Service for analyzing the claude-code repository"""
    
    def __init__(self):
        self.repo_url = settings.claude_code_repo_url
        self.cache_dir = Path(settings.repo_cache_dir)
        self.repo_path = self.cache_dir / "claude-code"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def ensure_repo_cloned(self) -> Path:
        """
        Ensure repository is cloned and up to date
        
        Returns:
            Path to repository
        """
        if self.repo_path.exists():
            # Pull latest changes
            try:
                subprocess.run(
                    ["git", "pull"],
                    cwd=self.repo_path,
                    capture_output=True,
                    check=True
                )
            except subprocess.CalledProcessError:
                # If pull fails, re-clone
                import shutil
                shutil.rmtree(self.repo_path)
                self._clone_repo()
        else:
            self._clone_repo()
        
        return self.repo_path
    
    def _clone_repo(self):
        """Clone the repository"""
        subprocess.run(
            ["git", "clone", self.repo_url, str(self.repo_path)],
            capture_output=True,
            check=True
        )
    
    def search_codebase(
        self,
        query: str,
        file_patterns: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search codebase for query
        
        Args:
            query: Search term (function name, class, etc.)
            file_patterns: File patterns to search (e.g., ['*.ts', '*.py'])
            
        Returns:
            List of search results with file, line, and content
        """
        self.ensure_repo_cloned()
        
        results = []
        
        try:
            # Use git grep for fast searching
            cmd = ["git", "grep", "-n", "-i", query]
            if file_patterns:
                for pattern in file_patterns:
                    cmd.extend(["--", pattern])
            
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if ':' in line:
                        parts = line.split(':', 2)
                        if len(parts) >= 3:
                            results.append({
                                "file": parts[0],
                                "line": parts[1],
                                "content": parts[2].strip()
                            })
            
        except Exception as e:
            print(f"Error searching codebase: {e}")
        
        return results
    
    def get_file_content(self, file_path: str) -> Optional[str]:
        """
        Get content of a file in the repository
        
        Args:
            file_path: Relative path to file
            
        Returns:
            File content or None
        """
        self.ensure_repo_cloned()
        
        full_path = self.repo_path / file_path
        if full_path.exists():
            try:
                return full_path.read_text(encoding='utf-8')
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")
        
        return None
    
    def find_function_definition(self, function_name: str) -> List[Dict[str, Any]]:
        """
        Find function definitions in codebase
        
        Args:
            function_name: Name of function to find
            
        Returns:
            List of function definitions with context
        """
        # Search for function definitions
        patterns = [
            f"function {function_name}",
            f"def {function_name}",
            f"const {function_name} =",
            f"export function {function_name}",
            f"async function {function_name}",
        ]
        
        results = []
        for pattern in patterns:
            matches = self.search_codebase(pattern)
            results.extend(matches)
        
        # Get surrounding context for each match
        enriched_results = []
        for match in results:
            content = self.get_file_content(match['file'])
            if content:
                lines = content.split('\n')
                line_num = int(match['line']) - 1
                
                # Get 10 lines before and after
                start = max(0, line_num - 10)
                end = min(len(lines), line_num + 10)
                context = '\n'.join(lines[start:end])
                
                enriched_results.append({
                    **match,
                    "context": context,
                    "start_line": start + 1,
                    "end_line": end
                })
        
        return enriched_results
    
    def verify_code_example(self, code: str, language: str = "typescript") -> Dict[str, Any]:
        """
        Verify if code example is valid
        
        Args:
            code: Code snippet to verify
            language: Programming language
            
        Returns:
            Verification result with confidence and issues
        """
        # This is a simplified verification
        # In production, you'd want to actually run the code or use a linter
        
        issues = []
        confidence = 1.0
        
        # Check for common issues
        if language in ["typescript", "javascript"]:
            # Check for undefined variables/functions
            # Look for function calls
            function_calls = re.findall(r'(\w+)\s*\(', code)
            
            for func_name in function_calls:
                # Search if function exists in codebase
                results = self.search_codebase(func_name)
                if not results:
                    issues.append(f"Function '{func_name}' not found in codebase")
                    confidence *= 0.8
        
        elif language == "python":
            # Similar checks for Python
            imports = re.findall(r'from\s+(\S+)\s+import', code)
            for module in imports:
                results = self.search_codebase(module, ["*.py"])
                if not results:
                    issues.append(f"Module '{module}' not found in codebase")
                    confidence *= 0.8
        
        return {
            "is_valid": len(issues) == 0,
            "confidence": confidence,
            "issues": issues,
            "checked_elements": len(function_calls) if language in ["typescript", "javascript"] else 0
        }
    
    def get_api_signature(self, api_name: str) -> Optional[Dict[str, Any]]:
        """
        Get API signature from codebase
        
        Args:
            api_name: Name of API/function
            
        Returns:
            API signature information
        """
        definitions = self.find_function_definition(api_name)
        
        if definitions:
            best_match = definitions[0]
            
            # Extract parameters from context
            context = best_match.get('context', '')
            
            # Simple parameter extraction (would be better with AST parsing)
            param_match = re.search(rf'{api_name}\s*\((.*?)\)', context)
            params = param_match.group(1) if param_match else ""
            
            return {
                "name": api_name,
                "file": best_match['file'],
                "line": best_match['line'],
                "parameters": params,
                "context": context
            }
        
        return None

# Singleton instance
repo_analyzer = RepoAnalyzer()

