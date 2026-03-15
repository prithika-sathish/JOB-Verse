from typing import List, Dict, Any
import os
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()

class CareerPlannerAgent:
    """
    Predicts career trajectories and recommends bridge roles
    """
    
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found")
        
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.4,
            api_key=api_key
        )
    
    def predict_career_path(self, current_role: str, target_role: str, skills: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Predict career trajectory from current to target role
        """
        
        skills_summary = self._format_skills(skills)
        
        system_prompt = """You are a career counselor specializing in career transitions.
        Analyze the career path from current role to target role and provide a REALISTIC assessment.
        
        CRITICAL: You MUST provide a feasibility score on the FIRST line in this EXACT format:
        FEASIBILITY: X/10
        
        Where X is a number from 1-10 based on:
        - 1-3: Very difficult (major skill gaps, different field)
        - 4-6: Moderate challenge (some transferable skills, achievable with effort)
        - 7-9: Feasible (good skill match, logical progression)
        - 10: Easy (direct progression, skills already aligned)
        
        Then provide:
        1. Estimated timeline (in months)
        2. Key milestones needed
        3. Potential challenges
        
        BE HONEST - don't inflate scores. Consider the actual difficulty of the transition."""
        
        user_prompt = f"""Current Role: {current_role}
Target Role: {target_role}

Current Skills:
{skills_summary}

Analyze this career transition realistically. What's the feasibility score?"""
        
        try:
            response = self.llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ])
            
            return self._parse_career_path(response.content, current_role, target_role, skills)
            
        except Exception as e:
            print(f"Error predicting career path: {str(e)}")
            # Fallback with skill-based estimation
            return self._calculate_fallback_path(current_role, target_role, skills)
    
    def _calculate_fallback_path(self, current_role: str, target_role: str, skills: Dict[str, List[str]]) -> Dict[str, Any]:
        """Calculate a reasonable fallback path based on skills"""
        # Estimate feasibility based on skills provided
        total_skills = sum(len(skill_list) for skill_list in skills.values())
        
        if total_skills == 0:
            feasibility = 3  # Low if no skills provided
        elif total_skills < 3:
            feasibility = 4  # Moderate-low
        elif total_skills < 6:
            feasibility = 6  # Moderate
        else:
            feasibility = 7  # Good base
        
        return {
            "current_role": current_role,
            "target_role": target_role,
            "feasibility_score": feasibility,
            "timeline_months": 12,
            "milestones": ["Gain required skills", "Build portfolio", "Network in target industry", "Apply strategically"],
            "challenges": ["Skill acquisition", "Market competition", "Experience requirements"],
            "pathway_description": "Standard career transition path"
        }
    
    def _format_skills(self, skills: Dict[str, List[str]]) -> str:
        """Format skills dictionary to string"""
        result = []
        for category, skill_list in skills.items():
            if skill_list:
                result.append(f"{category.title()}: {', '.join(skill_list[:5])}")
        return "\n".join(result) if result else "No skills provided"
    
    def _parse_career_path(self, text: str, current: str, target: str, skills: Dict[str, List[str]]) -> Dict[str, Any]:
        """Parse career path analysis from response"""
        
        # Extract feasibility score - try multiple patterns
        feasibility = None
        import re
        
        # Pattern 1: FEASIBILITY: X/10 (our requested format)
        feas_match = re.search(r'FEASIBILITY:\s*(\d+)/10', text, re.IGNORECASE)
        if feas_match:
            feasibility = int(feas_match.group(1))
        else:
            # Pattern 2: X/10 or X out of 10
            scores = re.findall(r'(\d+)\s*(?:/|out of)\s*10', text, re.IGNORECASE)
            if scores:
                feasibility = int(scores[0])
            else:
                # Pattern 3: Look for "feasibility" followed by a number
                feas_match = re.search(r'feasibility[:\s]+(\d+)', text, re.IGNORECASE)
                if feas_match:
                    feasibility = int(feas_match.group(1))
        
        # If still no score found, calculate based on skills
        if feasibility is None:
            total_skills = sum(len(skill_list) for skill_list in skills.values())
            if total_skills == 0:
                feasibility = 3
            elif total_skills < 3:
                feasibility = 4
            elif total_skills < 6:
                feasibility = 6
            else:
                feasibility = 7
        
        # Extract timeline
        timeline = 12
        if "month" in text.lower():
            months = re.findall(r'(\d+)\s*(?:to\s*)?(\d+)?\s*months?', text, re.IGNORECASE)
            if months:
                timeline = int(months[0][1] if months[0][1] else months[0][0])
        
        # Extract milestones
        milestones = []
        lines = text.split('\n')
        in_milestones = False
        for line in lines:
            if 'milestone' in line.lower():
                in_milestones = True
            elif in_milestones and (line.strip().startswith('-') or line.strip().startswith('•') or line.strip().startswith(str(len(milestones) + 1))):
                milestone = line.strip().lstrip('-•0123456789.').strip()
                if milestone and len(milestone) > 10:
                    milestones.append(milestone)
        
        if not milestones:
            milestones = ["Build foundational skills", "Gain relevant experience", "Expand network", "Apply to target roles"]
        
        return {
            "current_role": current,
            "target_role": target,
            "feasibility_score": min(10, max(1, feasibility)),
            "timeline_months": timeline,
            "milestones": milestones[:6],
            "pathway_description": text,
            "challenges": self._extract_challenges(text)
        }
    
    def _extract_challenges(self, text: str) -> List[str]:
        """Extract challenges from text"""
        challenges = []
        lines = text.split('\n')
        in_challenges = False
        
        for line in lines:
            if 'challenge' in line.lower() or 'obstacle' in line.lower():
                in_challenges = True
            elif in_challenges and (line.strip().startswith('-') or line.strip().startswith('•')):
                challenge = line.strip().lstrip('-•').strip()
                if challenge:
                    challenges.append(challenge)
        
        return challenges[:5] if challenges else ["Skill acquisition", "Market competition"]
    
    def recommend_bridge_roles(self, current_role: str, target_role: str, skills: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """
        Recommend intermediate roles that bridge current to target
        """
        
        skills_summary = self._format_skills(skills)
        
        system_prompt = """You are a career strategist. Recommend 3-5 intermediate "bridge" roles
        that would help someone transition from their current role to their target role.
        
        For each role, provide:
        - Role title
        - Why it's a good bridge (1 sentence)
        - Key skills it builds
        - Typical timeline in this role (months)
        
        Format as:
        ROLE: [title]
        WHY: [reason]
        SKILLS: [skill1, skill2, skill3]
        TIMELINE: [months]
        ---"""
        
        user_prompt = f"""Current Role: {current_role}
Target Role: {target_role}

Current Skills:
{skills_summary}

Recommend bridge roles for this transition."""
        
        try:
            response = self.llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ])
            
            return self._parse_bridge_roles(response.content)
            
        except Exception as e:
            print(f"Error recommending bridge roles: {str(e)}")
            return [
                {
                    "role_title": f"Senior {current_role}",
                    "rationale": "Deepens expertise before transition",
                    "skills_built": ["Advanced technical skills", "Leadership"],
                    "timeline_months": 12
                }
            ]
    
    def _parse_bridge_roles(self, text: str) -> List[Dict[str, Any]]:
        """Parse bridge roles from response"""
        roles = []
        current_role = {}
        
        for line in text.split('\n'):
            line = line.strip()
            
            if line.startswith('ROLE:'):
                if current_role:
                    roles.append(current_role)
                current_role = {"role_title": line.replace('ROLE:', '').strip()}
            elif line.startswith('WHY:'):
                current_role["rationale"] = line.replace('WHY:', '').strip()
            elif line.startswith('SKILLS:'):
                skills_text = line.replace('SKILLS:', '').strip()
                current_role["skills_built"] = [s.strip() for s in skills_text.split(',')]
            elif line.startswith('TIMELINE:'):
                try:
                    import re
                    months = re.findall(r'\d+', line)
                    current_role["timeline_months"] = int(months[0]) if months else 12
                except:
                    current_role["timeline_months"] = 12
            elif line == '---' and current_role:
                roles.append(current_role)
                current_role = {}
        
        if current_role and "role_title" in current_role:
            roles.append(current_role)
        
        return roles[:5]
    
    def generate_networking_strategy(self, target_role: str, target_industry: str = "") -> Dict[str, List[str]]:
        """
        Generate networking recommendations
        """
        
        industry_context = f"in the {target_industry} industry" if target_industry else ""
        
        system_prompt = f"""You are a career networking expert. Provide specific, actionable networking advice
        for someone targeting a {target_role} role {industry_context}.
        
        Provide:
        1. Target Contacts (specific role titles to network with)
        2. Events/Communities (real organizations, conferences, or online communities)
        3. Outreach Template (brief, professional message template)
        
        Be specific and realistic."""
        
        try:
            response = self.llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Generate networking strategy for: {target_role}")
            ])
            
            return self._parse_networking_strategy(response.content)
            
        except Exception as e:
            print(f"Error generating networking strategy: {str(e)}")
            return {
                "target_contacts": ["Hiring Managers", "Team Leads", "Recruiters"],
                "events_communities": ["LinkedIn Groups", "Industry Conferences"],
                "outreach_template": "Professional networking message template"
            }
    
    def _parse_networking_strategy(self, text: str) -> Dict[str, List[str]]:
        """Parse networking recommendations"""
        strategy = {
            "target_contacts": [],
            "events_communities": [],
            "outreach_template": ""
        }
        
        lines = text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            if 'target contact' in line.lower() or 'who to contact' in line.lower():
                current_section = 'target_contacts'
            elif 'event' in line.lower() or 'communit' in line.lower():
                current_section = 'events_communities'
            elif 'template' in line.lower() or 'message' in line.lower():
                current_section = 'outreach_template'
                strategy["outreach_template"] = ""
            elif current_section and (line.startswith('-') or line.startswith('•')):
                item = line.lstrip('-•').strip()
                if current_section in ['target_contacts', 'events_communities']:
                    strategy[current_section].append(item)
            elif current_section == 'outreach_template' and line:
                strategy["outreach_template"] += line + "\n"
        
        return strategy

    def generate_skill_roadmap(self, current_role: str, target_role: str, current_skills_text: str, feasibility_score: int) -> Dict[str, Any]:
        """
        Generate a detailed learning roadmap when skills don't match the target position
        """
        
        system_prompt = """You are a career development expert. Create a structured learning roadmap.

You MUST follow this EXACT format:

SKILL GAPS:
- [Skill 1]
- [Skill 2]
- [Skill 3]

PHASE 1: [Phase Name]
DURATION: [X months]
FOCUS: [What to learn]
RESOURCES:
- [Resource 1]
- [Resource 2]
PROJECTS:
- [Project 1]
- [Project 2]

PHASE 2: [Phase Name]
DURATION: [X months]
FOCUS: [What to learn]
RESOURCES:
- [Resource 1]
PROJECTS:
- [Project 1]

TOTAL DURATION: [X-Y months]

Be specific with actual course names, platforms (Coursera, Udemy, YouTube channels), and project ideas."""
        
        user_prompt = f"""Current Role: {current_role}
Target Role: {target_role}
Current Skills: {current_skills_text if current_skills_text else "Limited skills provided"}
Feasibility: {feasibility_score}/10

Create a roadmap to transition to the target role."""
        
        try:
            response = self.llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ])
            
            return self._parse_roadmap(response.content)
            
        except Exception as e:
            print(f"Error generating roadmap: {str(e)}")
            return self._get_default_roadmap()
    
    def _get_default_roadmap(self) -> Dict[str, Any]:
        """Return a default roadmap when AI fails"""
        return {
            "skill_gaps": [
                "Core technical skills for target role",
                "Domain-specific knowledge",
                "Industry best practices",
                "Relevant tools and technologies"
            ],
            "learning_phases": [
                {
                    "phase_name": "Phase 1: Foundation Building",
                    "duration": "3 months",
                    "focus": "Master fundamental technical skills",
                    "resources": [
                        "Coursera or Udemy beginner courses",
                        "Official documentation",
                        "YouTube tutorials"
                    ],
                    "projects": [
                        "Build 2-3 small practice projects",
                        "Contribute to open source"
                    ]
                },
                {
                    "phase_name": "Phase 2: Intermediate Skills",
                    "duration": "3 months",
                    "focus": "Apply skills in real-world scenarios",
                    "resources": [
                        "Advanced online courses",
                        "Industry certifications",
                        "Professional communities"
                    ],
                    "projects": [
                        "Create portfolio projects",
                        "Build end-to-end applications"
                    ]
                }
            ],
            "total_duration": "6-9 months"
        }
    
    def _parse_roadmap(self, text: str) -> Dict[str, Any]:
        """Parse learning roadmap from AI response with improved structure parsing"""
        roadmap = {
            "skill_gaps": [],
            "learning_phases": [],
            "total_duration": "6-9 months"
        }
        
        lines = text.split('\n')
        current_section = None
        current_phase = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect main sections
            if 'SKILL GAP' in line.upper():
                current_section = 'skill_gaps'
                current_phase = None
            elif 'TOTAL DURATION' in line.upper():
                # Extract total duration
                import re
                duration_match = re.search(r'(\d+[-\s]*\d*)\s*months?', line, re.IGNORECASE)
                if duration_match:
                    roadmap['total_duration'] = duration_match.group(0)
                current_section = None
            elif line.upper().startswith('PHASE'):
                # Save previous phase
                if current_phase:
                    roadmap['learning_phases'].append(current_phase)
                
                # Start new phase
                phase_name = line.split(':', 1)[1].strip() if ':' in line else line
                current_phase = {
                    "phase_name": phase_name,
                    "duration": "3 months",
                    "focus": "",
                    "resources": [],
                    "projects": []
                }
                current_section = 'phase'
            elif current_phase and 'DURATION:' in line.upper():
                current_phase['duration'] = line.split(':', 1)[1].strip()
            elif current_phase and 'FOCUS:' in line.upper():
                current_phase['focus'] = line.split(':', 1)[1].strip()
            elif current_phase and 'RESOURCE' in line.upper():
                current_section = 'resources'
            elif current_phase and 'PROJECT' in line.upper():
                current_section = 'projects'
            
            # Parse list items
            elif line.startswith('-') or line.startswith('•'):
                item = line.lstrip('-•').strip()
                if not item:
                    continue
                
                if current_section == 'skill_gaps':
                    roadmap['skill_gaps'].append(item)
                elif current_section == 'resources' and current_phase:
                    current_phase['resources'].append(item)
                elif current_section == 'projects' and current_phase:
                    current_phase['projects'].append(item)
        
        # Add last phase
        if current_phase:
            roadmap['learning_phases'].append(current_phase)
        
        # Return default if parsing completely failed
        if not roadmap['skill_gaps'] and not roadmap['learning_phases']:
            return self._get_default_roadmap()
        
        # Ensure we have at least some data
        if not roadmap['skill_gaps']:
            roadmap['skill_gaps'] = ["Core technical skills", "Domain knowledge", "Best practices"]
        
        if not roadmap['learning_phases']:
            roadmap['learning_phases'] = [{
                "phase_name": "Learning Phase",
                "duration": "3-6 months",
                "focus": "Build required skills for target role",
                "resources": ["Online courses", "Documentation", "Practice"],
                "projects": ["Build portfolio projects"]
            }]
        
        return roadmap
