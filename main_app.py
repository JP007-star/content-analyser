"""
Content Analyser — Main Entry Point
Combines: YouTube Channel Analyzer + YouTube Analyzer (Skills & Tools)
"""

import streamlit as st

# Page config
st.set_page_config(
    page_title="Content Analyser",
    page_icon="🔱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header { font-size: 2.5rem; font-weight: 700; margin-bottom: 0.5rem; color: #0a0f1a; }
    .sub-header { color: #00f3ff; font-size: 1.2rem; margin-bottom: 2rem; }
    .tool-card {
        background: #1a1f3a;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #00f3ff33;
        margin: 0.5rem 0;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .tool-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 243, 255, 0.15);
        border-color: #00f3ff66;
    }
    .tool-title { color: #00f3ff; font-size: 1.1rem; font-weight: 600; margin-bottom: 0.5rem; }
    .tool-desc { color: #8892b0; font-size: 0.9rem; }
    .stTabs [data-baseweb="tab"] { border-radius: 8px; padding: 10px 20px; }
</style>
""", unsafe_allow_html=True)

# ─── Sidebar ───
with st.sidebar:
    st.markdown("## 🔱 Content Analyser")
    st.caption("JP Cinematic Universe Toolkit")

    app_mode = st.radio(
        "Select Analyzer",
        ["📊 YouTube Channel Analyzer", "🎯 YouTube Analyzer (Skills & Tools)"],
        index=0
    )

    st.divider()

    st.markdown("### 📺 Channels")
    channels = {
        "JP Cinematic Universe": "@jpcinematicuniverse",
        "Java Prasad": "@java-prasad",
        "JP Pipeline": "@jp-pipeline"
    }
    for name, handle in channels.items():
        st.write(f"• **{name}**: {handle}")

    st.divider()
    st.caption("Built with Streamlit + Claude Skills")

# ─── Main Content ───
if app_mode == "📊 YouTube Channel Analyzer":
    # Run the existing channel analyzer
    exec(open("youtube_analyzer_streamlit.py", encoding="utf-8").read())

elif app_mode == "🎯 YouTube Analyzer (Skills & Tools)":
    # Run our new YouTube Analyzer with skills/tools
    exec(open("youtube_analyzer_app.py", encoding="utf-8").read())