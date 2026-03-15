from typing import List, Dict, Any
import os
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
import re

load_dotenv()

class SkillAnalyzerAgent:
    """
    Analyzes resumes and job descriptions to identify skill gaps
    and recommend learning paths
    """
    
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found")
        
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            api_key=api_key
        )
    
    def extract_skills_from_text(self, text: str, source_type: str = "resume") -> Dict[str, List[str]]:
        """
        Extract skills from resume or job description
        
        Args:
            text: Resume text or job description
            source_type: "resume" or "job_description"
        """
        
        system_prompt = f"""You are an expert at extracting skills from {source_type}s.
        Extract and categorize skills into:
        - Technical Skills (programming languages, tools, frameworks)
        - Soft Skills (communication, leadership, etc.)
        - Domain Knowledge (industry-specific knowledge)
        
        Return in this exact format:
        TECHNICAL:
        - skill1
        - skill2
        
        SOFT:
        - skill1
        - skill2
        
        DOMAIN:
        - skill1
        - skill2"""
        
        try:
            response = self.llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=text[:3000])  # Limit to avoid token limits
            ])
            
            return self._parse_skills(response.content)
            
        except Exception as e:
            print(f"Error extracting skills: {str(e)}")
            return {"technical": [], "soft": [], "domain": []}
    
    def _parse_skills(self, text: str) -> Dict[str, List[str]]:
        """Parse skills from formatted response"""
        skills = {"technical": [], "soft": [], "domain": []}
        
        current_category = None
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if 'TECHNICAL:' in line.upper():
                current_category = 'technical'
            elif 'SOFT:' in line.upper():
                current_category = 'soft'
            elif 'DOMAIN:' in line.upper():
                current_category = 'domain'
            elif line.startswith('-') and current_category:
                skill = line.lstrip('-').strip()
                if skill and len(skill) > 2:
                    skills[current_category].append(skill)
        
        return skills
    
    def analyze_skill_gaps(self, resume_skills: Dict[str, List[str]], job_skills: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Compare resume skills with job requirements and identify gaps
        """
        
        gaps = {
            "critical": [],
            "moderate": [],
            "minor": []
        }
        
        matched = {
            "technical": [],
            "soft": [],
            "domain": []
        }
        
        # Check each category
        for category in ["technical", "soft", "domain"]:
            resume_set = set(s.lower() for s in resume_skills.get(category, []))
            job_set = set(s.lower() for s in job_skills.get(category, []))
            
            # Find matches (case-insensitive partial matching)
            for job_skill in job_skills.get(category, []):
                job_skill_lower = job_skill.lower()
                is_matched = False
                
                for resume_skill in resume_skills.get(category, []):
                    resume_skill_lower = resume_skill.lower()
                    # Check if either is substring of the other or if they share significant words
                    if (job_skill_lower in resume_skill_lower or 
                        resume_skill_lower in job_skill_lower or
                        self._skills_similar(job_skill_lower, resume_skill_lower)):
                        matched[category].append(job_skill)
                        is_matched = True
                        break
                
                if not is_matched:
                    # Categorize by gap severity
                    if category == "technical":
                        gaps["critical"].append(job_skill)
                    elif category == "domain":
                        gaps["moderate"].append(job_skill)
                    else:
                        gaps["minor"].append(job_skill)
        
        # Calculate match percentage
        total_required = sum(len(job_skills.get(c, [])) for c in ["technical", "soft", "domain"])
        total_matched = sum(len(matched[c]) for c in matched)
        
        match_percentage = (total_matched / total_required * 100) if total_required > 0 else 0
        
        return {
            "gaps": gaps,
            "matched": matched,
            "match_percentage": round(match_percentage, 1),
            "resume_skills": resume_skills,
            "job_skills": job_skills
        }
    
    def _skills_similar(self, skill1: str, skill2: str) -> bool:
        """Check if two skills are similar based on shared keywords"""
        # Remove common words
        stop_words = {'and', 'or', 'the', 'in', 'with', 'for', 'to', 'of', 'a', 'an'}
        
        words1 = set(re.findall(r'\w+', skill1.lower())) - stop_words
        words2 = set(re.findall(r'\w+', skill2.lower())) - stop_words
        
        if not words1 or not words2:
            return False
        
        # If they share 50%+ of words, consider similar
        shared = words1 & words2
        return len(shared) / max(len(words1), len(words2)) >= 0.5
    
    def recommend_learning_resources(self, gaps: List[str]) -> List[Dict[str, Any]]:
        """
        Recommend learning resources for skill gaps
        Note: In production, this would call actual course APIs
        """
        
        if not gaps:
            return []
        
        system_prompt = """You are a career development advisor. For each skill gap provided,
        recommend specific, real courses or resources. Format as:
        
        SKILL: [skill name]
        COURSE: [course name]
        PLATFORM: [Coursera/Udemy/LinkedIn Learning/YouTube]
        DURATION: [estimated time]
        PRIORITY: [High/Medium/Low]
        ---
        
        Recommend real, popular courses that actually exist."""
        
        try:
            response = self.llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Recommend learning resources for these skills:\n" + "\n".join(f"- {gap}" for gap in gaps[:10]))
            ])
            
            return self._parse_recommendations(response.content)
            
        except Exception as e:
            print(f"Error getting recommendations: {str(e)}")
            # Return generic recommendations
            return [
                {
                    "skill": gap,
                    "course": f"Introduction to {gap}",
                    "platform": "Coursera",
                    "duration": "4-6 weeks",
                    "priority": "High" if i < 3 else "Medium"
                }
                for i, gap in enumerate(gaps[:5])
            ]
    
    def _parse_recommendations(self, text: str) -> List[Dict[str, Any]]:
        """Parse course recommendations from response"""
        recommendations = []
        
        current_rec = {}
        for line in text.split('\n'):
            line = line.strip()
            
            if line.startswith('SKILL:'):
                if current_rec:
                    recommendations.append(current_rec)
                current_rec = {"skill": line.replace('SKILL:', '').strip()}
            elif line.startswith('COURSE:'):
                current_rec["course"] = line.replace('COURSE:', '').strip()
            elif line.startswith('PLATFORM:'):
                current_rec["platform"] = line.replace('PLATFORM:', '').strip()
            elif line.startswith('DURATION:'):
                current_rec["duration"] = line.replace('DURATION:', '').strip()
            elif line.startswith('PRIORITY:'):
                current_rec["priority"] = line.replace('PRIORITY:', '').strip()
            elif line == '---' and current_rec:
                recommendations.append(current_rec)
                current_rec = {}
        
        if current_rec and "skill" in current_rec:
            recommendations.append(current_rec)
        
        return recommendations
    
    def generate_learning_roadmap(self, recommendations: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
        """
        Generate a 12-month learning roadmap
        """
        
        # Organize by priority
        high_priority = [r for r in recommendations if r.get('priority') == 'High']
        medium_priority = [r for r in recommendations if r.get('priority') == 'Medium']
        low_priority = [r for r in recommendations if r.get('priority') == 'Low']
        
        roadmap = {
            "months_1_3": high_priority[:2] if high_priority else [],
            "months_4_6": high_priority[2:] + medium_priority[:2] if len(high_priority) > 2 else medium_priority[:3],
            "months_7_9": medium_priority[2:] + low_priority[:2] if len(medium_priority) > 2 else low_priority[:3],
            "months_10_12": low_priority[2:] if len(low_priority) > 2 else []
        }
        
        return roadmap
