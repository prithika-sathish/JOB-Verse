import streamlit as st
from agents.career_planner_agent import CareerPlannerAgent
from theme import apply_dashboard_theme

st.set_page_config(page_title="Career Planning", page_icon="🎯", layout="wide")
apply_dashboard_theme()

st.title("🎯 Career Trajectory & Planning")
st.caption("Predict your career path and discover bridge roles")

# Initialize agent
@st.cache_resource
def get_planner():
    return CareerPlannerAgent()

planner = get_planner()

# Input section
col1, col2 = st.columns(2)

with col1:
    st.subheader("📍 Current Position")
    current_role = st.text_input("Current Role/Title", placeholder="e.g., Junior Software Engineer")
    current_skills_text = st.text_area(
        "Current Skills (comma-separated)",
        height=100,
        placeholder="Python, React, Git, Problem Solving, Teamwork"
    )

with col2:
    st.subheader("🚀 Target Position")
    target_role = st.text_input("Target Role/Title", placeholder="e.g., Senior Full Stack Engineer")
    target_industry = st.text_input("Target Industry (optional)", placeholder="e.g., FinTech, Healthcare")

if st.button("🔮 Predict Career Path", type="primary", use_container_width=True):
    if not current_role or not target_role:
        st.error("Please provide both current and target roles!")
    else:
        with st.spinner("Analyzing career trajectory..."):
            # Parse skills
            skills = {"technical": [], "soft": [], "domain": []}
            if current_skills_text:
                skill_list = [s.strip() for s in current_skills_text.split(',') if s.strip()]
                skills["technical"] = skill_list[:5]
                skills["soft"] = skill_list[5:8] if len(skill_list) > 5 else []
            
            # Predict path
            career_path = planner.predict_career_path(current_role, target_role, skills)
            
            # Get bridge roles
            bridge_roles = planner.recommend_bridge_roles(current_role, target_role, skills)
            
            # Get networking strategy
            networking = planner.generate_networking_strategy(target_role, target_industry)
            
            # Store in session state
            st.session_state.career_path = career_path
            st.session_state.bridge_roles = bridge_roles
            st.session_state.networking = networking
            
            st.success("Career analysis complete!")
            st.rerun()

# Display results
if 'career_path' in st.session_state:
    st.divider()
    
    path = st.session_state.career_path
    
    # Feasibility and Timeline
    col1, col2 = st.columns(2)
    
    with col1:
        feasibility = path["feasibility_score"]
        feas_color = "#10b981" if feasibility >= 7 else "#f59e0b" if feasibility >= 5 else "#ef4444"
        
        st.markdown(f"""
        <div style="background:{feas_color}20; padding:20px; border-radius:12px; text-align:center; border:2px solid {feas_color};">
            <h3 style="margin:0; color:{feas_color};">Feasibility Score</h3>
            <h1 style="margin:10px 0 0 0; color:{feas_color};">{feasibility}/10</h1>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        timeline = path["timeline_months"]
        timeline_years = timeline / 12
        
        st.markdown(f"""
        <div style="background:#3b82f620; padding:20px; border-radius:12px; text-align:center; border:2px solid #3b82f6;">
            <h3 style="margin:0; color:#3b82f6;">Estimated Timeline</h3>
            <h1 style="margin:10px 0 0 0; color:#3b82f6;">{timeline} months</h1>
            <p style="margin:5px 0 0 0; color:#64748b;">≈ {timeline_years:.1f} years</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.write("")
    
    # Milestones
    st.subheader("📍 Key Milestones")
    milestones = path.get("milestones", [])
    
    for i, milestone in enumerate(milestones, 1):
        st.markdown(f"""
        <div style="background:white; padding:12px 16px; border-radius:8px; border-left:4px solid #3b82f6; margin-bottom:8px;">
            <b style="color:#3b82f6;">{i}.</b> {milestone}
        </div>
        """, unsafe_allow_html=True)
    
    st.write("")
    
    # Skill Gap & Roadmap Generation
    st.divider()
    st.subheader("🎓 Skill Development Roadmap")
    
    # Determine if roadmap is needed based on feasibility
    feasibility = path["feasibility_score"]
    
    if feasibility < 8:
        st.warning(f"⚠️ Feasibility Score: {feasibility}/10 - Your skills may not fully match the target position yet.")
        st.info("💡 A personalized learning roadmap can help you bridge the skill gap and reach your target role faster!")
        
        if st.button("📚 Generate My Learning Roadmap", type="primary", key="gen_roadmap"):
            with st.spinner("🤖 AI is creating your personalized roadmap..."):
                roadmap = planner.generate_skill_roadmap(
                    current_role=path["current_role"],
                    target_role=path["target_role"],
                    current_skills_text=current_skills_text,
                    feasibility_score=feasibility
                )
                st.session_state.learning_roadmap = roadmap
                st.rerun()
    else:
        st.success(f"✅ High Feasibility ({feasibility}/10) - Your skills align well! Keep building on your strengths.")
    
    # Display roadmap if generated
    if 'learning_roadmap' in st.session_state:
        st.write("")
        roadmap = st.session_state.learning_roadmap
        
        # Skill gaps
        if 'skill_gaps' in roadmap and roadmap['skill_gaps']:
            st.markdown("**🎯 Skills You Need to Develop:**")
            cols = st.columns(2)
            
            for i, skill in enumerate(roadmap['skill_gaps'][:8]):
                with cols[i % 2]:
                    st.markdown(f"""
                    <div style="background:#fef3c7; padding:10px 12px; border-radius:8px; margin-bottom:8px; border-left:4px solid #f59e0b;">
                        <b style="color:#d97706;">↗</b> {skill}
                    </div>
                    """, unsafe_allow_html=True)
        
        st.write("")
        
        # Learning phases
        if 'learning_phases' in roadmap and roadmap['learning_phases']:
            st.markdown("**📚 Your Learning Journey:**")
            
            for idx, phase in enumerate(roadmap['learning_phases'], 1):
                phase_name = phase.get('phase_name', f'Phase {idx}')
                duration = phase.get('duration', '3 months')
                
                with st.expander(f"**{phase_name}** — {duration}", expanded=(idx == 1)):
                    focus = phase.get('focus', 'Build foundational skills')
                    st.write(f"**🎯 Focus:** {focus}")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        resources = phase.get('resources', [])
                        if resources:
                            st.write("**📖 Resources:**")
                            for resource in resources[:5]:
                                st.write(f"• {resource}")
                    
                    with col2:
                        projects = phase.get('projects', [])
                        if projects:
                            st.write("**🛠️ Practice Projects:**")
                            for project in projects[:4]:
                                st.write(f"• {project}")
        
        # Total duration
        total = roadmap.get('total_duration', '6-12 months')
        st.write("")
        st.info(f"⏱️ **Estimated Total Time:** {total}")
        st.progress(0, text="🚀 Start your journey today!")
    
    # Bridge Roles
    if 'bridge_roles' in st.session_state and st.session_state.bridge_roles:
        st.divider()
        st.subheader("🌉 Recommended Bridge Roles")
        st.caption("Intermediate positions that can help you reach your target")
        
        bridge_roles = st.session_state.bridge_roles
        
        for role in bridge_roles:
            with st.expander(f"**{role.get('role_title', 'Bridge Role')}** ({role.get('timeline_months', 12)} months)"):
                st.write(f"**Why this role:** {role.get('rationale', 'Strategic stepping stone')}")
                
                skills_built = role.get('skills_built', [])
                if skills_built:
                    st.write("**Skills you'll build:**")
                    for skill in skills_built[:5]:
                        st.write(f"• {skill}")
                
                # Visual timeline
                months = role.get('timeline_months', 12)
                progress_width = min(100, (months / 24) * 100)
                st.markdown(f"""
                <div style="background:#e2e8f0; height:20px; border-radius:10px; margin-top:10px;">
                    <div style="background:#3b82f6; height:100%; width:{progress_width}%; border-radius:10px;"></div>
                </div>
                <p style="font-size:0.8rem; color:#64748b; margin-top:5px;">Typical duration: {months} months</p>
                """, unsafe_allow_html=True)
    
    # Networking Strategy
    if 'networking' in st.session_state:
        st.divider()
        st.subheader("🤝 Networking Strategy")
        
        networking = st.session_state.networking
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**👥 Who to Connect With:**")
            target_contacts = networking.get('target_contacts', [])
            for contact in target_contacts[:5]:
                st.write(f"• {contact}")
        
        with col2:
            st.markdown("**🎪 Events & Communities:**")
            events = networking.get('events_communities', [])
            for event in events[:5]:
                st.write(f"• {event}")
        
        # Outreach template
        template = networking.get('outreach_template', '')
        if template.strip():
            st.markdown("**✉️ Outreach Message Template:**")
            st.code(template.strip(), language=None)

else:
    st.info("👆 Enter your current and target roles above to get started!", icon="ℹ️")

# Career Path Visualization
if 'career_path' in st.session_state and 'bridge_roles' in st.session_state:
    st.divider()
    st.subheader("🗺️ Career Journey Visualization")
    
    current = st.session_state.career_path["current_role"]
    target = st.session_state.career_path["target_role"]
    bridges = st.session_state.bridge_roles
    
    # Create visual path
    roles_path = [current] + [b.get('role_title', '') for b in bridges[:3]] + [target]
    
    # Build HTML visualization
    path_html = '<div style="display:flex; align-items:center; justify-content:space-around; flex-wrap:wrap; gap:10px;">'
    
    for i, role in enumerate(roles_path):
        # Color coding
        if i == 0:
            color = "#64748b"  # Current (gray)
        elif i == len(roles_path) - 1:
            color = "#10b981"  # Target (green)
        else:
            color = "#3b82f6"  # Bridge (blue)
        
        path_html += f"""
        <div style="flex:1; min-width:150px; text-align:center;">
            <div style="background:{color}; color:white; padding:15px; border-radius:12px; font-weight:600;">
                {role}
            </div>
        </div>
        """
        
        if i < len(roles_path) - 1:
            path_html += '<div style="color:#cbd5e1; font-size:2rem;">→</div>'
    
    path_html += '</div>'
    
    st.markdown(path_html, unsafe_allow_html=True)
