import streamlit as st
import time
from agents.search_agent import SearchAgent, JobSearchConfig
from agents.memory_agent import MemoryAgent
from agents.personalization_agent import PersonalizationAgent
from dotenv import load_dotenv
from theme import apply_dashboard_theme

# Load Env
load_dotenv()

# UI Config
st.set_page_config(page_title="Agentic Job Search", layout="wide")
apply_dashboard_theme()

# Hide the home/app name from sidebar navigation
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] li:first-child {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    * {
        font-family: 'Inter', -apple-system, sans-serif;
    }

    .agent-card {
        background: #0f172a;
        padding: 24px;
        border-radius: 12px;
        border: 1px solid #1f2937;
        margin-bottom: 20px;
        transition: all 0.2s ease;
    }

    .agent-card:hover {
        border-color: #00ffd5;
        box-shadow: 0 4px 12px rgba(0, 255, 213, 0.15);
    }

    .bias-badge {
        padding: 6px 14px;
        border-radius: 16px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    .bias-safe {
        background-color: rgba(16, 185, 129, 0.2);
        color: #86efac;
    }

    .bias-warn {
        background-color: rgba(245, 158, 11, 0.2);
        color: #fcd34d;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("🤖 AI Career Development System")
st.caption("Intelligent job search • Interview coaching • Skill development • Career planning")

# Welcome message
st.markdown("""
### 🎯 Ready to launch. Configure your agents below.

Navigate using the sidebar to access all features:
- **🎤 Interview Coach** - Practice with AI-generated questions and feedback
- **📚 Skill Analysis** - Identify gaps and get learning roadmaps
- **🎯 Career Planning** - Predict your path and discover bridge roles
- **🔒 Ethics Dashboard** - Ensure fairness and transparency
""")

st.divider()

# Job Search Controls on Main Page
st.subheader("🔍 Intelligent Job Search")

col1, col2, col3 = st.columns(3)
with col1:
    query = st.text_input("💼 Job Title", "Software Engineer", help="Enter the job position you're looking for")
with col2:
    location = st.text_input("📍 Location", "Bengaluru", help="City, country, or 'Remote'")
with col3:
    work_style = st.selectbox("🏠 Work Style", ["Any", "Remote", "Hybrid", "Onsite"], index=0)

col4, col5 = st.columns([2, 1])
with col4:
    num_jobs = st.slider("Minimum Jobs to Fetch", min_value=5, max_value=20, value=10, step=1)
with col5:
    st.write("")  # Spacer
    st.write("")  # Spacer
    start_btn = st.button("🚀 Launch Agents", type="primary", use_container_width=True)


# Init Agents (Cached)
@st.cache_resource
def get_agents():
    return {
        "search": SearchAgent(),
        "memory": MemoryAgent(),
        "personalization": PersonalizationAgent()
    }

agents = get_agents()

# Sidebar: Ethical AI Settings
with st.sidebar:
    st.subheader("Ethical AI Settings")
    audit_mode = st.toggle("Enable Bias Auditing", value=True)

# Main Dashboard Area
if start_btn:
    # 1. Memory Retrieval
    with st.status("🧠 Memory Agent Active...", expanded=True) as status:
        st.write("Checking context database...")
        context = agents["memory"].get_context(query)
        if context:
            st.info(f"Found context from previous searches: {context[:100]}...")
        else:
            st.write("No previous context found.")
        status.update(label="Memory Agent Complete", state="complete")

    # 2. Search Execution
    with st.status("🕵️ Search Agent Active...", expanded=True) as status:
        st.write(f"Scouring the web for '{query}' in '{location}' ({work_style})...")
        config = JobSearchConfig(job_title=query, location=location, work_style=work_style, num_jobs=num_jobs)
        search_state = agents["search"].search(config)
        
        raw_count = search_state["count"]
        if search_state.get("status") == "disabled":
            st.warning(search_state.get("message", "Search provider is disabled."))
            status.update(label="Search Agent Disabled", state="complete")
        else:
            st.write(f"Found {raw_count} raw candidates.")
            status.update(label=f"Search Agent Complete ({raw_count} found)", state="complete")

    # 3. Personalization & Audit
    with st.status("⚖️ Personalization & Audit Agent Active...", expanded=True) as status:
        st.write("Analyzing job descriptions...")
        if audit_mode:
            st.write("Running Ethical Bias Audit on all listings...")
        
        # Process all fetched jobs (minimum is num_jobs, but can show more)
        processed_jobs = agents["personalization"].process_jobs(search_state["raw_results"]) 
        
        status.update(label="Analysis Complete", state="complete")

    # 4. Results Display
    st.divider()
    st.subheader("📋 Top Matches")
    
    if not processed_jobs:
        st.warning("⚠️ No job openings found for your search.")
        st.info("""
        **Try these tips:**
        - Broaden your location (try "Remote" or remove location)
        - Use different job title variations (e.g., "Developer" instead of "Engineer")  
        - Check back later - new positions are posted daily
        - Try related roles in your field
        """)
    
    for job in processed_jobs:
        # Determine card color based on bias score
        bias_class = "bias-safe" if not job["is_biased"] else "bias-warn"
        bias_text = f"Audit Score: {job['audit_score']}/100"
        
        # Prepare HTML with clean organization
        # Only show audit badge if audit mode is enabled
        audit_badge_html = f'<span class="bias-badge {bias_class}">{bias_text}</span>' if audit_mode else ''
        
        # Clean salary display
        salary_display = f'<div style="color:#16a34a; font-weight:600; margin-top:4px;">💰 {job.get("salary")}</div>' if job.get('salary') and job.get('salary') != 'Salary N/A' else ''
        
        card_html = f"""
<div class="agent-card" style="margin-bottom:20px;">
<div style="border-bottom:2px solid #e2e8f0; padding-bottom:12px; margin-bottom:12px;">
<div style="display:flex; justify-content:space-between; align-items:flex-start;">
<div style="flex:1;">
<h3 style="margin:0; color:#1e293b; font-size:1.4rem; font-weight:700; line-height:1.3;">{job['title']}</h3>
<div style="color:#64748b; font-size:1rem; margin-top:6px; font-weight:500;">🏢 {job['company']}</div>
{salary_display}
</div>
{audit_badge_html}
</div>
</div>
<div style="margin-bottom:16px;">
<div style="font-size:0.75rem; font-weight:700; color:#64748b; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:8px;">Job Description</div>
<div style="background:#f8fafc; padding:14px; border-radius:8px; border-left:3px solid #3b82f6;">
<p style="margin:0; font-size:0.95rem; line-height:1.7; color:#475569;">{job['description'][:300]}{'...' if len(job['description']) > 300 else ''}</p>
</div>
</div>
<div>
<a href="{job['url']}" target="_blank" style="text-decoration:none;">
<button style="background:linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); color:white; border:none; padding:12px 24px; border-radius:8px; cursor:pointer; font-weight:600; font-size:0.95rem; box-shadow:0 4px 6px rgba(37,99,235,0.3); transition:all 0.2s; width:100%;">
📋 View Full Job & Apply →
</button>
</a>
</div>
</div>
"""
        # Add flags if biased AND audit mode is enabled
        if audit_mode and (job['is_biased'] or (job.get('audit_flags') and len(job['audit_flags']) > 0 and "Skipped" in job['audit_flags'][0])):
             flag_class = "color:#dc2626;" if job['is_biased'] else "color:#d97706;"
             flag_html = f'<div style="{flag_class} margin:12px 0; padding:10px 14px; background:#fef2f2; border-left:3px solid #dc2626; border-radius:6px; font-size:0.85rem; font-weight:600;">⚠️ {", ".join(job["audit_flags"])}</div>'
             # Insert before closing button div
             card_html = card_html.replace('</div>\n</div>\n</div>', flag_html + '</div>\n</div>\n</div>')

        with st.container():
            st.markdown(card_html, unsafe_allow_html=True)

    # 5. Save Context
    agents["memory"].save_interaction(query, f"Found {len(processed_jobs)} jobs")

else:
    st.info("Ready to launch. Configure your agents in the sidebar.")
