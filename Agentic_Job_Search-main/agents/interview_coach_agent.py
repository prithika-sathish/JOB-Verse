from typing import List, Dict, Any
import os
import random
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()

class InterviewCoachAgent:
    """
    AI Interview Coach that generates questions and provides feedback
    """
    
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found")
        
        self.api_key = api_key
    
    def generate_questions(self, job_description: str, question_type: str = "behavioral", count: int = 5) -> List[str]:
        """
        Generate interview questions based on job description
        
        Args:
            job_description: The target job posting
            question_type: Type of questions (behavioral, technical, situational)
            count: Number of questions to generate
        """
        
        # Create LLM with varied temperature for each call to ensure variety
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.9,  # Higher temperature for more variety
            api_key=self.api_key
        )
        
        system_prompt = f"""You are an expert interview coach. Generate EXACTLY {count} UNIQUE {question_type} interview questions 
        based on the following job description. Make questions realistic, diverse, and relevant to the role.
        
        For behavioral questions, focus on competencies like: leadership, problem-solving, teamwork, conflict resolution, adaptability.
        For technical questions, focus on specific skills, technologies, and problem-solving approaches mentioned in the job.
        For situational questions, create realistic scenarios the candidate might face in this specific role.
        
        IMPORTANT: Generate {count} DIFFERENT questions. Do NOT repeat questions.
        
        Return ONLY the questions, one per line, numbered 1-{count}."""
        
        try:
            print(f"Generating {count} {question_type} questions...")
            response = llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Job Description:\n{job_description[:1500]}")  # Limit to avoid token limits
            ])
            
            # Parse questions from response
            questions_text = response.content.strip()
            print(f"AI Response: {questions_text[:200]}...")  # Debug output
            
            questions = [q.strip() for q in questions_text.split('\n') if q.strip() and any(c.isdigit() for c in q[:3])]
            
            # Clean up numbering
            cleaned_questions = []
            for q in questions:
                # Remove leading numbers, dots, and parentheses
                clean_q = q.lstrip('0123456789.) ').strip()
                if clean_q and len(clean_q) > 10:  # Ensure it's a real question
                    cleaned_questions.append(clean_q)
            
            if len(cleaned_questions) >= count:
                print(f"✓ Successfully generated {len(cleaned_questions)} questions")
                return cleaned_questions[:count]
            else:
                print(f"⚠ Only got {len(cleaned_questions)} questions, using fallbacks")
                raise Exception("Not enough questions generated")
            
        except Exception as e:
            print(f"❌ Error generating questions: {str(e)}")
            # Type-specific fallback questions
            return self._get_fallback_questions(question_type, count)
    
    def _get_fallback_questions(self, question_type: str, count: int) -> List[str]:
        """Get fallback questions when API fails"""
        
        fallbacks = {
            "behavioral": [
                "Tell me about a time when you faced a significant challenge at work. How did you handle it?",
                "Describe a situation where you had to work with a difficult team member.",
                "What's your greatest professional accomplishment and why?",
                "How do you prioritize tasks when you have multiple deadlines?",
                "Tell me about a time when you failed. What did you learn?",
                "Describe a situation where you had to adapt to significant changes at work.",
                "Give me an example of when you showed leadership without having formal authority.",
                "Tell me about a time you had to make a difficult decision with limited information.",
                "Describe a conflict you had with a colleague and how you resolved it.",
                "Share an example of when you went above and beyond what was expected of you."
            ],
            "technical": [
                "Walk me through your approach to solving a complex technical problem.",
                "How would you optimize the performance of a slow application?",
                "Explain a technical concept you recently learned to someone non-technical.",
                "Describe your experience with version control and collaboration workflows.",
                "How do you ensure code quality in your projects?",
                "What's your approach to debugging when you encounter an error you've never seen before?",
                "Explain the trade-offs between different architectural patterns you've used.",
                "How do you stay updated with new technologies and best practices?",
                "Describe a time when you had to refactor legacy code.",
                "What testing strategies do you employ in your development process?"
            ],
            "situational": [
                "If you joined a team with an ongoing project in crisis, what would be your first steps?",
                "How would you handle discovering a critical bug in production just before a major release?",
                "What would you do if you disagreed with your manager's technical decision?",
                "If you had two critical tasks with the same deadline, how would you prioritize?",
                "How would you approach learning a completely new technology stack for a project?",
                "What would you do if a team member consistently missed deadlines?",
                "How would you handle receiving harsh criticism on your work?",
                "If given an impossible deadline, how would you respond?",
                "What would you do if you noticed a colleague's code had security vulnerabilities?",
                "How would you balance technical debt with new feature development?"
            ]
        }
        
        questions = fallbacks.get(question_type, fallbacks["behavioral"])
        # Shuffle to add some variety even in fallbacks
        shuffled = questions.copy()
        random.shuffle(shuffled)
        return shuffled[:count]
    
    
    def evaluate_answer(self, question: str, answer: str, job_description: str) -> Dict[str, Any]:
        """
        Evaluate an interview answer
        
        Returns:
            Dict with score, feedback, and improvement suggestions
        """
        
        # Create LLM for evaluation
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            api_key=self.api_key
        )
        
        system_prompt = """You are an expert interview coach evaluating candidate answers.
        
        Analyze the answer thoroughly and provide:
        1. A score from 1-10 (be accurate - give low scores for poor/incorrect answers)
        2. Whether the answer is correct/incorrect for factual questions
        3. Specific strengths (what they did well)
        4. Specific improvements needed
        5. For technical questions: provide the correct/complete answer if theirs was wrong
        6. STAR method adherence (for behavioral questions)
        
        Be honest and direct - if the answer is wrong, say it's wrong and explain why."""
        
        try:
            response = llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"""Question: {question}

Answer: {answer}

Job Context: {job_description[:500]}

Evaluate this answer thoroughly and return feedback in this format:

Score: [1-10]

Correctness: [Correct/Partially Correct/Incorrect - explain briefly]

Strengths:
- [strength 1]
- [strength 2]

Improvements:
- [improvement 1]  
- [improvement 2]

Better Answer: [For technical/factual questions: provide a complete, correct answer. For behavioral: provide example of what a strong answer would include]

STAR Method: [Yes/No/Partial/Not Applicable - explain]""")
            ])
            
            feedback_text = response.content
            print(f"Evaluation response: {feedback_text[:200]}...")  # Debug
            
            # Parse score
            score = 5  # default
            if "Score:" in feedback_text:
                try:
                    score_line = [line for line in feedback_text.split('\n') if 'Score:' in line][0]
                    score_str = ''.join(filter(str.isdigit, score_line))
                    if score_str:
                        score = int(score_str)
                except Exception as e:
                    print(f"Error parsing score: {e}")
            
            # Parse correctness
            is_correct = "unknown"
            if "Correctness:" in feedback_text:
                try:
                    correctness_line = [line for line in feedback_text.split('\n') if 'Correctness:' in line][0].lower()
                    if "incorrect" in correctness_line:
                        is_correct = "incorrect"
                    elif "partially" in correctness_line:
                        is_correct = "partial"
                    elif "correct" in correctness_line:
                        is_correct = "correct"
                except:
                    pass
            
            # Extract better answer
            better_answer = ""
            if "Better Answer:" in feedback_text:
                try:
                    lines = feedback_text.split('\n')
                    better_idx = next(i for i, line in enumerate(lines) if 'Better Answer:' in line)
                    # Get everything after "Better Answer:" until next section or end
                    better_lines = []
                    for line in lines[better_idx:]:
                        if line.strip() and not line.strip().startswith(('STAR Method:', 'Score:', 'Correctness:')):
                            better_lines.append(line.replace('Better Answer:', '').strip())
                        elif line.strip().startswith('STAR Method:'):
                            break
                    better_answer = '\n'.join(better_lines).strip()
                except:
                    pass
            
            return {
                "score": min(10, max(1, score)),
                "feedback": feedback_text,
                "is_correct": is_correct,
                "better_answer": better_answer,
                "detailed_analysis": self._parse_feedback(feedback_text)
            }
            
        except Exception as e:
            print(f"Error evaluating answer: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "score": 5,
                "feedback": f"Error during evaluation: {str(e)}\n\nPlease try again or check your GROQ_API_KEY configuration.",
                "is_correct": "error",
                "better_answer": "",
                "detailed_analysis": {"strengths": [], "improvements": ["Unable to evaluate - technical error occurred"]}
            }
    
    def _parse_feedback(self, feedback_text: str) -> Dict[str, List[str]]:
        """Parse structured feedback from response"""
        strengths = []
        improvements = []
        
        lines = feedback_text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if 'Strengths:' in line:
                current_section = 'strengths'
            elif 'Improvements:' in line or 'Areas for Improvement' in line:
                current_section = 'improvements'
            elif line.startswith('-') or line.startswith('•'):
                item = line.lstrip('-•').strip()
                if current_section == 'strengths' and item:
                    strengths.append(item)
                elif current_section == 'improvements' and item:
                    improvements.append(item)
        
        return {
            "strengths": strengths[:3],  # Limit to 3
            "improvements": improvements[:3]
        }
    
    def get_practice_tips(self, question_type: str) -> List[str]:
        """Get general tips for answering different question types"""
        
        tips = {
            "behavioral": [
                "Use the STAR method: Situation, Task, Action, Result",
                "Be specific with examples from your experience",
                "Quantify your impact with numbers when possible",
                "Keep answers concise (1-2 minutes)",
                "Focus on YOUR actions, not just the team's"
            ],
            "technical": [
                "Think out loud to show your problem-solving process",
                "Ask clarifying questions if needed",
                "Discuss trade-offs between different approaches",
                "Mention edge cases you'd consider",
                "Be honest if you don't know something"
            ],
            "situational": [
                "Take a moment to think before answering",
                "Explain your reasoning step-by-step",
                "Consider company values in your response",
                "Show awareness of different perspectives",
                "Demonstrate leadership and initiative"
            ]
        }
        
        return tips.get(question_type, tips["behavioral"])
