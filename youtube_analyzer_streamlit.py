"""
YouTube Channel Analyzer — Streamlit App
Analyzes any YouTube channel using YouTube Data API v3
Run: streamlit run youtube_analyzer_streamlit.py
"""

import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from datetime import datetime
from typing import Optional, Dict, List
import time

# ============ CONFIG ============
st.set_page_config(
    page_title="YouTube Channel Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stMetric { background: #f8f9fa; padding: 1rem; border-radius: 0.5rem; border: 1px solid #e9ecef; }
    .metric-card { background: white; padding: 1.5rem; border-radius: 12px; border: 1px solid #e0e4eb; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { border-radius: 8px; padding: 8px 16px; }
    .main-header { font-size: 2.5rem; font-weight: 700; margin-bottom: 0.5rem; }
    .channel-handle { font-family: monospace; color: #009d7a; font-size: 1.2rem; }
    .demo-badge { background: #fff3cd; color: #856404; padding: 4px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: 500; }
</style>
""", unsafe_allow_html=True)

# ============ CONSTANTS ============
YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"
DEFAULT_CHANNEL = "@java-prasad"
MAX_VIDEOS = 50

# ============ API FUNCTIONS ============
@st.cache_data(ttl=300, show_spinner=False)
def resolve_channel_id(api_key: str, channel_input: str) -> Optional[str]:
    """Resolve channel handle/ID to channel ID."""
    clean = channel_input.strip().replace("@", "")

    # If already a channel ID
    if clean.startswith("UC") and len(clean) == 24:
        return clean

    # Try forHandle
    url = f"{YOUTUBE_API_BASE}/channels"
    params = {"part": "id", "forHandle": clean, "key": api_key}
    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.ok:
            data = resp.json()
            if data.get("items"):
                return data["items"][0]["id"]
    except Exception:
        pass

    # Fallback: search
    params = {"part": "snippet", "type": "channel", "q": clean, "maxResults": 1, "key": api_key}
    url = f"{YOUTUBE_API_BASE}/search"
    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.ok:
            data = resp.json()
            if data.get("items"):
                return data["items"][0]["snippet"]["channelId"]
    except Exception:
        pass

    return None


@st.cache_data(ttl=300, show_spinner=False)
def fetch_channel_stats(api_key: str, channel_id: str) -> Optional[Dict]:
    """Fetch channel statistics and snippet."""
    url = f"{YOUTUBE_API_BASE}/channels"
    params = {"part": "snippet,statistics,contentDetails,brandingSettings", "id": channel_id, "key": api_key}
    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.ok:
            data = resp.json()
            if data.get("items"):
                return data["items"][0]
    except Exception as e:
        st.error(f"Error fetching channel: {e}")
    return None


@st.cache_data(ttl=300, show_spinner=False)
def fetch_recent_videos(api_key: str, channel_id: str, max_results: int = 20) -> List[Dict]:
    """Fetch recent videos with statistics."""
    # Get uploads playlist ID
    url = f"{YOUTUBE_API_BASE}/channels"
    params = {"part": "contentDetails", "id": channel_id, "key": api_key}
    try:
        resp = requests.get(url, params=params, timeout=10)
        if not resp.ok:
            return []
        data = resp.json()
        uploads_playlist = data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    except Exception:
        return []

    # Get playlist items
    url = f"{YOUTUBE_API_BASE}/playlistItems"
    params = {"part": "snippet,contentDetails", "playlistId": uploads_playlist, "maxResults": max_results, "key": api_key}
    try:
        resp = requests.get(url, params=params, timeout=10)
        if not resp.ok:
            return []
        data = resp.json()
        video_ids = [item["contentDetails"]["videoId"] for item in data.get("items", [])]
    except Exception:
        return []

    if not video_ids:
        return []

    # Get video details
    url = f"{YOUTUBE_API_BASE}/videos"
    params = {"part": "snippet,statistics,contentDetails", "id": ",".join(video_ids), "key": api_key}
    try:
        resp = requests.get(url, params=params, timeout=10)
        if not resp.ok:
            return []
        data = resp.json()
        videos = []
        for item in data.get("items", []):
            stats = item.get("statistics", {})
            videos.append({
                "video_id": item["id"],
                "title": item["snippet"]["title"],
                "published_at": item["snippet"]["publishedAt"],
                "thumbnail": item["snippet"]["thumbnails"].get("medium", {}).get("url", ""),
                "view_count": int(stats.get("viewCount", 0)),
                "like_count": int(stats.get("likeCount", 0)),
                "comment_count": int(stats.get("commentCount", 0)),
                "duration": item["contentDetails"]["duration"],
            })
        return videos
    except Exception:
        return []


def parse_duration(iso_duration: str) -> str:
    """Parse ISO 8601 duration to readable format."""
    import re
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso_duration)
    if not match:
        return "—"
    h, m, s = match.groups()
    h, m, s = int(h or 0), int(m or 0), int(s or 0)
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def format_number(num: int) -> str:
    """Format large numbers with K/M/B suffixes."""
    if num >= 1_000_000_000:
        return f"{num / 1_000_000_000:.1f}B".replace(".0", "")
    if num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M".replace(".0", "")
    if num >= 1_000:
        return f"{num / 1_000:.1f}K".replace(".0", "")
    return f"{num:,}"


# ============ DEMO DATA ============
def get_demo_data() -> tuple:
    """Return demo channel data and videos for testing."""
    demo_channel = {
        "snippet": {
            "title": "Java Prasad",
            "customUrl": "@java-prasad",
            "publishedAt": "2020-03-15T00:00:00Z",
            "thumbnails": {"medium": {"url": ""}}
        },
        "statistics": {
            "subscriberCount": "127000",
            "viewCount": "8920000",
            "videoCount": "85"
        },
        "id": "UCdemo12345678901234567890"
    }

    demo_videos = [
        {"video_id": "demo1", "title": "Java 21 Features You Need to Know", "published_at": "2024-01-15T10:00:00Z", "view_count": 45200, "like_count": 2100, "comment_count": 180, "duration": "PT12M34S"},
        {"video_id": "demo2", "title": "Spring Boot 3.2 Tutorial", "published_at": "2024-01-08T10:00:00Z", "view_count": 38700, "like_count": 1850, "comment_count": 145, "duration": "PT18M22S"},
        {"video_id": "demo3", "title": "Java vs Kotlin in 2024", "published_at": "2024-01-01T10:00:00Z", "view_count": 52100, "like_count": 2800, "comment_count": 320, "duration": "PT15M45S"},
        {"video_id": "demo4", "title": "Building REST APIs with Spring Boot", "published_at": "2023-12-25T10:00:00Z", "view_count": 31400, "like_count": 1420, "comment_count": 98, "duration": "PT22M10S"},
        {"video_id": "demo5", "title": "Java Virtual Threads Deep Dive", "published_at": "2023-12-18T10:00:00Z", "view_count": 41800, "like_count": 2200, "comment_count": 210, "duration": "PT16M55S"},
        {"video_id": "demo6", "title": "Maven vs Gradle 2024", "published_at": "2023-12-11T10:00:00Z", "view_count": 28900, "like_count": 1200, "comment_count": 85, "duration": "PT14M30S"},
        {"video_id": "demo7", "title": "Testing Spring Boot Applications", "published_at": "2023-12-04T10:00:00Z", "view_count": 24500, "like_count": 1100, "comment_count": 72, "duration": "PT19M15S"},
        {"video_id": "demo8", "title": "Java Records Pattern Matching", "published_at": "2023-11-27T10:00:00Z", "view_count": 33200, "like_count": 1650, "comment_count": 130, "duration": "PT13M40S"},
        {"video_id": "demo9", "title": "Dockerizing Spring Boot Apps", "published_at": "2023-11-20T10:00:00Z", "view_count": 29800, "like_count": 1380, "comment_count": 95, "duration": "PT20M05S"},
        {"video_id": "demo10", "title": "Java 21 String Templates Preview", "published_at": "2023-11-13T10:00:00Z", "view_count": 36700, "like_count": 1720, "comment_count": 110, "duration": "PT11M50S"},
    ]
    return demo_channel, demo_videos


# ============ VISUALIZATION FUNCTIONS ============
def create_views_chart(df: pd.DataFrame) -> go.Figure:
    """Bar chart: Views per video."""
    df = df.sort_values("published_at").copy()
    df["date_label"] = pd.to_datetime(df["published_at"]).dt.strftime("%b %d")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["date_label"],
        y=df["view_count"],
        name="Views",
        marker_color="#009d7a",
        marker_line_color="#00d4aa",
        marker_line_width=1.5,
        hovertemplate="<b>%{x}</b><br>Views: %{y:,}<br>%{customdata}<extra></extra>",
        customdata=df["title"]
    ))
    fig.update_layout(
        title="Views per Video (Recent)",
        xaxis_title="Publish Date",
        yaxis_title="Views",
        template="plotly_white",
        height=350,
        margin=dict(l=40, r=20, t=50, b=40),
        hovermode="x unified"
    )
    return fig


def create_engagement_chart(df: pd.DataFrame) -> go.Figure:
    """Line chart: Engagement rate over time."""
    df = df.sort_values("published_at").copy()
    df["engagement_rate"] = ((df["like_count"] + df["comment_count"]) / df["view_count"] * 100).round(2)
    df["date_label"] = pd.to_datetime(df["published_at"]).dt.strftime("%b %d")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date_label"],
        y=df["engagement_rate"],
        mode="lines+markers",
        name="Engagement %",
        line=dict(color="#009d7a", width=3),
        marker=dict(size=8, color="#009d7a", line=dict(width=2, color="white")),
        fill="tozeroy",
        fillcolor="rgba(0, 157, 122, 0.1)",
        hovertemplate="<b>%{x}</b><br>Engagement: %{y:.2f}%<br>%{customdata}<extra></extra>",
        customdata=df["title"]
    ))
    fig.update_layout(
        title="Engagement Rate by Video",
        xaxis_title="Publish Date",
        yaxis_title="Engagement %",
        template="plotly_white",
        height=350,
        margin=dict(l=40, r=20, t=50, b=40),
        hovermode="x unified"
    )
    return fig


def create_frequency_chart(df: pd.DataFrame) -> go.Figure:
    """Bar chart: Upload frequency per month."""
    df["month"] = pd.to_datetime(df["published_at"]).dt.to_period("M")
    monthly = df.groupby("month").size().reset_index(name="count")
    monthly["month_label"] = monthly["month"].dt.strftime("%b %Y")

    # Ensure last 12 months shown
    all_months = pd.period_range(end=pd.Timestamp.now(), periods=12, freq="M")
    all_df = pd.DataFrame({"month": all_months})
    all_df["month_label"] = all_df["month"].dt.strftime("%b %Y")
    merged = all_df.merge(monthly[["month", "count"]], on="month", how="left").fillna(0)
    merged["count"] = merged["count"].astype(int)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=merged["month_label"],
        y=merged["count"],
        name="Videos",
        marker_color="#009d7a",
        marker_line_color="#00d4aa",
        marker_line_width=1.5,
        hovertemplate="<b>%{x}</b><br>Videos: %{y}<extra></extra>"
    ))
    fig.update_layout(
        title="Upload Frequency (Last 12 Months)",
        xaxis_title="Month",
        yaxis_title="Videos Published",
        template="plotly_white",
        height=350,
        margin=dict(l=40, r=20, t=50, b=40),
        hovermode="x unified"
    )
    return fig


def create_growth_chart(df: pd.DataFrame) -> go.Figure:
    """Area chart: Cumulative views growth."""
    df = df.sort_values("published_at").copy()
    df["cumulative_views"] = df["view_count"].cumsum()
    df["date_label"] = pd.to_datetime(df["published_at"]).dt.strftime("%b %d")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date_label"],
        y=df["cumulative_views"],
        mode="lines",
        name="Cumulative Views",
        line=dict(color="#009d7a", width=3),
        fill="tozeroy",
        fillcolor="rgba(0, 157, 122, 0.15)",
        hovertemplate="<b>%{x}</b><br>Total Views: %{y:,}<extra></extra>"
    ))
    fig.update_layout(
        title="Cumulative Views Growth",
        xaxis_title="Publish Date",
        yaxis_title="Cumulative Views",
        template="plotly_white",
        height=350,
        margin=dict(l=40, r=20, t=50, b=40),
        hovermode="x unified"
    )
    return fig


# ============ MAIN APP ============
def main():
    # Header
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown('<div class="main-header">📊 YouTube Channel Analyzer</div>', unsafe_allow_html=True)
        st.markdown('<span class="channel-handle">Analyze any channel with YouTube Data API v3</span>', unsafe_allow_html=True)
    with col2:
        st.markdown('<span class="demo-badge">Try Demo Data</span>', unsafe_allow_html=True)

    st.divider()

    # Sidebar - Configuration
    with st.sidebar:
        st.header("⚙️ Configuration")

        # API Key input
        api_key = st.text_input(
            "YouTube Data API Key",
            type="password",
            placeholder="AIzaSy...",
            help="Get a free key at Google Cloud Console → Enable YouTube Data API v3"
        )

        # Channel input
        channel_input = st.text_input(
            "Channel Handle or ID",
            value=DEFAULT_CHANNEL,
            placeholder="@handle or UC...",
            help="Enter @handle or channel ID (UC...)"
        )

        max_videos = st.slider("Max Videos to Analyze", 5, 50, 20, 5)

        st.divider()

        # Action buttons
        col_a, col_b = st.columns(2)
        with col_a:
            analyze_btn = st.button("🔍 Analyze", type="primary", use_container_width=True)
        with col_b:
            demo_btn = st.button("🎯 Load Demo", use_container_width=True)

        st.divider()

        # API Key help
        with st.expander("🔑 How to get API Key"):
            st.markdown("""
            1. Go to [Google Cloud Console](https://console.cloud.google.com/)
            2. Create/select a project
            3. Enable **YouTube Data API v3**
            4. Go to **Credentials** → **Create Credentials** → **API Key**
            5. Copy the key (starts with `AIzaSy...`)
            6. Optional: Restrict key to YouTube Data API
            """)

        st.caption("💡 Demo data works without API key")

    # Main content area
    if "data_loaded" not in st.session_state:
        st.session_state.data_loaded = False
        st.session_state.demo_mode = False
        st.session_state.channel_data = None
        st.session_state.videos_data = []

    # Load demo data
    if demo_btn:
        with st.spinner("Loading demo data..."):
            time.sleep(0.5)
            channel, videos = get_demo_data()
            st.session_state.channel_data = channel
            st.session_state.videos_data = videos
            st.session_state.data_loaded = True
            st.session_state.demo_mode = True
            st.success("✅ Demo data loaded!")
            st.rerun()

    # Analyze real channel
    if analyze_btn:
        if not api_key:
            st.error("❌ Please enter a YouTube Data API key")
            st.stop()
        if not channel_input.strip():
            st.error("❌ Please enter a channel handle or ID")
            st.stop()

        with st.spinner(f"Analyzing {channel_input}..."):
            # Resolve channel ID
            channel_id = resolve_channel_id(api_key, channel_input)
            if not channel_id:
                st.error("❌ Channel not found. Check the handle/ID and API key.")
                st.stop()

            # Fetch data
            channel = fetch_channel_stats(api_key, channel_id)
            if not channel:
                st.error("❌ Failed to fetch channel data. Check API key permissions.")
                st.stop()

            videos = fetch_recent_videos(api_key, channel_id, max_videos)
            if not videos:
                st.warning("⚠️ No videos found for this channel")
                st.stop()

            st.session_state.channel_data = channel
            st.session_state.videos_data = videos
            st.session_state.data_loaded = True
            st.session_state.demo_mode = False
            st.success(f"✅ Analyzed {len(videos)} videos!")
            st.rerun()

    # Display results
    if st.session_state.data_loaded and st.session_state.channel_data:
        channel = st.session_state.channel_data
        videos = st.session_state.videos_data
        df = pd.DataFrame(videos)
        df["published_at"] = pd.to_datetime(df["published_at"])
        df["engagement_rate"] = ((df["like_count"] + df["comment_count"]) / df["view_count"] * 100).round(2)
        df["duration_str"] = df["duration"].apply(parse_duration)

        snippet = channel["snippet"]
        stats = channel["statistics"]

        # Channel info header
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader(f"{snippet.get('title', 'Unknown Channel')}")
            st.caption(f"Channel ID: {channel['id']} | Joined: {pd.to_datetime(snippet['publishedAt']).strftime('%B %d, %Y')}")
        with col2:
            if st.session_state.demo_mode:
                st.info("🎯 Demo Mode")

        # Stats cards
        st.markdown("### 📈 Channel Overview")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("👥 Subscribers", format_number(int(stats.get("subscriberCount", 0))))
        with c2:
            st.metric("👁️ Total Views", format_number(int(stats.get("viewCount", 0))))
        with c3:
            st.metric("📹 Total Videos", format_number(int(stats.get("videoCount", 0))))
        with c4:
            avg_views = int(stats.get("viewCount", 0)) / max(int(stats.get("videoCount", 1)), 1)
            st.metric("📊 Avg Views/Video", format_number(int(avg_views)))

        st.divider()

        # Tabs for charts
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Views", "📈 Engagement", "📅 Frequency", "📈 Growth", "📋 Videos Table"
        ])

        with tab1:
            st.plotly_chart(create_views_chart(df), use_container_width=True)

        with tab2:
            st.plotly_chart(create_engagement_chart(df), use_container_width=True)

        with tab3:
            st.plotly_chart(create_frequency_chart(df), use_container_width=True)

        with tab4:
            st.plotly_chart(create_growth_chart(df), use_container_width=True)

        with tab5:
            # Videos table
            display_df = df.sort_values("published_at", ascending=False).copy()
            display_df["Published"] = display_df["published_at"].dt.strftime("%Y-%m-%d")
            display_df["Views"] = display_df["view_count"].apply(format_number)
            display_df["Likes"] = display_df["like_count"].apply(format_number)
            display_df["Comments"] = display_df["comment_count"].apply(format_number)
            display_df["Engagement %"] = display_df["engagement_rate"].apply(lambda x: f"{x:.2f}%")
            display_df["Duration"] = display_df["duration_str"]
            display_df["Link"] = display_df["video_id"].apply(lambda x: f"https://youtu.be/{x}")

            # Add clickable title
            display_df["Title"] = display_df.apply(
                lambda row: f'<a href="https://youtu.be/{row["video_id"]}" target="_blank">{row["title"]}</a>', axis=1
            )

            st.markdown(
                display_df[["Title", "Published", "Views", "Likes", "Comments", "Engagement %", "Duration"]]
                .to_html(escape=False, index=False),
                unsafe_allow_html=True
            )

            # Download button
            csv = display_df[["title", "published_at", "view_count", "like_count", "comment_count", "engagement_rate", "duration_str"]].to_csv(index=False)
            st.download_button(
                "📥 Download as CSV",
                csv,
                file_name=f"{snippet.get('customUrl', 'channel')}_analysis.csv",
                mime="text/csv"
            )

    else:
        # Empty state
        st.markdown("""
        <div style="text-align: center; padding: 3rem; color: #6c757d;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">📊</div>
            <h3>Ready to Analyze</h3>
            <p>Enter your YouTube Data API key and a channel handle to get started.</p>
            <p>Or click <strong>Load Demo</strong> to see sample visualizations instantly.</p>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()