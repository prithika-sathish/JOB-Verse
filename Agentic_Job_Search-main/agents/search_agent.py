from typing import List, Dict, Any, Optional
import os
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

try:
    from exa_py import Exa
except Exception:
    Exa = None

class JobSearchConfig(BaseModel):
    job_title: str
    location: Optional[str] = None
    work_style: Optional[str] = "Any"
    num_jobs: int = 5

class SearchAgent:
    def __init__(self):
        self.api_key = os.getenv("EXA_API_KEY")
        self.client = None

        if Exa is None:
            print("Search Agent: exa_py not installed. Exa search is disabled.")
            return

        if not self.api_key:
            print("Search Agent: EXA_API_KEY not set. Exa search is disabled.")
            return

        try:
            self.client = Exa(api_key=self.api_key)
        except Exception as error:
            print(f"Search Agent failed to initialize Exa client: {error}")
            self.client = None

    def _is_job_posting(self, url: str, title: str, text: str) -> bool:
        """
        Validate if this is an INDIVIDUAL job posting, not a blog/news/advice article or aggregated list
        """
        # URL patterns that indicate job postings
        job_url_patterns = [
            '/job/', '/jobs/', '/career', '/apply', '/position',
            '/opening', '/vacancy', '/hiring', '/recruit'
        ]
        
        # URL patterns to EXCLUDE (blogs, news, advice, aggregated lists)
        exclude_patterns = [
            '/blog/', '/news/', '/article/', '/post/', '/story/',
            '/updates/', '/press/', '/media/', '/tips/', '/guide/', '/advice/',
            '/search/', '/browse/', '/directory/', '/list/'  # aggregated pages
        ]
        
        url_lower = url.lower()
        
        # Exclude non-job content
        if any(pattern in url_lower for pattern in exclude_patterns):
            return False
        
        title_lower = title.lower() if title else ""
        
        # EXCLUDE aggregated/summary titles (e.g., "63 Jobs in Pakistan")
        # Check for count-based titles FIRST (highest priority block)
        import re
        
        # Pattern 1: Numbers followed by job keywords (e.g., "63 Software Engineering Jobs")
        if re.search(r'\d+\s+.*?\bjobs?\b', title_lower):
            return False
        
        # Pattern 2: Phrases indicating aggregated listings
        aggregated_phrases = [
            'jobs in', 'job openings in', 'positions in', 'vacancies in',
            'jobs available', 'job listings', 'careers in',
            'remote jobs', 'job search', 'find jobs', 'jobs at',
            'hiring for', 'open positions', 'employment opportunities',
            'fully remote', 'best companies'
        ]
        
        if any(phrase in title_lower for phrase in aggregated_phrases):
            return False
        
        # Content indicators of a SINGLE, INDIVIDUAL job posting
        job_content_indicators = [
            'apply now', 'submit application', 'job description',
            'requirements:', 'responsibilities:', 'qualifications:',
            'salary', 'compensation', 'benefits', 'experience required',
            'apply for this job', 'send resume', 'submit cv',
            'job summary', 'about the role', 'what you will do'
        ]
        
        text_lower = text.lower() if text else ""
        
        # Must have at least 2 job content indicators for individual postings
        indicator_count = sum(1 for indicator in job_content_indicators if indicator in text_lower or indicator in title_lower)
        
        # Check if URL suggests it's a job posting OR has strong content indicators
        has_job_url = any(pattern in url_lower for pattern in job_url_patterns)
        has_strong_content = indicator_count >= 2
        
        return has_job_url or has_strong_content


    def _build_query(self, config: JobSearchConfig) -> str:
        """
        Build an intelligent query targeting actual job postings
        """
        # Core job title with variations
        job_title = config.job_title
        
        # Build query emphasizing we want job applications
        query_parts = [
            job_title,
            "job posting",
            "apply"
        ]
        
        # Add location if specified
        if config.location and config.location.lower() not in ["any", "remote"]:
            query_parts.append(f"in {config.location}")
        
        # Add work style if specified
        if config.work_style and config.work_style != "Any":
            query_parts.append(config.work_style)
        
        return " ".join(query_parts)

    def search(self, config: JobSearchConfig) -> Dict[str, Any]:
        """
        Smart job search that returns ONLY actual job postings
        """
        if not self.client:
            return {
                "raw_results": [],
                "status": "disabled",
                "count": 0,
                "message": "Exa search is disabled (missing exa_py package or EXA_API_KEY)."
            }

        query = self._build_query(config)
        sixty_days_ago = (datetime.now() - timedelta(days=60)).isoformat()  # Wider window
        
        all_results = []
        seen_urls = set()
        
        # Request significantly more to account for filtering
        search_limit = config.num_jobs * 3
        
        try:
            res = self.client.search_and_contents(
                query=query,
                num_results=search_limit,
                text=True,
                start_published_date=sixty_days_ago
            )
            
            for r in res.results:
                if r.url not in seen_urls:
                    # Validate this is actually a job posting
                    if self._is_job_posting(r.url, r.title, r.text):
                        seen_urls.add(r.url)
                        all_results.append({
                            "title": r.title,
                            "url": r.url,
                            "text": r.text if r.text else "Job opportunity. Visit link for details.",
                            "published_date": r.published_date
                        })
                        
                        # Stop once we have enough valid jobs
                        if len(all_results) >= config.num_jobs * 2:
                            break
                            
        except Exception as e:
            print(f"Search error: {e}")
            import traceback
            traceback.print_exc()
        
        return {
            "raw_results": all_results,
            "status": "success" if all_results else "no_results",
            "count": len(all_results)
        }

