"""
Configuration management using environment variables
"""
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # API Keys
    anthropic_api_key: str
    github_token: str
    
    # Database
    postgres_connection_string: str
    
    # Repository URLs
    claude_code_repo_url: str = "https://github.com/anthropics/claude-code"
    docs_base_url: str = "https://code.claude.com/docs/en/"
    
    # Agent Configuration
    max_iterations: int = 2
    improvement_iterations: int = 1
    claude_model: str = "claude-sonnet-4-20250514"
    
    # Local paths
    repo_cache_dir: str = "./cache/repos"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()

