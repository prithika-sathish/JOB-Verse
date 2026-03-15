import streamlit as st
from agents.skill_analyzer_agent import SkillAnalyzerAgent
from theme import apply_dashboard_theme

st.set_page_config(page_title="Skill Gap Analysis", page_icon="📚", layout="wide")
apply_dashboard_theme()

st.title("📚 Skill Gap Analysis & Learning Roadmap")
st.caption("Identify skill gaps and get personalized learning recommendations")

# Initialize agent
@st.cache_resource
def get_analyzer():
    return SkillAnalyzerAgent()

analyzer = get_analyzer()

# Input section
col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 Your Resume / Profile")
    
    # File upload option with 5MB limit
    uploaded_file = st.file_uploader(
        "Upload Resume (PDF, DOCX, TXT) - Max 5MB",
        type=['pdf', 'docx', 'txt'],
        help="Upload your resume file and we'll extract the text automatically"
    )
    
    # Initialize resume text
    resume_text = ""
    
    # Extract text from uploaded file with size validation
    if uploaded_file is not None:
        # Check file size (5MB limit)
        file_size = uploaded_file.size
        max_size = 5 * 1024 * 1024  # 5MB in bytes
        
        if file_size > max_size:
            st.error(f"❌ File too large! ({file_size / (1024*1024):.2f}MB). Maximum: 5MB")
        else:
            try:
                if uploaded_file.type == "application/pdf":
                    import PyPDF2
                    import io
                    pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
                    resume_text = "\n".join([page.extract_text() for page in pdf_reader.pages])
                    st.success(f"✅ Extracted from {uploaded_file.name} ({file_size / 1024:.1f}KB)")
                
                elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    from docx import Document
                    import io
                    doc = Document(io.BytesIO(uploaded_file.read()))
                    resume_text = "\n".join([para.text for para in doc.paragraphs])
                    st.success(f"✅ Extracted from {uploaded_file.name} ({file_size / 1024:.1f}KB)")
                
                elif uploaded_file.type == "text/plain":
                    resume_text = uploaded_file.read().decode('utf-8')
                    st.success(f"✅ Loaded {uploaded_file.name} ({file_size / 1024:.1f}KB)")
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info("Please paste your resume text manually below")
    
    resume_text = st.text_area(
        "Paste your resume or describe your current skills",
        value=resume_text,
        height=250,
        placeholder="Example:\nSoftware Engineer with 3 years experience in Python, Django, React...",
        help="Include your skills, experience, and accomplishments"
    )

with col2:
    st.subheader("🎯 Target Job Description")
    job_text = st.text_area(
        "Paste the job description you're targeting",
        height=250,
        placeholder="Example:\nWe're looking for a Senior Full Stack Engineer with expertise in Python, React, AWS...",
        help="Paste the complete job posting"
    )

if st.button("🔍 Analyze Skill Gaps", type="primary", use_container_width=True):
    if not resume_text or not job_text:
        st.error("Please provide both your resume and target job description!")
    else:
        with st.spinner("Analyzing skills and identifying gaps..."):
            # Extract skills
            resume_skills = analyzer.extract_skills_from_text(resume_text, "resume")
            job_skills = analyzer.extract_skills_from_text(job_text, "job_description")
            
            # Analyze gaps
            analysis = analyzer.analyze_skill_gaps(resume_skills, job_skills)
            
            # Get recommendations for gaps
            all_gaps = analysis["gaps"]["critical"] + analysis["gaps"]["moderate"]
            recommendations = analyzer.recommend_learning_resources(all_gaps)
            
            # Generate roadmap
            roadmap = analyzer.generate_learning_roadmap(recommendations)
            
            # Store in session state
            st.session_state.analysis = analysis
            st.session_state.recommendations = recommendations
            st.session_state.roadmap = roadmap
            
            st.success("Analysis complete!")
            st.rerun()

# Display results
if 'analysis' in st.session_state:
    st.divider()
    
    analysis = st.session_state.analysis
    
    # Match percentage
    match_pct = analysis["match_percentage"]
    match_color = "#10b981" if match_pct >= 70 else "#f59e0b" if match_pct >= 50 else "#ef4444"
    
    st.markdown(f"""
    <div style="background:{match_color}20; padding:20px; border-radius:12px; text-align:center; border-left:5px solid {match_color};">
        <h2 style="margin:0; color:{match_color};">Overall Match: {match_pct}%</h2>
        <p style="margin:5px 0 0 0; color:#64748b;">Based on skills alignment with job requirements</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    
    # Skills breakdown
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("✅ Matched Skills")
        matched = analysis["matched"]
        
        if matched["technical"]:
            st.success(f"**Technical ({len(matched['technical'])})**")
            for skill in matched["technical"]:
                st.write(f"• {skill}")
        
        if matched["soft"]:
            st.success(f"**Soft Skills ({len(matched['soft'])})**")
            for skill in matched["soft"]:
                st.write(f"• {skill}")
        
        if matched["domain"]:
            st.success(f"**Domain Knowledge ({len(matched['domain'])})**")
            for skill in matched["domain"]:
                st.write(f"• {skill}")
    
    with col2:
        st.subheader("❌ Skill Gaps")
        gaps = analysis["gaps"]
        
        if gaps["critical"]:
            st.error(f"**Critical Gaps ({len(gaps['critical'])})**")
            for skill in gaps["critical"]:
                st.write(f"• {skill}")
        
        if gaps["moderate"]:
            st.warning(f"**Moderate Gaps ({len(gaps['moderate'])})**")
            for skill in gaps["moderate"]:
                st.write(f"• {skill}")
        
        if gaps["minor"]:
            st.info(f"**Nice-to-Have ({len(gaps['minor'])})**")
            for skill in gaps["minor"]:
                st.write(f"• {skill}")
    
    # Learning recommendations
    if 'recommendations' in st.session_state and st.session_state.recommendations:
        st.divider()
        st.subheader("📚 Recommended Courses")
        
        recommendations = st.session_state.recommendations
        
        for rec in recommendations[:8]:  # Show top 8
            priority_color = {"High": "#ef4444", "Medium": "#f59e0b", "Low": "#64748b"}.get(rec.get('priority', 'Medium'), "#64748b")
            
            with st.container():
                st.markdown(f"""
                <div style="background:white; padding:15px; border-radius:8px; border-left:4px solid {priority_color}; margin-bottom:10px;">
                    <div style="display:flex; justify-content:space-between; align-items:start;">
                        <div>
                            <h4 style="margin:0; color:#0f172a;">{rec.get('course', 'Course')}</h4>
                            <p style="margin:5px 0; color:#64748b; font-size:0.9rem;">
                                <b>Skill:</b> {rec.get('skill', 'N/A')} | 
                                <b>Platform:</b> {rec.get('platform', 'N/A')} | 
                                <b>Duration:</b> {rec.get('duration', 'N/A')}
                            </p>
                        </div>
                        <span style="background:{priority_color}20; color:{priority_color}; padding:4px 12px; border-radius:12px; font-size:0.75rem; font-weight:600;">
                            {rec.get('priority', 'Medium')} Priority
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # 12-month roadmap
    if 'roadmap' in st.session_state:
        st.divider()
        st.subheader("📅 12-Month Learning Roadmap")
        
        roadmap = st.session_state.roadmap
        
        timeline_sections = [
            ("Months 1-3: Foundation", "months_1_3", "#3b82f6"),
            ("Months 4-6: Intermediate", "months_4_6", "#8b5cf6"),
            ("Months 7-9: Advanced", "months_7_9", "#ec4899"),
            ("Months 10-12: Specialization", "months_10_12", "#10b981")
        ]
        
        for title, key, color in timeline_sections:
            if roadmap.get(key):
                st.markdown(f"""
                <div style="background:{color}15; padding:12px; border-radius:8px; border-left:4px solid {color}; margin-bottom:12px;">
                    <h4 style="margin:0 0 8px 0; color:{color};">{title}</h4>
                </div>
                """, unsafe_allow_html=True)
                
                for course in roadmap[key]:
                    st.write(f"• **{course.get('course', 'Course')}** ({course.get('platform', 'Platform')}) - {course.get('skill', 'Skill')}")
                
                st.write("")

else:
    st.info("👆 Enter your resume and target job description above to get started!", icon="ℹ️")
