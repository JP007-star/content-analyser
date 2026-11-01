"""
Content Analyser — Main Entry Point
Combines: YouTube Channel Analyzer + YouTube Analyzer (Skills & Tools)
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

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
        "JP Cinematic Universe": ("@jpcinematicuniverse", "Tech cinema, Trishul Stories"),
        "Java Prasad": ("@java-prasad", "Java education, interviews"),
        "JP Pipeline": ("@jp-pipeline", "DevOps, CI/CD, automation"),
        "JP News 360": ("@jp-news-360", "TTD Darshan, IPOs, Cinema, Cricket, Trending")
    }
    for name, (handle, niche) in channels.items():
        st.write(f"• **{name}** ({niche}): {handle}")

    st.divider()
    st.caption("Built with Streamlit + Claude Skills")

# ─── Main Content ───
if app_mode == "📊 YouTube Channel Analyzer":
    # Import and run the channel analyzer
    from youtube_analyzer_streamlit import main
    main()

elif app_mode == "🎯 YouTube Analyzer (Skills & Tools)":
    # Import and run the skills/tools analyzer
    from youtube_analyzer_app import main
    main()