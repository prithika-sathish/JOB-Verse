import streamlit as st


def apply_dashboard_theme() -> None:
    st.markdown(
        """
        <style>
            :root {
                --bg-dark: #0b1120;
                --card-dark: #111827;
                --text-dark: #e2e8f0;
                --muted-dark: #94a3b8;
                --primary-dark: #00ffd5;
                --secondary-dark: #00b8ff;
                --border-color: #1f2937;
            }

            .stApp {
                background: radial-gradient(circle at top right, rgba(0, 255, 213, 0.08), transparent 35%), var(--bg-dark);
                color: var(--text-dark);
            }

            .main .block-container {
                background: var(--card-dark);
                border: 1px solid var(--border-color);
                border-radius: 16px;
                padding: 2rem;
            }

            [data-testid="stHeader"] {
                background: transparent;
            }

            [data-testid="stSidebar"] {
                background: #0f172a;
                border-right: 1px solid var(--border-color);
            }

            [data-testid="stSidebar"] * {
                color: var(--text-dark) !important;
            }

            h1, h2, h3, h4, h5, h6,
            p, li, label,
            [data-testid="stMarkdownContainer"],
            [data-testid="stText"] {
                color: var(--text-dark) !important;
            }

            .stCaptionContainer,
            [data-testid="stCaptionContainer"] {
                color: var(--muted-dark) !important;
            }

            [data-baseweb="input"] input,
            [data-baseweb="textarea"] textarea,
            [data-baseweb="select"] > div,
            .stTextInput input,
            .stTextArea textarea,
            .stSelectbox div,
            .stMultiSelect div {
                background: #0f172a !important;
                color: var(--text-dark) !important;
                border-color: var(--border-color) !important;
            }

            .stButton button,
            .stDownloadButton button {
                background: linear-gradient(45deg, var(--primary-dark), var(--secondary-dark)) !important;
                color: #001018 !important;
                border: none !important;
                font-weight: 700 !important;
            }

            .stProgress > div > div {
                background: linear-gradient(45deg, var(--primary-dark), var(--secondary-dark)) !important;
            }

            [data-testid="stMetric"] {
                background: #0f172a;
                border: 1px solid var(--border-color);
                border-radius: 10px;
                padding: 0.75rem;
            }

            /* Bring inline HTML cards to dark mode */
            div[style*="background:white"],
            div[style*="background: white"],
            div[style*="background:#f8fafc"],
            div[style*="background: #f8fafc"],
            div[style*="background: rgb(248, 250, 252)"],
            div[style*="background:rgb(248, 250, 252)"],
            div[style*="background:#e2e8f0"],
            div[style*="background: #e2e8f0"] {
                background: #0f172a !important;
                border-color: var(--border-color) !important;
                color: var(--text-dark) !important;
            }

            [style*="color:#0f172a"],
            [style*="color: #0f172a"],
            [style*="color:#1e293b"],
            [style*="color: #1e293b"],
            [style*="color:#334155"],
            [style*="color: #334155"],
            [style*="color:#64748b"],
            [style*="color: #64748b"],
            [style*="color: rgb(71, 85, 105)"],
            [style*="color:rgb(71, 85, 105)"],
            [style*="color: rgb(100, 116, 139)"],
            [style*="color:rgb(100, 116, 139)"] {
                color: var(--text-dark) !important;
            }

            div[style*="background: rgb(248, 250, 252)"] p,
            div[style*="background:rgb(248, 250, 252)"] p,
            div[style*="background:#f8fafc"] p,
            div[style*="background: #f8fafc"] p,
            div[style*="background: rgb(248, 250, 252)"] h1,
            div[style*="background: rgb(248, 250, 252)"] h2,
            div[style*="background: rgb(248, 250, 252)"] h3,
            div[style*="background:#f8fafc"] h1,
            div[style*="background:#f8fafc"] h2,
            div[style*="background:#f8fafc"] h3 {
                color: var(--text-dark) !important;
            }

            [style*="background:#fef3c7"],
            [style*="background: #fef3c7"] {
                background: rgba(245, 158, 11, 0.14) !important;
                border-color: rgba(245, 158, 11, 0.35) !important;
            }

            [style*="background:#dcfce7"],
            [style*="background: #dcfce7"] {
                background: rgba(16, 185, 129, 0.14) !important;
                border-color: rgba(16, 185, 129, 0.35) !important;
            }

            .stTabs [data-baseweb="tab-list"] {
                background: #0f172a;
                border-radius: 10px;
            }

            .stTabs [aria-selected="true"] {
                color: var(--primary-dark) !important;
            }

            [data-testid="stStatusWidget"] {
                background: #0f172a;
                border: 1px solid var(--border-color);
                border-radius: 10px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
