"""
Content Creator Analyzer — Streamlit App
Supports YouTube (Data API v3) and Instagram (Graph API)
Run: streamlit run content_creator_analyzer.py
"""

import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
import time
import json

# ============ CONFIG ============
st.set_page_config(
    page_title="Content Creator Analyzer",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header { font-size: 2.5rem; font-weight: 700; margin-bottom: 0.3rem; }
    .platform-badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; margin-right: 8px; }
    .youtube-badge { background: #ffebe9; color: #cc0000; }
    .instagram-badge { background: #f3e5f5; color: #c13584; }
    .demo-badge { background: #fff3cd; color: #856404; }
    .metric-card { background: white; padding: 1.5rem; border-radius: 12px; border: 1px solid #e0e4eb; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }
    .stTabs [data-baseweb="tab"] { border-radius: 8px; padding: 8px 16px; }
    .api-status { padding: 8px 12px; border-radius: 8px; font-size: 0.85rem; font-weight: 500; }
    .api-connected { background: #e8f5e9; color: #2e7d32; }
    .api-disconnected { background: #ffebee; color: #c62828; }
    .video-thumb { width: 120px; height: 68px; object-fit: cover; border-radius: 8px; }
    .post-thumb { width: 100px; height: 100px; object-fit: cover; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# ============ CONSTANTS ============
YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"
INSTAGRAM_API_BASE = "https://graph.facebook.com/v19.0"
DEFAULT_YOUTUBE = "@java-prasad"
DEFAULT_INSTAGRAM = ""

# ============ SESSION STATE INIT ============
# Initialize all session state keys
for key, default in [
    ("yt_data", {"channel": None, "videos": [], "loaded": False}),
    ("ig_data", {"profile": None, "posts": [], "loaded": False}),
    ("yt_demo", False),
    ("ig_demo", False),
    ("active_platform", "YouTube"),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ============ UTILITY FUNCTIONS ============
def format_number(num: int) -> str:
    if num >= 1_000_000_000: return f"{num / 1_000_000_000:.1f}B".replace(".0", "")
    if num >= 1_000_000: return f"{num / 1_000_000:.1f}M".replace(".0", "")
    if num >= 1_000: return f"{num / 1_000:.1f}K".replace(".0", "")
    return f"{num:,}"

def format_date(date_str: str, fmt: str = "%b %d, %Y") -> str:
    try: return pd.to_datetime(date_str).strftime(fmt)
    except: return "—"

def parse_iso_duration(iso: str) -> str:
    import re
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso)
    if not m: return "—"
    h, m, s = int(m.group(1) or 0), int(m.group(2) or 0), int(m.group(3) or 0)
    return f"{h}:{m:02d}:{s:02d}" if h > 0 else f"{m}:{s:02d}"

def safe_get(d: dict, *keys, default=None):
    for k in keys:
        if isinstance(d, dict): d = d.get(k, default)
        else: return default
    return d if d is not None else default

# ============ YOUTUBE API ============
@st.cache_data(ttl=300, show_spinner=False)
def yt_resolve_channel_id(api_key: str, channel_input: str) -> Optional[str]:
    clean = channel_input.strip().replace("@", "")
    if clean.startswith("UC") and len(clean) == 24: return clean
    # forHandle
    resp = requests.get(f"{YOUTUBE_API_BASE}/channels", params={"part": "id", "forHandle": clean, "key": api_key}, timeout=10)
    if resp.ok and resp.json().get("items"): return resp.json()["items"][0]["id"]
    # search fallback
    resp = requests.get(f"{YOUTUBE_API_BASE}/search", params={"part": "snippet", "type": "channel", "q": clean, "maxResults": 1, "key": api_key}, timeout=10)
    if resp.ok and resp.json().get("items"): return resp.json()["items"][0]["snippet"]["channelId"]
    return None

@st.cache_data(ttl=300, show_spinner=False)
def yt_fetch_channel(api_key: str, channel_id: str) -> Optional[Dict]:
    resp = requests.get(f"{YOUTUBE_API_BASE}/channels", params={"part": "snippet,statistics,contentDetails,brandingSettings", "id": channel_id, "key": api_key}, timeout=10)
    if resp.ok and resp.json().get("items"): return resp.json()["items"][0]
    return None

@st.cache_data(ttl=300, show_spinner=False)
def yt_fetch_videos(api_key: str, channel_id: str, max_results: int = 20) -> List[Dict]:
    # Get uploads playlist
    resp = requests.get(f"{YOUTUBE_API_BASE}/channels", params={"part": "contentDetails", "id": channel_id, "key": api_key}, timeout=10)
    if not resp.ok: return []
    uploads_id = resp.json()["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    # Get playlist items
    resp = requests.get(f"{YOUTUBE_API_BASE}/playlistItems", params={"part": "snippet,contentDetails", "playlistId": uploads_id, "maxResults": max_results, "key": api_key}, timeout=10)
    if not resp.ok: return []
    video_ids = [item["contentDetails"]["videoId"] for item in resp.json().get("items", [])]
    if not video_ids: return []
    # Get video details
    resp = requests.get(f"{YOUTUBE_API_BASE}/videos", params={"part": "snippet,statistics,contentDetails", "id": ",".join(video_ids), "key": api_key}, timeout=10)
    if not resp.ok: return []
    videos = []
    for item in resp.json().get("items", []):
        stats = item.get("statistics", {})
        videos.append({
            "id": item["id"], "title": item["snippet"]["title"], "published_at": item["snippet"]["publishedAt"],
            "thumbnail": item["snippet"]["thumbnails"].get("medium", {}).get("url", ""),
            "views": int(stats.get("viewCount", 0)), "likes": int(stats.get("likeCount", 0)),
            "comments": int(stats.get("commentCount", 0)), "duration": item["contentDetails"]["duration"],
            "url": f"https://youtu.be/{item['id']}"
        })
    return videos

# ============ INSTAGRAM API ============
@st.cache_data(ttl=300, show_spinner=False)
def ig_fetch_profile(access_token: str, user_id: str = "me") -> Optional[Dict]:
    """Fetch Instagram Business/Creator profile."""
    fields = "id,username,account_type,media_count,followers_count,follows_count,profile_picture_url,biography,website"
    resp = requests.get(f"{INSTAGRAM_API_BASE}/{user_id}", params={"fields": fields, "access_token": access_token}, timeout=10)
    if resp.ok: return resp.json()
    return None

@st.cache_data(ttl=300, show_spinner=False)
def ig_fetch_posts(access_token: str, user_id: str = "me", limit: int = 20) -> List[Dict]:
    """Fetch recent Instagram posts/media."""
    fields = "id,caption,media_type,media_url,permalink,timestamp,like_count,comments_count,thumbnail_url"
    resp = requests.get(f"{INSTAGRAM_API_BASE}/{user_id}/media", params={"fields": fields, "limit": limit, "access_token": access_token}, timeout=10)
    if not resp.ok: return []
    data = resp.json()
    posts = []
    for item in data.get("data", []):
        posts.append({
            "id": item["id"], "caption": item.get("caption", "")[:100], "type": item["media_type"],
            "media_url": item.get("media_url", ""), "thumbnail": item.get("thumbnail_url", item.get("media_url", "")),
            "permalink": item.get("permalink", ""), "timestamp": item["timestamp"],
            "likes": item.get("like_count", 0), "comments": item.get("comments_count", 0),
            "url": item.get("permalink", "")
        })
    # Handle pagination
    while "paging" in data and "next" in data["paging"] and len(posts) < limit:
        resp = requests.get(data["paging"]["next"], timeout=10)
        if not resp.ok: break
        data = resp.json()
        for item in data.get("data", []):
            posts.append({
                "id": item["id"], "caption": item.get("caption", "")[:100], "type": item["media_type"],
                "media_url": item.get("media_url", ""), "thumbnail": item.get("thumbnail_url", item.get("media_url", "")),
                "permalink": item.get("permalink", ""), "timestamp": item["timestamp"],
                "likes": item.get("like_count", 0), "comments": item.get("comments_count", 0),
                "url": item.get("permalink", "")
            })
    return posts[:limit]

@st.cache_data(ttl=300, show_spinner=False)
def ig_fetch_insights(access_token: str, user_id: str = "me", metric: str = "followers_count") -> Optional[Dict]:
    """Fetch Instagram insights (requires Business/Creator account)."""
    resp = requests.get(f"{INSTAGRAM_API_BASE}/{user_id}/insights", params={"metric": metric, "period": "day", "access_token": access_token}, timeout=10)
    if resp.ok: return resp.json()
    return None

# ============ DEMO DATA ============
def get_demo_youtube() -> tuple:
    channel = {
        "snippet": {"title": "Java Prasad", "customUrl": "@java-prasad", "publishedAt": "2020-03-15T00:00:00Z", "thumbnails": {"medium": {"url": ""}}},
        "statistics": {"subscriberCount": "127000", "viewCount": "8920000", "videoCount": "85"},
        "id": "UCdemo12345678901234567890"
    }
    videos = [
        {"id": "demo1", "title": "Java 21 Features You Need to Know", "published_at": "2024-01-15T10:00:00Z", "views": 45200, "likes": 2100, "comments": 180, "duration": "PT12M34S", "url": "https://youtu.be/demo1"},
        {"id": "demo2", "title": "Spring Boot 3.2 Tutorial", "published_at": "2024-01-08T10:00:00Z", "views": 38700, "likes": 1850, "comments": 145, "duration": "PT18M22S", "url": "https://youtu.be/demo2"},
        {"id": "demo3", "title": "Java vs Kotlin in 2024", "published_at": "2024-01-01T10:00:00Z", "views": 52100, "likes": 2800, "comments": 320, "duration": "PT15M45S", "url": "https://youtu.be/demo3"},
        {"id": "demo4", "title": "Building REST APIs with Spring Boot", "published_at": "2023-12-25T10:00:00Z", "views": 31400, "likes": 1420, "comments": 98, "duration": "PT22M10S", "url": "https://youtu.be/demo4"},
        {"id": "demo5", "title": "Java Virtual Threads Deep Dive", "published_at": "2023-12-18T10:00:00Z", "views": 41800, "likes": 2200, "comments": 210, "duration": "PT16M55S", "url": "https://youtu.be/demo5"},
        {"id": "demo6", "title": "Maven vs Gradle 2024", "published_at": "2023-12-11T10:00:00Z", "views": 28900, "likes": 1200, "comments": 85, "duration": "PT14M30S", "url": "https://youtu.be/demo6"},
        {"id": "demo7", "title": "Testing Spring Boot Applications", "published_at": "2023-12-04T10:00:00Z", "views": 24500, "likes": 1100, "comments": 72, "duration": "PT19M15S", "url": "https://youtu.be/demo7"},
        {"id": "demo8", "title": "Java Records Pattern Matching", "published_at": "2023-11-27T10:00:00Z", "views": 33200, "likes": 1650, "comments": 130, "duration": "PT13M40S", "url": "https://youtu.be/demo8"},
        {"id": "demo9", "title": "Dockerizing Spring Boot Apps", "published_at": "2023-11-20T10:00:00Z", "views": 29800, "likes": 1380, "comments": 95, "duration": "PT20M05S", "url": "https://youtu.be/demo9"},
        {"id": "demo10", "title": "Java 21 String Templates Preview", "published_at": "2023-11-13T10:00:00Z", "views": 36700, "likes": 1720, "comments": 110, "duration": "PT11M50S", "url": "https://youtu.be/demo10"},
    ]
    return channel, videos

def get_demo_instagram() -> tuple:
    profile = {
        "id": "17841400000000000", "username": "java_prasad", "account_type": "BUSINESS",
        "media_count": 156, "followers_count": 45200, "follows_count": 234,
        "profile_picture_url": "", "biography": "Java Developer | Spring Boot | Cloud Native | Teaching tech", "website": "https://github.com/java-prasad"
    }
    posts = [
        {"id": "ig1", "caption": "Just released: Java 21 deep dive! 🚀 #java #programming", "type": "IMAGE", "media_url": "", "thumbnail": "", "timestamp": "2024-01-15T10:00:00Z", "likes": 2340, "comments": 89, "url": "https://instagram.com/p/demo1"},
        {"id": "ig2", "caption": "Spring Boot 3.2 tips that save hours ⚡", "type": "CAROUSEL_ALBUM", "media_url": "", "thumbnail": "", "timestamp": "2024-01-10T10:00:00Z", "likes": 1890, "comments": 67, "url": "https://instagram.com/p/demo2"},
        {"id": "ig3", "caption": "Java vs Kotlin - my honest take 🤔", "type": "VIDEO", "media_url": "", "thumbnail": "", "timestamp": "2024-01-05T10:00:00Z", "likes": 3120, "comments": 145, "url": "https://instagram.com/p/demo3"},
        {"id": "ig4", "caption": "Virtual threads are a game changer 🧵", "type": "REELS", "media_url": "", "thumbnail": "", "timestamp": "2023-12-28T10:00:00Z", "likes": 4560, "comments": 203, "url": "https://instagram.com/p/demo4"},
        {"id": "ig5", "caption": "Docker + Spring Boot = 🐳☕", "type": "IMAGE", "media_url": "", "thumbnail": "", "timestamp": "2023-12-20T10:00:00Z", "likes": 1670, "comments": 54, "url": "https://instagram.com/p/demo5"},
        {"id": "ig6", "caption": "Testing strategies that actually work ✅", "type": "CAROUSEL_ALBUM", "media_url": "", "thumbnail": "", "timestamp": "2023-12-15T10:00:00Z", "likes": 1340, "comments": 42, "url": "https://instagram.com/p/demo6"},
        {"id": "ig7", "caption": "Records + Pattern Matching = clean code ✨", "type": "IMAGE", "media_url": "", "thumbnail": "", "timestamp": "2023-12-10T10:00:00Z", "likes": 1890, "comments": 61, "url": "https://instagram.com/p/demo7"},
        {"id": "ig8", "caption": "Maven vs Gradle 2024 edition ⚔️", "type": "REELS", "media_url": "", "thumbnail": "", "timestamp": "2023-12-05T10:00:00Z", "likes": 2780, "comments": 112, "url": "https://instagram.com/p/demo8"},
        {"id": "ig9", "caption": "String templates in Java 21 🎯", "type": "IMAGE", "media_url": "", "thumbnail": "", "timestamp": "2023-11-28T10:00:00Z", "likes": 1560, "comments": 38, "url": "https://instagram.com/p/demo9"},
        {"id": "ig10", "caption": "Behind the scenes: recording a tech tutorial 🎥", "type": "VIDEO", "media_url": "", "thumbnail": "", "timestamp": "2023-11-20T10:00:00Z", "likes": 2010, "comments": 76, "url": "https://instagram.com/p/demo10"},
    ]
    return profile, posts

# ============ CHART FUNCTIONS ============
def yt_views_chart(df: pd.DataFrame) -> go.Figure:
    df = df.sort_values("published_at")
    df["date_label"] = pd.to_datetime(df["published_at"]).dt.strftime("%b %d")
    fig = go.Figure(go.Bar(x=df["date_label"], y=df["views"], name="Views", marker_color="#cc0000", marker_line_color="#ff0000", marker_line_width=1.5, hovertemplate="<b>%{x}</b><br>Views: %{y:,}<br>%{customdata}<extra></extra>", customdata=df["title"]))
    fig.update_layout(title="Views per Video", template="plotly_white", height=350, margin=dict(l=40, r=20, t=50, b=40))
    return fig

def yt_engagement_chart(df: pd.DataFrame) -> go.Figure:
    df = df.sort_values("published_at")
    df["engagement"] = ((df["likes"] + df["comments"]) / df["views"] * 100).round(2)
    df["date_label"] = pd.to_datetime(df["published_at"]).dt.strftime("%b %d")
    fig = go.Figure(go.Scatter(x=df["date_label"], y=df["engagement"], mode="lines+markers", line=dict(color="#cc0000", width=3), marker=dict(size=8, color="#cc0000"), fill="tozeroy", fillcolor="rgba(204,0,0,0.1)", hovertemplate="<b>%{x}</b><br>Engagement: %{y:.2f}%<extra></extra>"))
    fig.update_layout(title="Engagement Rate", template="plotly_white", height=350, margin=dict(l=40, r=20, t=50, b=40), yaxis_title="Engagement %")
    return fig

def yt_frequency_chart(df: pd.DataFrame) -> go.Figure:
    df["month"] = pd.to_datetime(df["published_at"]).dt.to_period("M")
    monthly = df.groupby("month").size().reset_index(name="count")
    all_months = pd.period_range(end=pd.Timestamp.now(), periods=12, freq="M")
    merged = pd.DataFrame({"month": all_months}).merge(monthly, on="month", how="left").fillna(0)
    merged["count"] = merged["count"].astype(int)
    merged["label"] = merged["month"].dt.strftime("%b %Y")
    fig = go.Figure(go.Bar(x=merged["label"], y=merged["count"], marker_color="#cc0000"))
    fig.update_layout(title="Upload Frequency (12 Months)", template="plotly_white", height=350, margin=dict(l=40, r=20, t=50, b=40))
    return fig

def yt_growth_chart(df: pd.DataFrame) -> go.Figure:
    df = df.sort_values("published_at")
    df["cum_views"] = df["views"].cumsum()
    df["date_label"] = pd.to_datetime(df["published_at"]).dt.strftime("%b %d")
    fig = go.Figure(go.Scatter(x=df["date_label"], y=df["cum_views"], mode="lines", line=dict(color="#cc0000", width=3), fill="tozeroy", fillcolor="rgba(204,0,0,0.15)", hovertemplate="<b>%{x}</b><br>Total: %{y:,}<extra></extra>"))
    fig.update_layout(title="Cumulative Views Growth", template="plotly_white", height=350, margin=dict(l=40, r=20, t=50, b=40))
    return fig

def ig_engagement_chart(df: pd.DataFrame) -> go.Figure:
    df = df.sort_values("timestamp")
    df["engagement"] = ((df["likes"] + df["comments"]) / (df["likes"] + df["comments"] + 1) * 100).round(2)  # approx
    df["date_label"] = pd.to_datetime(df["timestamp"]).dt.strftime("%b %d")
    fig = go.Figure(go.Bar(x=df["date_label"], y=df["likes"], name="Likes", marker_color="#c13584", hovertemplate="<b>%{x}</b><br>Likes: %{y:,}<extra></extra>"))
    fig.add_trace(go.Bar(x=df["date_label"], y=df["comments"], name="Comments", marker_color="#e91e63", hovertemplate="<b>%{x}</b><br>Comments: %{y:,}<extra></extra>"))
    fig.update_layout(title="Likes & Comments per Post", barmode="group", template="plotly_white", height=350, margin=dict(l=40, r=20, t=50, b=40))
    return fig

def ig_type_distribution(df: pd.DataFrame) -> go.Figure:
    type_counts = df["type"].value_counts()
    fig = go.Figure(go.Pie(labels=type_counts.index, values=type_counts.values, hole=0.4, marker_colors=["#c13584", "#e91e63", "#f06292", "#ad1457"]))
    fig.update_layout(title="Content Type Distribution", template="plotly_white", height=350, margin=dict(l=20, r=20, t=50, b=20))
    return fig

def ig_frequency_chart(df: pd.DataFrame) -> go.Figure:
    df["month"] = pd.to_datetime(df["timestamp"]).dt.to_period("M")
    monthly = df.groupby("month").size().reset_index(name="count")
    all_months = pd.period_range(end=pd.Timestamp.now(), periods=12, freq="M")
    merged = pd.DataFrame({"month": all_months}).merge(monthly, on="month", how="left").fillna(0)
    merged["count"] = merged["count"].astype(int)
    merged["label"] = merged["month"].dt.strftime("%b %Y")
    fig = go.Figure(go.Bar(x=merged["label"], y=merged["count"], marker_color="#c13584"))
    fig.update_layout(title="Posts per Month (12 Months)", template="plotly_white", height=350, margin=dict(l=40, r=20, t=50, b=40))
    return fig

def ig_growth_chart(df: pd.DataFrame) -> go.Figure:
    df = df.sort_values("timestamp")
    df["cum_likes"] = df["likes"].cumsum()
    df["date_label"] = pd.to_datetime(df["timestamp"]).dt.strftime("%b %d")
    fig = go.Figure(go.Scatter(x=df["date_label"], y=df["cum_likes"], mode="lines", line=dict(color="#c13584", width=3), fill="tozeroy", fillcolor="rgba(193,53,132,0.15)", hovertemplate="<b>%{x}</b><br>Total Likes: %{y:,}<extra></extra>"))
    fig.update_layout(title="Cumulative Likes Growth", template="plotly_white", height=350, margin=dict(l=40, r=20, t=50, b=40))
    return fig

# ============ RENDER FUNCTIONS ============
def render_youtube_dashboard():
    data = st.session_state.yt_data
    if not data["loaded"] or not data["channel"]:
        return

    channel = data["channel"]
    videos = data["videos"]
    df = pd.DataFrame(videos)
    if df.empty: return
    df["published_at"] = pd.to_datetime(df["published_at"])
    df["engagement"] = ((df["likes"] + df["comments"]) / df["views"] * 100).round(2)
    df["duration_str"] = df["duration"].apply(parse_iso_duration)

    snippet, stats = channel["snippet"], channel["statistics"]

    # Header
    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown(f'<span class="platform-badge youtube-badge">YouTube</span> **{snippet.get("title", "Unknown")}**', unsafe_allow_html=True)
        st.caption(f"Channel ID: {channel['id']} | Joined: {format_date(snippet['publishedAt'], '%B %d, %Y')}")
    with c2:
        if st.session_state["yt_demo"]: st.info("🎯 Demo Mode")

    # Metrics
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric("👥 Subscribers", format_number(int(stats.get("subscriberCount", 0))))
    with m2: st.metric("👁️ Total Views", format_number(int(stats.get("viewCount", 0))))
    with m3: st.metric("📹 Videos", format_number(int(stats.get("videoCount", 0))))
    with m4:
        avg = int(stats.get("viewCount", 0)) / max(int(stats.get("videoCount", 1)), 1)
        st.metric("📊 Avg Views", format_number(int(avg)))

    st.divider()

    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Views", "📈 Engagement", "📅 Frequency", "📈 Growth", "📋 Videos"])

    with tab1: st.plotly_chart(yt_views_chart(df), use_container_width=True)
    with tab2: st.plotly_chart(yt_engagement_chart(df), use_container_width=True)
    with tab3: st.plotly_chart(yt_frequency_chart(df), use_container_width=True)
    with tab4: st.plotly_chart(yt_growth_chart(df), use_container_width=True)
    with tab5:
        display = df.sort_values("published_at", ascending=False).copy()
        display["Published"] = display["published_at"].dt.strftime("%Y-%m-%d")
        display["Views"] = display["views"].apply(format_number)
        display["Likes"] = display["likes"].apply(format_number)
        display["Comments"] = display["comments"].apply(format_number)
        display["Engagement"] = display["engagement"].apply(lambda x: f"{x:.2f}%")
        display["Duration"] = display["duration_str"]
        display["Title"] = display.apply(lambda r: f'<a href="{r["url"]}" target="_blank">{r["title"]}</a>', axis=1)
        st.markdown(display[["Title", "Published", "Views", "Likes", "Comments", "Engagement", "Duration"]].to_html(escape=False, index=False), unsafe_allow_html=True)
        csv = display[["title", "published_at", "views", "likes", "comments", "engagement", "duration_str"]].to_csv(index=False)
        st.download_button("📥 Download CSV", csv, f"{snippet.get('customUrl', 'channel')}_youtube.csv", "text/csv")

def render_instagram_dashboard():
    data = st.session_state.ig_data
    if not data["loaded"] or not data["profile"]:
        return

    profile = data["profile"]
    posts = data["posts"]
    df = pd.DataFrame(posts)
    if df.empty: return
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["engagement"] = ((df["likes"] + df["comments"]) / (df["likes"] + df["comments"] + 1) * 100).round(2)

    # Header
    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown(f'<span class="platform-badge instagram-badge">Instagram</span> **@{profile.get("username", "unknown")}**', unsafe_allow_html=True)
        st.caption(f"Type: {profile.get('account_type', 'UNKNOWN')} | Bio: {profile.get('biography', '—')[:80]}")
    with c2:
        if st.session_state["ig_demo"]: st.info("🎯 Demo Mode")

    # Metrics
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric("👥 Followers", format_number(profile.get("followers_count", 0)))
    with m2: st.metric("📸 Posts", format_number(profile.get("media_count", 0)))
    with m3:
        total_eng = df["likes"].sum() + df["comments"].sum()
        avg_eng = total_eng / max(len(df), 1)
        st.metric("❤️ Avg Engagement", format_number(int(avg_eng)))
    with m4: st.metric("📊 Engagement Rate", f"{(total_eng / max(profile.get('followers_count', 1), 1) * 100):.2f}%")

    st.divider()

    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["❤️ Engagement", "📊 Types", "📅 Frequency", "📈 Growth", "📋 Posts"])

    with tab1: st.plotly_chart(ig_engagement_chart(df), use_container_width=True)
    with tab2: st.plotly_chart(ig_type_distribution(df), use_container_width=True)
    with tab3: st.plotly_chart(ig_frequency_chart(df), use_container_width=True)
    with tab4: st.plotly_chart(ig_growth_chart(df), use_container_width=True)
    with tab5:
        display = df.sort_values("timestamp", ascending=False).copy()
        display["Posted"] = display["timestamp"].dt.strftime("%Y-%m-%d")
        display["Type"] = display["type"]
        display["Caption"] = display["caption"].apply(lambda x: x[:60] + "..." if len(x) > 60 else x)
        display["Likes"] = display["likes"].apply(format_number)
        display["Comments"] = display["comments"].apply(format_number)
        display["Engagement"] = display["engagement"].apply(lambda x: f"{x:.2f}%")
        display["Link"] = display.apply(lambda r: f'<a href="{r["url"]}" target="_blank">View</a>', axis=1)
        st.markdown(display[["Type", "Posted", "Caption", "Likes", "Comments", "Engagement", "Link"]].to_html(escape=False, index=False), unsafe_allow_html=True)
        csv = display[["type", "timestamp", "caption", "likes", "comments", "engagement"]].to_csv(index=False)
        st.download_button("📥 Download CSV", csv, f"{profile.get('username', 'instagram')}_instagram.csv", "text/csv")

# ============ MAIN APP ============
def main():
    # Header
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown('<div class="main-header">🎬 Content Creator Analyzer</div>', unsafe_allow_html=True)
        st.markdown('<span style="color: #666;">Analyze YouTube & Instagram channels in one place</span>', unsafe_allow_html=True)
    with col2:
        st.markdown('<span class="demo-badge">Demo Mode Available</span>', unsafe_allow_html=True)

    st.divider()

    # Platform selector
    platform = st.radio("Platform", ["YouTube", "Instagram"], horizontal=True, key="platform_selector")
    st.session_state.active_platform = platform

    # Sidebar
    with st.sidebar:
        st.header(f"⚙️ {platform} Configuration")

        if platform == "YouTube":
            api_key = st.text_input("YouTube Data API v3 Key", type="password", placeholder="AIzaSy...", key="yt_api_key")
            channel_input = st.text_input("Channel Handle/ID", value=DEFAULT_YOUTUBE, placeholder="@handle or UC...", key="yt_channel")
            max_videos = st.slider("Max Videos", 5, 50, 20, 5, key="yt_max")

            st.divider()
            c1, c2 = st.columns(2)
            with c1:
                if st.button("🔍 Analyze YouTube", type="primary", use_container_width=True, key="yt_analyze"):
                    if not api_key:
                        st.error("Enter API key"); st.stop()
                    with st.spinner("Fetching YouTube data..."):
                        channel_id = yt_resolve_channel_id(api_key, channel_input)
                        if not channel_id: st.error("Channel not found"); st.stop()
                        channel = yt_fetch_channel(api_key, channel_id)
                        if not channel: st.error("Failed to fetch channel"); st.stop()
                        videos = yt_fetch_videos(api_key, channel_id, max_videos)
                        if not videos: st.warning("No videos found"); st.stop()
                        st.session_state.yt_data = {"channel": channel, "videos": videos, "loaded": True}
                        st.session_state["yt_demo"] = False
                        st.success(f"✅ {len(videos)} videos loaded!")
                        st.rerun()
            with c2:
                if st.button("🎯 Load YouTube Demo", use_container_width=True, key="yt_demo_btn"):
                    with st.spinner("Loading demo..."):
                        time.sleep(0.3)
                        channel, videos = get_demo_youtube()
                        st.session_state.yt_data = {"channel": channel, "videos": videos, "loaded": True}
                        st.session_state["yt_demo"] = True
                        st.success("✅ Demo loaded!")
                        st.rerun()

            with st.expander("🔑 Get YouTube API Key"):
                st.markdown("""
                1. [Google Cloud Console](https://console.cloud.google.com/)
                2. Enable **YouTube Data API v3**
                3. Credentials → Create → **API Key**
                4. Copy key (`AIzaSy...`)
                """)

        else:  # Instagram
            access_token = st.text_input("Instagram Access Token", type="password", placeholder="EAA...", key="ig_token", help="Long-lived token from Facebook Graph API")
            user_id = st.text_input("Instagram User ID (optional)", placeholder="17841400000000000 or 'me'", key="ig_user", value="me")
            max_posts = st.slider("Max Posts", 5, 50, 20, 5, key="ig_max")

            st.divider()
            c1, c2 = st.columns(2)
            with c1:
                if st.button("🔍 Analyze Instagram", type="primary", use_container_width=True, key="ig_analyze"):
                    if not access_token:
                        st.error("Enter access token"); st.stop()
                    with st.spinner("Fetching Instagram data..."):
                        profile = ig_fetch_profile(access_token, user_id)
                        if not profile: st.error("Failed to fetch profile. Check token & permissions."); st.stop()
                        posts = ig_fetch_posts(access_token, user_id, max_posts)
                        st.session_state.ig_data = {"profile": profile, "posts": posts, "loaded": True}
                        st.session_state["ig_demo"] = False
                        st.success(f"✅ {len(posts)} posts loaded!")
                        st.rerun()
            with c2:
                if st.button("🎯 Load Instagram Demo", use_container_width=True, key="ig_demo_btn"):
                    with st.spinner("Loading demo..."):
                        time.sleep(0.3)
                        profile, posts = get_demo_instagram()
                        st.session_state.ig_data = {"profile": profile, "posts": posts, "loaded": True}
                        st.session_state["ig_demo"] = True
                        st.success("✅ Demo loaded!")
                        st.rerun()

            with st.expander("🔑 Get Instagram Access Token"):
                st.markdown("""
                **Requirements:** Instagram Business/Creator account + Facebook Page

                1. [Meta for Developers](https://developers.facebook.com/)
                2. Create App → **Business** type
                3. Add **Instagram Basic Display** or **Instagram Graph API**
                4. Get **User Token** → Extend to **Long-lived token** (60 days)
                5. Required permissions: `instagram_graph_user_profile`, `instagram_graph_user_media`

                *Or use a token generator tool for testing*
                """)

    # Render Dashboard
    if platform == "YouTube":
        if st.session_state.yt_data["loaded"]:
            render_youtube_dashboard()
        else:
            st.markdown("""
            <div style="text-align:center;padding:3rem;color:#666;">
                <div style="font-size:4rem;">📺</div>
                <h3>YouTube Analysis Ready</h3>
                <p>Enter API key + channel handle, or click <b>Load YouTube Demo</b></p>
            </div>
            """, unsafe_allow_html=True)
    else:
        if st.session_state.ig_data["loaded"]:
            render_instagram_dashboard()
        else:
            st.markdown("""
            <div style="text-align:center;padding:3rem;color:#666;">
                <div style="font-size:4rem;">📸</div>
                <h3>Instagram Analysis Ready</h3>
                <p>Enter Access Token + User ID, or click <b>Load Instagram Demo</b></p>
                <p><small>Requires Business/Creator account connected to Facebook Page</small></p>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()