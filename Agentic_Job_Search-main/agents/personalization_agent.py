from typing import Dict, Any, List
import os
import re
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel

class AuditResult(BaseModel):
    score: int
    flags: List[str]
    is_biased: bool

class PersonalizationAgent:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found")
        
        self.audit_enabled = False
        try:
            self.llm = ChatGroq(
                model="llama-3.3-70b-versatile",
                temperature=0.3,
                api_key=api_key
            )
            # Test if the model is accessible
            test_response = self.llm.invoke([HumanMessage(content="Test")])
            if test_response:
                self.audit_enabled = True
                print("✓ Groq API initialized successfully for bias auditing")
        except Exception as e:
            print(f"⚠ Gemini API unavailable: {str(e)[:100]}")
            print("  Audit feature disabled. Core job search will continue normally.")
            self.llm = None

    def audit_job(self, job_text: str) -> AuditResult:
        """
        Audits a job description for bias/inclusivity.
        """
        # Skip if API not available - use basic heuristic instead
        if not self.audit_enabled:
            # Simple heuristic: check for common bias indicators
            score = 75  # Base score (lowered from 85)
            flags = []
            
            text_lower = job_text.lower()
            
            # Deduct points for potentially biased language
            bias_words = ['ninja', 'rockstar', 'guru', 'dominant', 'aggressive', 'young', 'energetic', 
                         'competitive', 'ambitious', 'assertive', 'strong', 'dynamic']
            found_bias = [word for word in bias_words if word in text_lower]
            
            if found_bias:
                score -= len(found_bias) * 8  # Increased penalty from 5 to 8
                flags.append(f"Potentially biased terms: {', '.join(found_bias[:3])}")  # Show first 3
            
            # Reward for inclusive language
            inclusive_words = ['diverse', 'inclusive', 'equitable', 'accessible', 'flexible', 
                              'collaborative', 'supportive', 'balanced', 'equal opportunity']
            found_inclusive = [word for word in inclusive_words if word in text_lower]
            
            if found_inclusive:
                score += len(found_inclusive) * 4  # Increased reward from 3 to 4
                score = min(score, 100)  # Cap at 100
            
            # Additional factors for variation
            # Deduct points for very long requirements (might be exclusionary)
            if len(job_text) > 2000:
                score -= 5
                
            # Deduct if uses ALL CAPS extensively (aggressive tone)
            caps_ratio = sum(1 for c in job_text if c.isupper()) / max(len(job_text), 1)
            if caps_ratio > 0.15:
                score -= 10
                flags.append("Excessive capitalization detected")
            
            if not flags:
                flags = ["Basic audit completed (API unavailable)"]
            
            return AuditResult(
                score=max(45, min(100, score)),  # Keep between 45-100 for more range
                flags=flags,
                is_biased=(score < 70)
            )
            
        # Fallback result in case of failure
        fallback_result = AuditResult(
            score=70,  # Neutral/Passing score
            flags=["Audit Skipped (Service Unavailable)"],
            is_biased=False
        )

        prompt = f"""
        Analyze this job description for inclusive language.
        Check for:
        1. Gender-coded words (e.g., 'ninja', 'dominant', 'nurturing')
        2. Ageism
        3. Ableism
        
        Return a score from 0-100 (100 = perfectly inclusive) and a list of specific flags.
        Format output exactly as:
        SCORE: <number>
        FLAGS: <flag1>, <flag2> (or 'None')
        
        Job Text (truncated):
        {job_text[:1500]}
        """
        
        try:
            resp = self.llm.invoke([HumanMessage(content=prompt)]).content
            
            if not resp:
                return fallback_result

            # Parse response
            score_match = re.search(r"SCORE:\s*(\d+)", resp)
            score = int(score_match.group(1)) if score_match else 75
            
            flags_match = re.search(r"FLAGS:\s*(.+)", resp)
            flags_text = flags_match.group(1).strip() if flags_match else "None"
            flags = [f.strip() for f in flags_text.split(",") if f.strip().lower() != "none"]
            
            return AuditResult(
                score=score,
                flags=flags,
                is_biased=(score < 70)
            )
        except Exception as e:
            # Fallback must be returned but let's print the actual error to stderr for logs
            # And modify the flag to show the error reason if possible in a user-friendly way
            error_msg = str(e)
            if "quota" in error_msg.lower():
                reason = "Quota Exceeded"
            elif "key" in error_msg.lower():
                reason = "Invalid API Key"
            else:
                # Expose the actual error for debugging
                reason = f"Error: {error_msg[:100]}"
            
            print(f"Audit API Error: {error_msg}")
            
            return AuditResult(
                score=70,  
                flags=[f"Audit Skipped ({reason})"],
                is_biased=False
            )

    def process_jobs(self, raw_jobs: List[Dict], user_resume: str = "") -> List[Dict]:
        """
        Cleans, extracts details, and audits bias for jobs.
        """
        processed = []
        
        extraction_prompt = """
        Extract the following from this job text. Return ONLY JSON format:
        {
            "company": "Company Name",
            "location": "Location",
            "work_style": "Remote/Hybrid/Onsite",
            "salary": "Salary or None",
            "summary": "1 sentence summary"
        }
        
        Job Text:
        """
        
        for job in raw_jobs:
            text = job.get("text", "")
            if not text:
                text = f"Job at {job.get('title', 'this company')}. See job link for details."
                
            # 1. Extraction (Regex fallback for speed, LLM for complex)
            # We will use simple regex/rules first to save tokens, then LLM for details if needed
            # For this agent, let's use the LLM for high quality extraction since we're "Agentic"
            
            try:
                # Fast extraction for company/location using simple logic from before
                # (Reusing the robust regex logic or simple LLM call)
                # Let's do a lightweight LLM call or just reuse the provided text if structured
                pass 
                # Actually, let's do the Audit FIRST, then basic cleanup
            except:
                pass

            # Perform Ethical Audit
            audit = self.audit_job(text)
            
            # Extract basic fields (simulating extraction for speed)
            # In a real heavy agent, we'd use function calling.
            # Here we wrap the existing logic logic or simplify
            
            processed.append({
                "title": job.get("title", "Job Opening"),
                "url": job.get("url"),
                "company": self._extract_company(text) or "Unknown Company",
                "location": "See details", # Simplified for now
                "work_style": "Flexible",
                "salary": self._extract_salary(text),
                "description": text[:500] + "...",
                "audit_score": audit.score,
                "audit_flags": audit.flags,
                "is_biased": audit.is_biased
            })
            
        return processed

    def _extract_company(self, text):
        # Quick regex fallback
        import re
        match = re.search(r"(?:at|company|employer):\s*([A-Z][a-zA-Z\s&]{2,30})", text)
        return match.group(1) if match else None

    def _extract_salary(self, text):
        import re
        match = re.search(r"\$(\d{1,3}(?:,\d{3})*(?:k|K)?)", text)
        return match.group(0) if match else None
