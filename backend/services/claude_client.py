"""
Anthropic Claude API wrapper service
"""
import anthropic
from config import settings
from typing import Optional, Dict, Any
import json
import asyncio

class ClaudeClient:
    """Wrapper for Anthropic Claude API"""
    
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.claude_model
    
    async def send_message(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> str:
        """
        Send a message to Claude and get response
        
        Args:
            system_prompt: System prompt defining Claude's role
            user_message: User message/question
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response
            
        Returns:
            Claude's response text
        """
        try:
            print(f"[ClaudeClient] Sending message to Claude (max_tokens={max_tokens})")
            
            # Run the synchronous API call in a thread pool to avoid blocking
            message = await asyncio.to_thread(
                self.client.messages.create,
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )
            
            print(f"[ClaudeClient] ✓ Received response from Claude")
            return message.content[0].text
            
        except Exception as e:
            print(f"[ClaudeClient] ✗ Claude API error: {e}")
            raise Exception(f"Claude API error: {str(e)}")
    
    async def send_structured_message(
        self,
        system_prompt: str,
        user_message: str,
        response_schema: Dict[str, Any],
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """
        Send message and request structured JSON response
        
        Args:
            system_prompt: System prompt
            user_message: User message
            response_schema: Expected JSON schema
            temperature: Sampling temperature
            max_tokens: Max tokens
            
        Returns:
            Parsed JSON response
        """
        schema_str = json.dumps(response_schema, indent=2)
        enhanced_prompt = f"""{system_prompt}

You must respond with a valid JSON object matching this schema:
{schema_str}

Respond ONLY with the JSON object, no additional text."""
        
        response_text = await self.send_message(
            system_prompt=enhanced_prompt,
            user_message=user_message,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Extract JSON from response (handle markdown code blocks)
        response_text = response_text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        try:
            return json.loads(response_text.strip())
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse JSON response: {str(e)}\nResponse: {response_text}")

# Singleton instance
claude_client = ClaudeClient()

