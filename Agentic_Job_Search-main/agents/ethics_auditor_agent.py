from typing import List, Dict, Any
import os
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
import re

load_dotenv()

class EthicsAuditorAgent:
    """
    Comprehensive ethical AI auditing for resumes, job descriptions, and system outputs
    """
    
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found")
        self.audit_enabled = False
        
        try:
            self.llm = ChatGroq(
                model="llama-3.3-70b-versatile",
                temperature=0.2,
                api_key=api_key
            )
            # Test if model is accessible
            test_response = self.llm.invoke([HumanMessage(content="Test")])
            if test_response:
                self.audit_enabled = True
                print("✓ Ethics Auditor initialized successfully")
        except Exception as e:
            print(f"⚠ Gemini API unavailable for ethics auditing: {str(e)[:100]}")
            print("  Using heuristic-based auditing instead.")
            self.llm = None
    
    def audit_resume(self, resume_text: str) -> Dict[str, Any]:
        """
        Audit resume for potential biases and suggest improvements
        """
        
        biases_found = []
        suggestions = []
        score = 70  # Start with moderate base score (changed from 85)
        
        text_lower = resume_text.lower().strip()
        
        # Content quality validation
        if len(resume_text.strip()) < 50:
            biases_found.append("Insufficient Content")
            suggestions.append("Resume too short - provide more details about your experience and skills")
            score = 30
        
        # Check for resume-related keywords
        resume_keywords = ['experience', 'skills', 'education', 'work', 'project', 
                          'responsibilities', 'achievements', 'degree', 'certificate',
                          'position', 'role', 'company', 'team']
        
        keyword_count = sum(1 for keyword in resume_keywords if keyword in text_lower)
        
        if keyword_count == 0 and len(resume_text.strip()) > 10:
            biases_found.append("Invalid Content")
            suggestions.append("Content doesn't appear to be a resume - should include work experience, skills, education")
            score = 20
        elif keyword_count < 3 and len(resume_text.strip()) > 50:
            biases_found.append("Low Quality Resume")
            suggestions.append("Resume lacks detail - include clear sections for experience, skills, and education")
            score -= 15
        
        # Reward good content structure
        if keyword_count >= 6:
            score += 15
        
        # Age indicators
        age_patterns = [
            (r'\b(19|20)\d{2}\b', "Graduation year visible - consider removing to avoid age discrimination"),
            (r'\b\d{2}\+?\s*years?\s+(?:of\s+)?experience\b', "Extensive years mentioned - consider 'significant experience' instead"),
            (r'\bsenior\s+professional\b', "May indicate age - consider role-specific titles")
        ]
        
        for pattern, suggestion in age_patterns:
            if re.search(pattern, resume_text, re.IGNORECASE):
                biases_found.append("Age Indicator")
                suggestions.append(suggestion)
                score -= 5
        
        # Gender-coded language (based on research)
        masculine_coded = ['aggressive', 'competitive', 'dominant', 'decisive', 'assertive', 'ambitious']
        feminine_coded = ['supportive', 'collaborative', 'nurturing', 'understanding', 'loyal']
        
        masc_count = sum(1 for word in masculine_coded if word in text_lower)
        fem_count = sum(1 for word in feminine_coded if word in text_lower)
        
        if masc_count > 3:
            biases_found.append("Gender-Coded Language (Masculine)")
            suggestions.append("Consider balancing masculine-coded words with neutral alternatives")
            score -= 5
        
        if fem_count > 3:
            biases_found.append("Gender-Coded Language (Feminine)")
            suggestions.append("Consider balancing feminine-coded words with neutral alternatives")
            score -= 5
        
        # Socioeconomic signals
        if re.search(r'\b(ivy\s+league|top\s+tier|elite)\b', resume_text, re.IGNORECASE):
            biases_found.append("Elite Institution Emphasis")
            suggestions.append("While noting education is fine, excessive emphasis on 'elite' status may trigger bias")
            score -= 3
        
        # Positive signals
        inclusive_terms = ['diverse', 'inclusive', 'accessible', 'equitable', 'collaborative']
        inclusive_count = sum(1 for term in inclusive_terms if term in text_lower)
        
        if inclusive_count > 0:
            score += inclusive_count * 2
        
        return {
            "score": max(0, min(100, score)),
            "biases_found": list(set(biases_found)),
            "suggestions": suggestions,
            "inclusive_signals": inclusive_count,
            "is_biased": score < 70
        }
    
    def audit_job_description(self, job_desc: str) -> Dict[str, Any]:
        """
        Audit job description for discriminatory language and unrealistic requirements
        """
        
        issues = []
        flags = []
        score = 70  # Start with moderate base score (changed from 90)
        
        text_lower = job_desc.lower().strip()
        
        # Content quality validation
        if len(job_desc.strip()) < 50:
            issues.append("Insufficient Content")
            flags.append("Job description too short - should provide detailed role information")
            score = 30
        
        # Check for meaningful job-related keywords
        job_keywords = ['role', 'position', 'responsibilities', 'requirements', 'qualifications', 
                       'experience', 'skills', 'duties', 'job', 'candidate', 'team', 'company',
                       'salary', 'benefits', 'work', 'hiring']
        
        keyword_count = sum(1 for keyword in job_keywords if keyword in text_lower)
        
        if keyword_count == 0 and len(job_desc.strip()) > 10:
            issues.append("Invalid Content")
            flags.append("Content doesn't appear to be a job description - no job-related keywords found")
            score = 20
        elif keyword_count < 3 and len(job_desc.strip()) > 50:
            issues.append("Low Quality Content")
            flags.append("Job description lacks detail - should include responsibilities, requirements, etc.")
            score -= 20
        
        # Reward good content structure
        if keyword_count >= 5:
            score += 15
        
        # Gender-biased pronouns
        if re.search(r'\b(he|him|his)\b', job_desc, re.IGNORECASE):
            issues.append("Gendered Pronouns")
            flags.append("Uses 'he/him' - use gender-neutral 'they/them' instead")
            score -= 10
        
        # Age discrimination
        age_terms = [
            ('digital native', 'May exclude older workers'),
            ('recent graduate', 'Excludes experienced professionals'),
            ('young and energetic', 'Direct age discrimination'),
            ('new grad', 'Age-restrictive')
        ]
        
        for term, reason in age_terms:
            if term in text_lower:
                issues.append("Age Discrimination")
                flags.append(f"'{term.title()}' - {reason}")
                score -= 10
        
        # Gendered language
        gendered_terms = [
            ('rockstar', 'guru', 'ninja', 'wizard'),  # Masculine-coded
            ('aggressive', 'dominant', 'competitive'),
        ]
        
        for term_group in gendered_terms:
            for term in term_group:
                if term in text_lower:
                    issues.append("Gender-Coded Language")
                    flags.append(f"'{term.title()}' is masculine-coded - use neutral alternatives")
                    score -= 5
        
        # Credential inflation
        if re.search(r'\brequire[sd]?\s+.*\b(phd|master\'?s|mba)\b', text_lower):
            if 'or equivalent' not in text_lower and 'preferred' not in text_lower:
                issues.append("Credential Inflation")
                flags.append("Strict degree requirement may exclude qualified candidates")
                score -= 8
        
        # Unrealistic requirements
        if re.search(r'\b(\d{1,2})\+?\s*years?\s+.*\brequired\b', job_desc):
            issues.append("Experience Barrier")
            flags.append("Consider if all years are truly required or if skills matter more")
            score -= 5
        
        # Positive signals
        inclusive_phrases = [
            'equal opportunity employer',
            'diverse',
            'inclusive',
            'all qualified applicants',
            'disability',
            'veteran',
            'accommodation'
        ]
        
        inclusive_count = sum(1 for phrase in inclusive_phrases if phrase in text_lower)
        if inclusive_count > 0:
            score += inclusive_count * 3
        
        return {
            "score": max(0, min(100, score)),
            "issues": list(set(issues)),
            "flags": flags,
            "inclusive_signals": inclusive_count,
            "is_discriminatory": score < 65
        }
    
    def explain_decision(self, feature_type: str, value: Any, context: str = "") -> str:
        """
        Explain why a particular recommendation or decision was made
        """
        
        explanations = {
            "course_recommendation": f"This course was recommended because it directly addresses the skill gap '{value}' identified in the analysis. The recommendation algorithm prioritized it based on relevance to your target role and current skill level.",
            
            "interview_question": f"This question was generated to assess competencies mentioned in the job description, specifically targeting '{value}'. The difficulty level was calibrated to your target role's seniority.",
            
            "bridge_role": f"This role ('{value}') was suggested as it builds critical skills needed for your target position while matching your current experience level. It represents a strategic intermediate step.",
            
            "skill_gap": f"'{value}' was identified as a gap because it appears in the job requirements but wasn't found in your resume. The severity rating considers how central this skill is to the role."
        }
        
        return explanations.get(feature_type, f"Recommended based on analysis of: {value}")
    
    def generate_transparency_report(self, session_data: Dict[str, Any]) -> str:
        """
        Generate a comprehensive transparency report explaining all system decisions
        """
        
        report = "# AI System Transparency Report\n\n"
        report += "_Generated to explain how AI recommendations and decisions are made in your job search journey._\n\n"
        
        report += "## 📊 Data Used\n\n"
        data_items = []
        
        if 'resume_analyzed' in session_data:
            data_items.append("✅ Resume/profile data (skills, experience)")
        if 'job_description' in session_data:
            data_items.append("✅ Target job description")
        if 'interview_answers' in session_data:
            data_items.append("✅ Interview practice responses")
        if 'search_results' in session_data:
            data_items.append("✅ Job search results and preferences")
        
        if data_items:
            for item in data_items:
                report += f"- {item}\n"
        else:
            report += "_No data processed yet. Complete a job search or skill analysis to see what data is used._\n"
        
        report += "\n## 🤖 Decisions Made\n\n"
        
        if 'skill_gaps' in session_data and session_data['skill_gaps']:
            report += f"### Skill Gap Analysis\n"
            report += f"Identified **{len(session_data['skill_gaps'])} skill gaps** using:\n\n"
            report += "- NLP-based skill extraction from resume and job description\n"
            report += "- Fuzzy matching algorithm for skill comparison (tolerates spelling variations)\n"
            report += "- Severity scoring based on skill category:\n"
            report += "  - **Critical**: Core technical requirements\n"
            report += "  - **Moderate**: Beneficial skills\n"
            report += "  - **Minor**: Nice-to-have competencies\n\n"
        
        if 'recommendations' in session_data and session_data['recommendations']:
            report += f"### Learning Recommendations\n"
            report += f"Provided **{len(session_data['recommendations'])} course recommendations** based on:\n\n"
            report += "- Skill gap prioritization (critical → moderate → minor)\n"
            report += "- Course relevance scoring (matched to specific skills)\n"
            report += "- Learning path optimization for 12-month timeline\n"
            report += "- Diverse platform selection (Coursera, Udemy, edX, YouTube)\n\n"
        
        if 'job_matches' in session_data:
            report += f"### Job Matching\n"
            report += "Jobs filtered and ranked using:\n\n"
            report += "- **Keyword matching**: Title and description alignment with search query\n"
            report += "- **Location filtering**: Based on your preferences (remote/onsite)\n"
            report += "- **Bias detection**: Removed discriminatory job postings\n"
            report += "- **Relevance scoring**: Prioritized best matches first\n\n"
        
        if not ('skill_gaps' in session_data or 'recommendations' in session_data or 'job_matches' in session_data):
            report += "_No decisions made yet. Use the app features to see how AI makes recommendations._\n\n"
        
        report += "## ⚖️ Bias Mitigation\n\n"
        report += "Our system actively prevents discrimination:\n\n"
        report += "- **Gender-neutral language**: All AI-generated content uses they/them pronouns\n"
        report += "- **Age-agnostic recommendations**: No assumptions based on graduation year or experience length\n"
        report += "- **Skill-based matching**: Focus on competencies, not credentials (no degree requirements)\n"
        report += "- **Diverse platforms**: Recommendations include free and paid options\n"
        report += "- **Bias audit**: Job descriptions scanned for discriminatory language\n"
        report += "- **Fair scoring**: Resume audits identify and flag potential biases\n\n"
        
        report += "## 🔒 User Control\n\n"
        report += "**You have complete control:**\n\n"
        report += "- ✅ View and edit all input data (resume, preferences)\n"
        report += "- ✅ Request explanations for any recommendation (see below)\n"
        report += "- ✅ Adjust recommendation weights and priorities\n"
        report += "- ✅ Export your data anytime (download reports)\n"
        report += "- ✅ Delete your session data (Clear All button at bottom)\n\n"
        
        report += "## 🛡️ Privacy Commitment\n\n"
        report += "- **Local storage only**: Your data stays in your browser session\n"
        report += "- **No tracking**: We don't log search queries or personal info\n"
        report += "- **API calls**: Only job search uses external APIs (ExaAI, Groq)\n"
        report += "- **No sharing**: Your resume and data never leave your device\n\n"
        
        report += "---\n\n"
        report += "_This report was auto-generated. Use the 'Ask About Any Decision' section below to get specific explanations._\n"
        
        return report
