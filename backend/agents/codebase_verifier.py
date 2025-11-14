"""
Codebase Verification Agent
Deep analysis to prevent hallucinations
"""
from services.repo_analyzer import repo_analyzer
from services.claude_client import claude_client
from typing import Dict, Any, List
import re

class CodebaseVerifier:
    """Agent for verifying documentation against codebase"""
    
    async def verify_documentation(
        self,
        doc_content: str,
        issue_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Verify documentation claims against codebase
        
        Args:
            doc_content: Documentation content to verify
            issue_data: Issue data for context
            
        Returns:
            Verification report with confidence scores
        """
        # Extract technical claims from documentation
        claims = await self._extract_technical_claims(doc_content)
        
        # Verify each claim
        verification_results = []
        
        for claim in claims:
            result = await self._verify_claim(claim)
            verification_results.append(result)
        
        # Calculate overall confidence
        if verification_results:
            confidence = sum(r['confidence'] for r in verification_results) / len(verification_results)
        else:
            confidence = 0.5  # Neutral if no claims to verify
        
        return {
            "overall_confidence": confidence,
            "claims_verified": len(verification_results),
            "claims_passed": sum(1 for r in verification_results if r['verified']),
            "verification_results": verification_results,
            "summary": self._generate_summary(verification_results)
        }
    
    async def _extract_technical_claims(self, doc_content: str) -> List[Dict[str, Any]]:
        """
        Extract technical claims from documentation
        
        Args:
            doc_content: Documentation content
            
        Returns:
            List of claims to verify
        """
        system_prompt = """You are an expert at extracting technical claims from documentation that can be verified against source code.

Extract claims about:
- Function/command names and signatures
- API endpoints and parameters
- Configuration options
- File paths and locations
- Code examples
- Feature availability

DO NOT extract:
- General descriptions
- User advice
- Installation instructions
- Marketing claims"""
        
        user_message = f"""Extract verifiable technical claims from this documentation:

{doc_content[:2000]}

List each claim as a JSON object with: type (function, command, config, file, example), claim (the specific claim), and keywords (array of searchable terms)."""
        
        response_schema = {
            "claims": [
                {
                    "type": "string",
                    "claim": "string",
                    "keywords": ["array", "of", "strings"]
                }
            ]
        }
        
        try:
            result = await claude_client.send_structured_message(
                system_prompt=system_prompt,
                user_message=user_message,
                response_schema=response_schema,
                temperature=0.3
            )
            
            return result.get('claims', [])
            
        except Exception as e:
            print(f"Error extracting claims: {e}")
            return []
    
    async def _verify_claim(self, claim: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify a single claim against codebase
        
        Args:
            claim: Claim to verify
            
        Returns:
            Verification result
        """
        claim_type = claim.get('type', '')
        claim_text = claim.get('claim', '')
        keywords = claim.get('keywords', [])
        
        verified = False
        confidence = 0.0
        evidence = []
        issues = []
        
        # Search codebase for keywords
        for keyword in keywords[:3]:  # Limit to first 3 keywords
            results = repo_analyzer.search_codebase(keyword)
            
            if results:
                verified = True
                confidence += 0.3
                evidence.extend(results[:2])  # Add top 2 results as evidence
        
        # Type-specific verification
        if claim_type == 'function' or claim_type == 'command':
            # Extract function/command name
            func_match = re.search(r'`([a-zA-Z_][a-zA-Z0-9_]*)`', claim_text)
            if func_match:
                func_name = func_match.group(1)
                definitions = repo_analyzer.find_function_definition(func_name)
                
                if definitions:
                    verified = True
                    confidence = 0.9
                    evidence.extend(definitions[:1])
                else:
                    issues.append(f"Function '{func_name}' not found in codebase")
                    confidence = max(0.0, confidence - 0.3)
        
        elif claim_type == 'example':
            # Try to verify code example
            code_match = re.search(r'```(\w+)?\n(.*?)```', claim_text, re.DOTALL)
            if code_match:
                language = code_match.group(1) or 'typescript'
                code = code_match.group(2)
                
                verification = repo_analyzer.verify_code_example(code, language)
                verified = verification['is_valid']
                confidence = verification['confidence']
                
                if not verified:
                    issues.extend(verification['issues'])
        
        # Cap confidence at 1.0
        confidence = min(1.0, confidence)
        
        return {
            "claim": claim_text,
            "type": claim_type,
            "verified": verified,
            "confidence": confidence,
            "evidence": evidence[:2],  # Limit evidence
            "issues": issues
        }
    
    def _generate_summary(self, verification_results: List[Dict[str, Any]]) -> str:
        """
        Generate human-readable summary of verification
        
        Args:
            verification_results: List of verification results
            
        Returns:
            Summary string
        """
        if not verification_results:
            return "No technical claims to verify."
        
        total = len(verification_results)
        passed = sum(1 for r in verification_results if r['verified'])
        
        summary_parts = [
            f"Verified {passed}/{total} technical claims.",
        ]
        
        # Add details about failed verifications
        failed = [r for r in verification_results if not r['verified']]
        if failed:
            summary_parts.append(f"{len(failed)} claims could not be verified:")
            for result in failed[:3]:  # Show first 3
                summary_parts.append(f"  - {result['claim'][:100]}")
        
        return "\n".join(summary_parts)

# Singleton instance
codebase_verifier = CodebaseVerifier()

