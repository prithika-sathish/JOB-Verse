import streamlit as st
from agents.ethics_auditor_agent import EthicsAuditorAgent
from theme import apply_dashboard_theme

st.set_page_config(page_title="Ethics & Transparency", page_icon="🔒", layout="wide")
apply_dashboard_theme()

st.title("🔒 Ethics & Transparency Dashboard")
st.caption("Understand how AI makes decisions and ensure fairness")

# Initialize agent
@st.cache_resource
def get_auditor():
    return EthicsAuditorAgent()

auditor = get_auditor()

# Tabs for different audits
tab1, tab2, tab3 = st.tabs(["📄 Resume Audit", "📋 Job Description Audit", "🔍 Transparency Report"])

with tab1:
    st.subheader("Resume Bias Detection")
    st.write("Upload or paste your resume to check for potential biases that might trigger unfair filtering.")
    
    # File upload option
    uploaded_file = st.file_uploader(
        "Upload Resume (PDF, DOCX, TXT)",
        type=['pdf', 'docx', 'txt'],
        help="Upload your resume file and we'll extract the text automatically"
    )
    
    # Initialize resume text
    resume_text = ""
    
    # Extract text from uploaded file
    if uploaded_file is not None:
        try:
            if uploaded_file.type == "application/pdf":
                # PDF extraction
                import PyPDF2
                import io
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
                resume_text = "\n".join([page.extract_text() for page in pdf_reader.pages])
                st.success(f"✅ Extracted text from {uploaded_file.name}")
            
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                # DOCX extraction
                from docx import Document
                import io
                doc = Document(io.BytesIO(uploaded_file.read()))
                resume_text = "\n".join([para.text for para in doc.paragraphs])
                st.success(f"✅ Extracted text from {uploaded_file.name}")
            
            elif uploaded_file.type == "text/plain":
                # TXT extraction
                resume_text = uploaded_file.read().decode('utf-8')
                st.success(f"✅ Loaded {uploaded_file.name}")
                
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
            st.info("Please paste your resume text manually below")
    
    # Text area for manual input or showing extracted text
    resume_text = st.text_area(
        "Your Resume Content",
        value=resume_text,
        height=300,
        placeholder="Paste your resume text here or upload a file above...",
        help="We'll check for age indicators, gender-coded language, and other potential biases"
    )
    
    if st.button("🔍 Audit Resume", key="audit_resume_btn"):
        if not resume_text:
            st.error("Please provide resume content!")
        else:
            with st.spinner("Analyzing resume for biases..."):
                audit_result = auditor.audit_resume(resume_text)
                st.session_state.resume_audit = audit_result
                st.rerun()
    
    if 'resume_audit' in st.session_state:
        result = st.session_state.resume_audit
        score = result["score"]
        score_color = "#10b981" if score >= 80 else "#f59e0b" if score >= 60 else "#ef4444"
        
        st.markdown(f"""
        <div style="background:{score_color}20; padding:20px; border-radius:12px; text-align:center; border:2px solid {score_color}; margin:20px 0;">
            <h2 style="margin:0; color:{score_color};">Fairness Score: {score}/100</h2>
            <p style="margin:5px 0 0 0; color:#64748b;">
                {" Above average!" if score >= 80 else "Room for improvement" if score >= 60 else "Significant issues found"}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if result["biases_found"]:
                st.error(f"**Potential Biases Found ({len(result['biases_found'])})**")
                for bias in result["biases_found"]:
                    st.write(f"⚠️ {bias}")
            else:
                st.success("**No major biases detected!**")
        
        with col2:
            if result["suggestions"]:
                st.warning("**Suggestions for Improvement**")
                for suggestion in result["suggestions"]:
                    st.write(f"💡 {suggestion}")
            
            if result["inclusive_signals"] > 0:
                st.info(f"**Inclusive Language Detected:** {result['inclusive_signals']} instances")

with tab2:
    st.subheader("Job Description Fairness Analysis")
    st.write("Analyze job postings for discriminatory language and unrealistic requirements.")
    
    job_desc_text = st.text_area(
        "Job Description",
        height=300,
        placeholder="Paste the job description here...",
        help="We'll flag gendered language, age discrimination, and credential inflation",
        key="jd_input"
    )
    
    if st.button("🔍 Audit Job Description", key="audit_jd_btn"):
        if not job_desc_text:
            st.error("Please provide a job description!")
        else:
            with st.spinner("Analyzing job description..."):
                audit_result = auditor.audit_job_description(job_desc_text)
                st.session_state.jd_audit = audit_result
                st.rerun()
    
    if 'jd_audit' in st.session_state:
        result = st.session_state.jd_audit
        score = result["score"]
        score_color = "#10b981" if score >= 80 else "#f59e0b" if score >= 60 else "#ef4444"
        
        st.markdown(f"""
        <div style="background:{score_color}20; padding:20px; border-radius:12px; text-align:center; border:2px solid {score_color}; margin:20px 0;">
            <h2 style="margin:0; color:{score_color};">Fairness Score: {score}/100</h2>
            <p style="margin:5px 0 0 0; color:#64748b;">
                {"Fair and inclusive!" if score >= 80 else "Some concerns" if score >= 60 else "Potentially discriminatory"}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if result["issues"]:
            st.error(f"**Issues Found ({len(result['issues'])})**")
            for issue in result["issues"]:
                st.write(f"⚠️ {issue}")
        
        if result["flags"]:
            st.warning("**Specific Flags**")
            for flag in result["flags"]:
                st.write(f"🚩 {flag}")
        
        if not result["issues"]:
            st.success("**No discriminatory language detected!**")
        
        if result["inclusive_signals"] > 0:
            st.info(f"**Positive Signals:** {result['inclusive_signals']} inclusive phrases found")

with tab3:
    st.subheader("AI Transparency Report")
    st.write("Understand how the AI system makes decisions and recommendations.")
    
    if st.button("📊 Generate Transparency Report"):
        # Collect session data
        session_data = {}
        
        if 'resume_audit' in st.session_state:
            session_data['resume_analyzed'] = True
        if 'jd_audit' in st.session_state:
            session_data['job_description'] = True
        if 'analysis' in st.session_state:
            analysis = st.session_state.get('analysis', {})
            session_data['skill_gaps'] = analysis.get('gaps', {}).get('critical', []) + analysis.get('gaps', {}).get('moderate', [])
        if 'recommendations' in st.session_state:
            session_data['recommendations'] = st.session_state.recommendations
        
        report = auditor.generate_transparency_report(session_data)
        st.session_state.transparency_report = report
        st.rerun()
    
    if 'transparency_report' in st.session_state:
        st.markdown(st.session_state.transparency_report)
    
    st.divider()
    
    # Explainability section
    st.subheader("🤔 Ask About Any Decision")
    
    feature_type = st.selectbox(
        "What would you like explained?",
        ["course_recommendation", "interview_question", "bridge_role", "skill_gap"],
        format_func=lambda x: {
            "course_recommendation": "Why was a course recommended?",
            "interview_question": "Why was this interview question asked?",
            "bridge_role": "Why was this role suggested?",
            "skill_gap": "Why was this identified as a gap?"
        }[x]
    )
    
    value = st.text_input("Enter the specific item (e.g., course name, skill, role)")
    
    if st.button("Explain", key="explain_btn"):
        if value:
            explanation = auditor.explain_decision(feature_type, value)
            st.info(explanation)
        else:
            st.warning("Please enter a value to explain")

# Privacy & Control section
st.divider()
st.subheader("🔐 Your Privacy & Control")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Data We Collect:**
    - Resume/profile text (stored locally)
    - Job descriptions you analyze
    - Interview practice responses
    - Skill assessment results
    
    **We DO NOT:**
    - Share your data with third parties
    - Use your data to train models
    - Store personally identifiable information
    """)

with col2:
    st.markdown("""
    **Your Rights:**
    - View all collected data
    - Export your data anytime
    - Delete your data
    - Opt-out of any feature
    """)

if st.button("🗑️ Clear All Session Data"):
    # Clear all session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.success("All session data cleared!")
    st.rerun()
