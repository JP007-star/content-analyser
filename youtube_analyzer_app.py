"""
YouTube Analyzer — Streamlit Dashboard
All-in-one toolkit for JP Cinematic Universe (and other channels)
Wraps: hookscore, title lint, chapters, retention, deadair, swipe, yt-skills
"""

import streamlit as st
import subprocess
import json
import os
import tempfile
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional
import time

# ──────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────
try:
    st.set_page_config(
        page_title="YouTube Analyzer | JP Cinematic Universe",
        page_icon="🔱",
        layout="wide",
        initial_sidebar_state="expanded"
    )
except Exception:
    pass

# Paths - robust for both local and Streamlit Cloud (exec)
def _get_base_dir() -> Path:
    """Get base directory reliably even when run via exec()."""
    # Try __file__ first (normal import)
    try:
        return Path(__file__).parent
    except NameError:
        pass
    # Fallback: use current working directory
    return Path.cwd()

BASE_DIR = _get_base_dir()
TOOLS_DIR = BASE_DIR / ".claude" / "youtube" / "python-tools"
VOICE_DIR = BASE_DIR / ".claude" / "youtube"
SKILLS_DIR = BASE_DIR / ".claude" / "skills"

# Verify tools exist, fallback to common locations
if not TOOLS_DIR.exists():
    # Try Streamlit Cloud mount path
    cloud_tools = Path("/mount/src/content-analyser/.claude/youtube/python-tools")
    if cloud_tools.exists():
        TOOLS_DIR = cloud_tools
        VOICE_DIR = Path("/mount/src/content-analyser/.claude/youtube")
        SKILLS_DIR = Path("/mount/src/content-analyser/.claude/skills")
        BASE_DIR = Path("/mount/src/content-analyser")

# Channel configs
CHANNELS = {
    "jp_cinematic": {
        "name": "JP Cinematic Universe",
        "handle": "@jpcinematicuniverse",
        "voice_file": VOICE_DIR / "voice.md",
        "niche": "tech cinema",
        "language": "ta+en",
        "category": "24"
    },
    "java_prasad": {
        "name": "Java Prasad",
        "handle": "@java-prasad",
        "voice_file": VOICE_DIR / "java-prasad-voice.md",
        "niche": "java education",
        "language": "ta+en",
        "category": "27"
    },
    "jp_pipeline": {
        "name": "JP Pipeline",
        "handle": "@jp-pipeline",
        "voice_file": VOICE_DIR / "jp-pipeline-voice.md",
        "niche": "devops automation",
        "language": "en",
        "category": "28"
    },
    "jp_news_360": {
        "name": "JP News 360",
        "handle": "@jp-news-360",
        "voice_file": VOICE_DIR / "jp-news-360-voice.md",
        "niche": "TTD, IPOs, cinema, cricket, trending",
        "language": "ta+en",
        "category": "25"
    }
}

# ──────────────────────────────────────────────
# HELPER FUNCTIONS
# ──────────────────────────────────────────────
def run_tool(script: str, args: List[str]) -> Dict[str, Any]:
    """Run a Python tool and return parsed output."""
    try:
        result = subprocess.run(
            [sys.executable, str(TOOLS_DIR / script)] + args,
            capture_output=True,
            text=True,
            timeout=60
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "stdout": "", "stderr": "Timeout", "returncode": -1}
    except Exception as e:
        return {"success": False, "stdout": "", "stderr": str(e), "returncode": -1}


def run_hookscore(hook: str) -> Dict:
    """Score a single hook."""
    return run_tool("hookscore.py", ["--hook", hook])


def run_hookscore_batch(hooks: List[str]) -> Dict:
    """Score multiple hooks from a temp file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write('\n'.join(hooks))
        tmp_path = f.name
    try:
        return run_tool("hookscore.py", [tmp_path])
    finally:
        os.unlink(tmp_path)


def run_title_lint(title: str, thumb: str) -> Dict:
    """Lint title + thumbnail pair."""
    return run_tool("title.py", ["--title", title, "--thumb", thumb])


def run_chapters(transcript_path: str) -> Dict:
    """Generate chapters from transcript."""
    return run_tool("chapters.py", [transcript_path])


def run_retention(csv_path: str, transcript_path: Optional[str] = None) -> Dict:
    """Analyze retention CSV."""
    args = [csv_path]
    if transcript_path:
        args.extend(["--transcript", transcript_path])
    return run_tool("retention.py", args)


def run_deadair(transcript_path: str, floor: float = 0.35) -> Dict:
    """Generate edit decision list."""
    return run_tool("deadair.py", [transcript_path, "--floor", str(floor)])


def run_swipe(json_path: str, min_mult: float = 2.0) -> Dict:
    """Rank viral outliers."""
    return run_tool("swipe.py", [json_path, "--min", str(min_mult)])


def load_voice_profile(channel_key: str) -> str:
    """Load voice profile for a channel."""
    voice_file = CHANNELS[channel_key]["voice_file"]
    if voice_file.exists():
        return voice_file.read_text(encoding="utf-8")
    return "Voice profile not found. Create at: " + str(voice_file)


def save_uploaded_file(uploaded_file, suffix: str) -> str:
    """Save uploaded file to temp location."""
    if hasattr(uploaded_file, "seek"):
        uploaded_file.seek(0)
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as f:
        f.write(uploaded_file.read())
        return f.name


# ──────────────────────────────────────────────
# UI COMPONENTS
# ──────────────────────────────────────────────
def render_header():
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #0a0f1a 0%, #1a1f3a 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #00f3ff33;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #1a1f3a;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #00f3ff22;
    }
    .hook-score { font-family: monospace; }
    .workable { color: #00ff88; }
    .weak { color: #ff6b6b; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="main-header">
        <h1 style="margin:0; color:#00f3ff;">🔱 YouTube Analyzer</h1>
        <p style="margin:0.5rem 0 0; color:#8892b0;">JP Cinematic Universe • Trishul Stories • All Channels</p>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    with st.sidebar:
        st.markdown("### 🎬 Channel")
        channel_key = st.selectbox(
            "Active Channel",
            options=list(CHANNELS.keys()),
            format_func=lambda k: CHANNELS[k]["name"]
        )
        channel = CHANNELS[channel_key]

        st.markdown("---")
        st.markdown("### 📊 Quick Stats")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Niche", channel["niche"])
            st.metric("Category", channel["category"])
        with col2:
            st.metric("Language", channel["language"])
            st.metric("Handle", channel["handle"])

        st.markdown("---")
        st.markdown("### 🛠 Tools Status")
        tools = ["hookscore.py", "title.py", "chapters.py", "retention.py", "deadair.py", "swipe.py"]
        for tool in tools:
            exists = (TOOLS_DIR / tool).exists()
            st.write(f"{'✅' if exists else '❌'} {tool}")

        st.markdown("---")
        st.markdown("### 🎯 Voice Profile")
        with st.expander("View / Edit Voice"):
            voice_content = load_voice_profile(channel_key)
            st.text_area("Voice Profile", voice_content, height=300, key=f"voice_{channel_key}")

    return channel_key, channel


# ──────────────────────────────────────────────
# TABS
# ──────────────────────────────────────────────
def tab_hook_scorer(channel):
    st.markdown("## 🎯 Hook Scorer")
    st.caption("Score your first 15 seconds against 21 formulas. Weakest link determines the verdict.")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### Single Hook")
        hook_input = st.text_area(
            "Paste your hook (first 15 seconds / first sentence):",
            placeholder="You think HashMap is O(1). Until your hashCode clusters everything in bucket 3 — and your P99 spikes 400%. Visual proof inside.",
            height=100
        )
        if st.button("Score Hook", type="primary", use_container_width=True):
            if hook_input.strip():
                with st.spinner("Scoring..."):
                    result = run_hookscore(hook_input.strip())
                render_hook_result(result, hook_input)
            else:
                st.warning("Enter a hook first.")

    with col2:
        st.markdown("### Batch Score (Compare)")
        st.caption("One hook per line")
        batch_input = st.text_area(
            "Multiple hooks:",
            placeholder="Hook 1\nHook 2\nHook 3",
            height=150
        )
        if st.button("Score All", use_container_width=True):
            hooks = [h.strip() for h in batch_input.strip().split('\n') if h.strip()]
            if hooks:
                with st.spinner(f"Scoring {len(hooks)} hooks..."):
                    result = run_hookscore_batch(hooks)
                render_batch_results(result)
            else:
                st.warning("Enter at least one hook.")

    # Formula reference
    with st.expander("📚 21 Hook Formulas Reference"):
        hooks_path = TOOLS_DIR / "hooks.json"
        if not hooks_path.exists():
            hooks_path = BASE_DIR / ".claude" / "skills" / "yt-script" / "hooks.json"
        if hooks_path.exists():
            hooks_json = hooks_path.read_text(encoding="utf-8")
            hooks_data = json.loads(hooks_json)["hooks"]
            df = pd.DataFrame([{
                "Formula": h["name"],
                "Shape": h["shape"],
                "Example": h["example"][:80] + "...",
                "Fails When": h["fails_when"][:60] + "..."
            } for h in hooks_data])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Formula reference file hooks.json not found.")


def render_hook_result(result: Dict, hook: str):
    if not result["success"]:
        st.error(f"Error: {result['stderr']}")
        return

    output = result["stdout"]
    st.code(output, language=None)

    # Parse verdict
    if "WORKABLE" in output:
        st.success("✅ **WORKABLE** — Good to shoot")
    elif "WEAK" in output:
        st.warning("⚠️ **WEAK** — Revise before shooting")
    else:
        st.info("ℹ️ Check output above")

    # Extract metrics
    lines = output.split('\n')
    for line in lines:
        if any(k in line for k in ["SPECIFICITY", "ADDRESS", "STAKES", "CURIOSITY", "BREVITY"]):
            parts = line.split()
            if len(parts) >= 3:
                metric = parts[0]
                score = parts[1]
                bar = parts[2] if len(parts) > 2 else ""
                color = "workable" if int(score) >= 60 else "weak"
                st.markdown(f"<span class='hook-score {color}'>{metric}: {score} {bar}</span>", unsafe_allow_html=True)


def render_batch_results(result: Dict):
    if not result["success"]:
        st.error(f"Error: {result['stderr']}")
        return

    output = result["stdout"]
    st.code(output, language=None)

    # Parse winner
    if "winner:" in output:
        for line in output.split('\n'):
            if line.strip().startswith("winner:"):
                st.success(f"🏆 **Winner:** {line.replace('winner:', '').strip()}")


def tab_title_thumbnail(channel):
    st.markdown("## 📦 Title + Thumbnail Linter")
    st.caption("The pairing is the unit. Checks: duplication, mobile truncation, missing numbers/names.")

    col1, col2 = st.columns(2)
    with col1:
        title = st.text_input(
            "Title:",
            placeholder="HashMap Visualized: The Memory Map",
            help="YouTube truncates at ~60 chars (desktop) / ~40 chars (mobile)"
        )
    with col2:
        thumb = st.text_input(
            "Thumbnail Text/Concept:",
            placeholder="Dark bg, glowing hash buckets, memory addresses, Tamil overlay",
            help="Describe what the thumbnail SHOWS (not what the title says)"
        )

    if st.button("Lint Pair", type="primary", use_container_width=True):
        if title and thumb:
            with st.spinner("Analyzing..."):
                result = run_title_lint(title, thumb)
            render_title_result(result, title)
        else:
            st.warning("Enter both title and thumbnail description.")

    # Preview
    if title:
        st.markdown("### 📱 Feed Preview")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**Desktop (60 chars)**")
            st.code(title[:60] + ("…" if len(title) > 60 else ""))
        with col2:
            st.markdown("**Mobile (40 chars)**")
            st.code(title[:40] + ("…" if len(title) > 40 else ""))
        with col3:
            st.markdown("**Thumbnail Text**")
            st.code(thumb[:30] + ("…" if len(thumb) > 30 else ""))


def render_title_result(result: Dict, title: str):
    if not result["success"]:
        st.error(f"Error: {result['stderr']}")
        return

    output = result["stdout"]
    st.code(output, language=None)

    # Parse score
    for line in output.split('\n'):
        if "score" in line and "/" in line:
            score_part = line.split("score")[1].strip()
            try:
                score = int(score_part.split("/")[0])
                if score >= 70:
                    st.success(f"✅ **Score: {score}/100** — Strong packaging")
                elif score >= 50:
                    st.warning(f"⚠️ **Score: {score}/100** — Needs work")
                else:
                    st.error(f"❌ **Score: {score}/100** — Major issues")
            except:
                pass


def tab_chapters(channel):
    st.markdown("## 📑 Chapter Generator")
    st.caption("Upload SRT/VTT/Whisper JSON → Get validated YouTube chapters (0:00 start, ≥3 chapters, ≥10s each)")

    uploaded = st.file_uploader(
        "Upload Transcript",
        type=["srt", "vtt", "json", "txt"],
        help="SRT/VTT from YouTube Studio, Whisper JSON, or plain text with timestamps"
    )

    if uploaded:
        if st.button("Generate Chapters", type="primary"):
            tmp_path = save_uploaded_file(uploaded, f".{uploaded.name.split('.')[-1]}")
            try:
                with st.spinner("Generating..."):
                    result = run_chapters(tmp_path)
                if result["success"]:
                    st.success("✅ Chapters generated!")
                    st.code(result["stdout"], language=None)
                    st.caption("⚠️ Retitle every line before pasting. These are topic words, not your words.")
                else:
                    st.error(f"Error: {result['stderr']}")
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)

    # Format guide
    with st.expander("📋 Supported Formats"):
        st.markdown("""
        **SRT (YouTube Studio export):**
        ```
        1
        00:00:00,000 --> 00:00:05,000
        Welcome to Trishul Stories

        2
        00:00:05,000 --> 00:01:30,000
        What happens when you put a key in HashMap?
        ```

        **Plain text with timestamps:**
        ```
        0:00 Introduction
        1:30 What is HashMap
        3:45 Internal Structure
        ```

        **Whisper JSON:** Direct output from `whisper --output_format json`
        """)


def tab_retention(channel):
    st.markdown("## 📉 Retention Analyzer")
    st.caption("Upload YouTube Studio audience-retention CSV → Find HOOK LEAK, CLIFFS, SLIDE + what was said at each drop")

    col1, col2 = st.columns(2)
    with col1:
        retention_file = st.file_uploader(
            "Retention CSV (required)",
            type=["csv"],
            help="YouTube Studio → Analytics → Engagement → Audience Retention → Download"
        )
    with col2:
        transcript_file = st.file_uploader(
            "Transcript (optional, for context)",
            type=["srt", "vtt", "txt"],
            help="Matches drops to what was being said"
        )

    if retention_file:
        if st.button("Analyze Retention", type="primary"):
            retention_path = save_uploaded_file(retention_file, ".csv")
            transcript_path = None
            if transcript_file:
                transcript_path = save_uploaded_file(transcript_file, f".{transcript_file.name.split('.')[-1]}")
            try:
                with st.spinner("Analyzing retention curve..."):
                    result = run_retention(retention_path, transcript_path)
                if result["success"]:
                    st.success("✅ Analysis complete!")
                    render_retention_output(result["stdout"])
                else:
                    st.error(f"Error: {result['stderr']}")
            finally:
                if os.path.exists(retention_path):
                    os.unlink(retention_path)
                if transcript_path and os.path.exists(transcript_path):
                    os.unlink(transcript_path)


def render_retention_output(output: str):
    st.code(output, language=None)

    # Visualize if we can parse
    if "HOOK LEAK" in output or "CLIFFS" in output or "SLIDE" in output:
        st.markdown("### 📊 Summary")
        cols = st.columns(3)
        with cols[0]:
            if "HOOK LEAK" in output:
                st.metric("Hook Leak", "⚠️ Check output")
        with cols[1]:
            if "CLIFFS" in output:
                st.metric("Cliffs", "⚠️ Check output")
        with cols[2]:
            if "SLIDE" in output:
                st.metric("Slide Rate", "⚠️ Check output")


def tab_edit_decisions(channel):
    st.markdown("## ✂️ Edit Decision List (Dead Air / Filler / Repeats)")
    st.caption("Upload transcript → Get cuts list with timestamps. Apply in your editor.")

    uploaded = st.file_uploader(
        "Upload Transcript",
        type=["srt", "vtt", "json", "txt"],
        key="edit_transcript"
    )

    floor = st.slider(
        "Dead air floor (seconds)",
        0.1, 2.0, 0.35, 0.05,
        help="Gaps longer than this are flagged as DEAD"
    )

    if uploaded:
        if st.button("Generate EDL", type="primary"):
            tmp_path = save_uploaded_file(uploaded, f".{uploaded.name.split('.')[-1]}")
            try:
                with st.spinner("Finding cuts..."):
                    result = run_deadair(tmp_path, floor)
                if result["success"]:
                    st.success("✅ Edit decision list generated!")
                    render_edl_output(result["stdout"])
                else:
                    st.error(f"Error: {result['stderr']}")
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)


def render_edl_output(output: str):
    st.code(output, language=None)

    # Parse summary
    if "total" in output.lower() and "remove" in output.lower():
        for line in output.split('\n'):
            if any(k in line.lower() for k in ["total", "remove", "runtime", "land"]):
                st.info(line)


def tab_viral_research(channel):
    st.markdown("## 🔥 Viral Research (Swipe File)")
    st.caption("Collect competitor videos → Rank by multiple of channel's own median → Identify formulas")

    st.markdown("### Input Format (JSON)")
    st.code("""[
  {"channel": "Channel Name", "title": "Video Title", "views": 412000, "url": "https://...", "duration": 613},
  {"channel": "Another Channel", "title": "Another Title", "views": 150000, "url": "https://...", "duration": 420}
]""", language="json")

    uploaded = st.file_uploader("Upload collected.json", type=["json"])
    min_mult = st.slider("Minimum multiple of channel median", 1.0, 5.0, 2.0, 0.1)

    if uploaded:
        if st.button("Rank Outliers", type="primary"):
            tmp_path = save_uploaded_file(uploaded, ".json")
            try:
                with st.spinner("Ranking..."):
                    result = run_swipe(tmp_path, min_mult)
                if result["success"]:
                    st.success("✅ Viral outliers ranked!")
                    render_swipe_output(result["stdout"])
                else:
                    st.error(f"Error: {result['stderr']}")
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)

    # Manual entry
    with st.expander("➕ Manual Entry (add videos one by one)"):
        if "swipe_videos" not in st.session_state:
            st.session_state.swipe_videos = []

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            ch = st.text_input("Channel")
        with col2:
            title = st.text_input("Title")
        with col3:
            views = st.number_input("Views", min_value=0, step=1000)
        with col4:
            duration = st.number_input("Duration (sec)", min_value=0, step=30)

        if st.button("Add to List") and ch and title:
            st.session_state.swipe_videos.append({
                "channel": ch, "title": title, "views": views,
                "url": "", "duration": duration
            })
            st.rerun()

        if st.session_state.swipe_videos:
            st.dataframe(pd.DataFrame(st.session_state.swipe_videos), use_container_width=True)
            if st.button("Analyze This List", type="primary"):
                tmp_path = save_uploaded_file(
                    type('obj', (), {'read': lambda self: json.dumps(st.session_state.swipe_videos).encode()})(),
                    ".json"
                )
                try:
                    result = run_swipe(tmp_path, min_mult)
                    if result["success"]:
                        render_swipe_output(result["stdout"])
                finally:
                    os.unlink(tmp_path)


def render_swipe_output(output: str):
    st.code(output, language=None)
    st.caption("Videos ranked by (views / channel_median). Higher = more exceptional for that channel.")


def tab_seo(channel):
    st.markdown("## 🔍 SEO Optimizer")
    st.caption("Generate description, tags, and search-facing text for your niche")

    topic = st.text_input("Video Topic:", placeholder="HashMap internal structure visualized")
    niche = st.selectbox("Niche:", ["tech cinema", "java education", "devops automation", "tech storytelling", "custom"])
    if niche == "custom":
        niche = st.text_input("Custom Niche:")

    language = st.selectbox("Language:", ["ta+en", "en", "ta", "hi+en"])

    if st.button("Generate SEO", type="primary", use_container_width=True):
        if topic and niche:
            with st.spinner("Generating SEO..."):
                # This would call yt-seo skill, for now show template
                render_seo_template(topic, niche, language, channel)
        else:
            st.warning("Enter topic and niche.")


def render_seo_template(topic: str, niche: str, language: str, channel):
    st.markdown("### 📝 Generated SEO Package")

    # Description template
    desc = f"""{topic} — explained visually in under 60 seconds.

This is Trishul Stories: where code meets cinema. We break down {topic.lower()} with memory diagrams, CPU-level animation, and the one fix that prevents production outages.

🎬 **Series:** Trishul Stories
💡 **Key Insight:** The O(1) myth vs reality
🔧 **Fix:** initialCapacity prevents resize spikes
📚 **Learn:** HashMap internals for interviews

▶️ **Watch Next:** [Part 2: ConcurrentHashMap](link)
💻 **Code:** [GitHub Gist](link)
🔔 **Subscribe:** https://youtube.com/@{channel['handle'].lstrip('@')}"""

    st.markdown("**Description:**")
    st.text_area("", desc, height=200)

    # Tags
    base_tags = ["cinematiccoding", "trishulstories", "techcinema", "storytelling", "softwarecinema", "developerlife", "behindthecode", "techshorts", "jpcinematicuniverse", "cinematiccoding"]
    niche_tags = {
        "tech cinema": ["techcinema", "cinematictech", "visualprogramming"],
        "java education": ["java", "programming", "dsa", "interview", "hashmap", "collections"],
        "devops automation": ["devops", "cicd", "githubactions", "automation", "infrastructure"],
        "tech storytelling": ["techstory", "developerstory", "codingjourney", "behindthecode"]
    }
    all_tags = base_tags + niche_tags.get(niche, [])
    tags_str = ", ".join(all_tags[:50])  # YouTube limit

    st.markdown("**Tags (copy to YouTube):**")
    st.code(tags_str)

    # Hashtags
    hashtags = {
        "tech cinema": "#CinematicCoding #TrishulStories #TechCinema #JPUniverse",
        "java education": "#Java #DSA #InterviewPrep #Programming #HashMap",
        "devops automation": "#DevOps #CI/CD #GitHubActions #Automation",
        "tech storytelling": "#TechStory #DeveloperLife #CodingJourney"
    }
    st.markdown("**Hashtags (for Shorts/Community):**")
    st.code(hashtags.get(niche, "#CinematicCoding #TrishulStories #TechCinema"))


def tab_script_writer(channel):
    st.markdown("## ✍️ Script Writer (yt-script)")
    st.caption("Uses your voice profile. Generates 5 hooks, scores them, outputs beat-by-beat script with [ON SCREEN] cues.")

    topic = st.text_input("Topic:", placeholder="HashMap internal structure visualized")
    format_type = st.selectbox("Format:", ["shorts", "long-form", "educational", "story"])
    voice_style = st.selectbox("Voice:", ["cinematic", "educational", "technical", "storytelling"])

    if st.button("Generate Script", type="primary", use_container_width=True):
        if topic:
            with st.spinner("Writing script... (this calls the yt-script skill)"):
                st.info("🤖 This would invoke the `/yt-script` skill in Claude. For now, here's the template:")
                render_script_template(topic, format_type, voice_style, channel)
        else:
            st.warning("Enter a topic.")


def render_script_template(topic: str, fmt: str, voice: str, channel):
    st.markdown(f"""
    ### Generated Script Structure for: **{topic}**

    **Format:** {fmt} | **Voice:** {voice} | **Channel:** {channel['name']}

    ---

    #### HOOKS (5 options, scored via hookscore.py)
    1. [The Statistic] You think X is true. Until [specific number] proves otherwise. Visual proof inside.
    2. [Direct Address] If you do X, you are [specific risk] away from [consequence]. Here is what actually happens.
    3. [Reveal] I'm going to show you the exact [artifact] that [result]. On screen in 10 seconds.
    4. [Contrarian] Everyone says [advice]. I [tested/built] and [result]. Here is why.
    5. [Question] Why does [pain point] happen when [condition]? The answer is [mechanism].

    → **Run through hookscore.py** → Keep top 2

    ---

    #### TURN (0:15-0:45)
    One sentence: what this video does + start doing it.
    *No intro, no subscribe, no "before we start"*

    ---

    #### BODY (beats with [ON SCREEN] cues)
    Beat 1: [Concept] → [ON SCREEN: visual metaphor]
    Beat 2: [Mechanism] → [ON SCREEN: code animation]
    Beat 3: [Problem] → [ON SCREEN: failure visualization]
    Beat 4: [Solution] → [ON SCREEN: fix demonstration]

    ---

    #### PAYOFF
    Deliver what hook promised. Explicitly: "That is the [thing], link in description."

    ---

    #### CLOSE
    One ask. Not three.
    *Save this. Next interview asks X — you draw Y.*
    """)


def tab_audit(channel):
    st.markdown("## 🏥 Channel Audit")
    st.caption("Paste your last 10 video titles + upload retention CSVs → Get THE single biggest fix")

    st.warning("⚠️ Audit requires existing channel data. Best run after 10+ videos published.")

    titles_text = st.text_area(
        "Last 10 Video Titles (one per line):",
        placeholder="Title 1\nTitle 2\nTitle 3\n...",
        height=200
    )

    retention_files = st.file_uploader(
        "Retention CSVs (up to 3 recent videos):",
        type=["csv"],
        accept_multiple_files=True
    )

    if st.button("Run Audit", type="primary", use_container_width=True):
        if titles_text.strip():
            with st.spinner("Auditing..."):
                titles = [t.strip() for t in titles_text.strip().split('\n') if t.strip()]
                render_audit_results(titles, retention_files, channel)
        else:
            st.warning("Enter at least 5 video titles.")


def render_audit_results(titles: List[str], retention_files, channel):
    st.markdown("### 📋 Title Analysis")
    for i, title in enumerate(titles, 1):
        st.write(f"{i}. {title}")

    # Title shape analysis
    shapes = {}
    for title in titles:
        words = title.split()
        shape = f"{len(words)} words"
        if any(c.isdigit() for c in title):
            shape += " + number"
        if "?" in title:
            shape += " + question"
        if ":" in title:
            shape += " + colon"
        shapes[shape] = shapes.get(shape, 0) + 1

    st.markdown("**Title Shapes:**")
    for shape, count in sorted(shapes.items(), key=lambda x: -x[1]):
        st.write(f"  • {shape}: {count}")

    if len(set(shapes.keys())) == 1:
        st.error("🚨 **FORMAT PROBLEM:** All titles same shape. Vary: question, number, colon, statement.")
    elif max(shapes.values()) / len(titles) > 0.6:
        st.warning("⚠️ **Dominant shape** — mix it up.")

    # Hook analysis (would need transcripts)
    st.markdown("### 🎯 Hook Analysis")
    st.info("Provide first 15s transcripts of 3 recent videos for hook scoring.")

    # Consistency
    st.markdown("### 📅 Upload Consistency")
    st.info("Upload rhythm check: 6 videos in 1 week then nothing for a month = worse than 1/fortnight forever.")

    # The One Fix
    st.markdown("---")
    st.markdown("## 🎯 THE ONE FIX")
    st.markdown("""
    Based on typical new cinematic tech channels:

    **Biggest Fix:** **Hook specificity + visual proof in first 8 seconds**

    **Do This Week:**
    1. Reshoot hooks for next 3 videos using `hookscore.py` — target 65+ WORKABLE
    2. Add visual artifact (diagram/code/animation) by 0:10 in every video
    3. Cut channel intro / "hey guys" / subscribe pitch from first 30s

    **What's Working (Don't Break):**
    - Cinematic visual style distinct from tutorial channels
    - Tamil + English code-switching = unique audience lock-in
    - Trishul Stories series format = bingeable

    **Don't Do Yet:**
    - Long-form > 8 min (retention cliff at 3-4 min for new channels)
    - Multiple CTAs (one ask per video)
    - Talking head without visual > 2 seconds
    """)


def tab_content_planner(channel):
    st.markdown("## 📅 Content Planner (yt-plan)")
    st.caption("Plan a week/month of uploads sized to your actual capacity")

    capacity = st.slider("Videos per week you can ACTUALLY ship:", 1, 7, 3)
    horizon = st.selectbox("Planning horizon:", ["week", "month"])

    if st.button("Generate Plan", type="primary"):
        render_content_plan(capacity, horizon, channel)


def render_content_plan(capacity: int, horizon: str, channel):
    st.markdown(f"### 📅 {horizon.title()} Plan — {capacity} videos/week")

    series = {
        "jp_cinematic": ["Trishul Stories", "Cinematic Coding", "Interview Cinematics", "Bug of the Week"],
        "java_prasad": ["Java Deep Dive", "Interview Questions", "DSA Visualized", "Code Review"],
        "jp_pipeline": ["GitHub Actions Deep Dive", "CI/CD Patterns", "War Stories", "Tool Comparison"],
        "jp_news_360": ["TTD Darshan Updates", "IPO & Market Watch", "Cinema Reviews", "Trending News"]
    }

    channel_series = series.get(list(CHANNELS.keys())[list(CHANNELS.values()).index(channel)], ["Series 1", "Series 2", "Series 3"])

    import datetime
    start = datetime.date.today()

    if horizon == "week":
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        plan = []
        for i in range(capacity):
            day = days[i % 7]
            series_name = channel_series[i % len(channel_series)]
            plan.append({"Day": day, "Series": series_name, "Topic": f"[Topic for {series_name}]", "Status": "💡 Idea"})
        st.dataframe(pd.DataFrame(plan), use_container_width=True, hide_index=True)
    elif horizon == "month":
        days = ["Mon", "Wed", "Fri", "Sat", "Sun", "Tue", "Thu"]
        plan = []
        for week in range(1, 5):
            for i in range(capacity):
                day = days[i % 7]
                series_name = channel_series[(week * capacity + i) % len(channel_series)]
                plan.append({"Week": f"Week {week}", "Day": day, "Series": series_name, "Topic": f"[Week {week}: {series_name}]", "Status": "💡 Idea"})
        st.dataframe(pd.DataFrame(plan), use_container_width=True, hide_index=True)

    st.markdown("""
    **Capacity Rules:**
    - Be honest: 3 shorts/week ≠ 3 long-form/week
    - Batch: Record 3 hooks in one session
    - Buffer: Always have 1 finished video in reserve
    - Review: Sunday = audit last week, plan next week
    """)


def tab_comments(channel):
    st.markdown("## 💬 Comment Analyzer (yt-comment)")
    st.caption("Paste comment thread → Get sentiment, FAQ extraction, reply drafts in your voice")

    comments_text = st.text_area(
        "Paste Comments (one per line, or copy from YouTube):",
        placeholder="User1: Great explanation!\nUser2: Can you do ConcurrentHashMap next?\nUser3: The treeify threshold part was confusing\n...",
        height=200
    )

    if st.button("Analyze Comments", type="primary"):
        if comments_text.strip():
            render_comment_analysis(comments_text, channel)
        else:
            st.warning("Paste comments first.")


def render_comment_analysis(text: str, channel):
    lines = [l.strip() for l in text.split('\n') if l.strip()]

    # Simple analysis
    questions = [l for l in lines if '?' in l]
    praise = [l for l in lines if any(w in l.lower() for w in ['great', 'awesome', 'love', 'best', 'amazing', 'thank'])]
    confusion = [l for l in lines if any(w in l.lower() for w in ['confus', 'don\'t understand', 'unclear', 'what', 'how'])]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total", len(lines))
    with col2:
        st.metric("Questions", len(questions))
    with col3:
        st.metric("Confusion", len(confusion))

    if questions:
        st.markdown("### ❓ Questions (Content Ideas)")
        for q in questions[:10]:
            st.write(f"• {q}")

    if confusion:
        st.markdown("### 🤔 Confusion Points (Fix in Next Video)")
        for c in confusion[:5]:
            st.write(f"• {c}")

    # Reply drafts
    st.markdown("### ✍️ Reply Drafts (in your voice)")
    for q in questions[:3]:
        reply = f"Great question! Part 2 covering this drops [day]. The short answer: [one sentence]. Full breakdown in the next Trishul Stories. 🔱"
        st.code(reply)


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────
def main():
    render_header()
    channel_key, channel = render_sidebar()

    # Tabs
    tabs = st.tabs([
        "🎯 Hook Scorer",
        "📦 Title + Thumb",
        "📑 Chapters",
        "📉 Retention",
        "✂️ Edit Decisions",
        "🔥 Viral Research",
        "🔍 SEO",
        "✍️ Script Writer",
        "🏥 Audit",
        "📅 Planner",
        "💬 Comments"
    ])

    with tabs[0]:
        tab_hook_scorer(channel)
    with tabs[1]:
        tab_title_thumbnail(channel)
    with tabs[2]:
        tab_chapters(channel)
    with tabs[3]:
        tab_retention(channel)
    with tabs[4]:
        tab_edit_decisions(channel)
    with tabs[5]:
        tab_viral_research(channel)
    with tabs[6]:
        tab_seo(channel)
    with tabs[7]:
        tab_script_writer(channel)
    with tabs[8]:
        tab_audit(channel)
    with tabs[9]:
        tab_content_planner(channel)
    with tabs[10]:
        tab_comments(channel)

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align:center; color:#8892b0; padding:1rem;">
        🔱 JP Cinematic Universe YouTube Analyzer | Built with Streamlit + Claude Skills
        <br>
        <a href="https://github.com/Jakeschincariol/youtube-agent-skill" target="_blank">Source Skills</a> •
        <a href="https://youtube.com/@jpcinematicuniverse" target="_blank">Channel</a> •
        <a href="https://instagram.com/jcu.stories" target="_blank">Instagram</a>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()