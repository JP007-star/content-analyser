# Content Analyser 🔱

**JP Cinematic Universe Toolkit** — Unified Streamlit dashboard for YouTube channel analysis + content optimization with AI skills.

## 🎯 Two Analyzers in One

| Analyzer | Purpose | Best For |
|----------|---------|----------|
| **📊 YouTube Channel Analyzer** | Fetch & visualize channel stats via YouTube Data API | Competitor research, growth tracking, audience insights |
| **🎯 YouTube Analyzer (Skills & Tools)** | Hook scoring, title linting, retention analysis, viral research, script writing | Content creation, SEO optimization, retention improvement |

---

## ✨ Features

### 📊 YouTube Channel Analyzer (API-based)
- **Channel Overview**: Subscribers, total views, video count, avg views/video
- **Interactive Charts**: Views/video, engagement rate, upload frequency, cumulative growth
- **Video Table**: Sortable, searchable, with CSV export
- **Demo Mode**: Test instantly without API key
- **Cached API Calls**: 5-min TTL, no rate limit issues

### 🎯 YouTube Analyzer (Skills & Tools) — *New!*
| Tool | Purpose | Input |
|------|---------|-------|
| **Hook Scorer** | Score first 15s against 21 formulas | Hook text |
| **Title + Thumbnail Linter** | Check duplication, truncation, missing numbers | Title + thumb desc |
| **Chapter Generator** | Validated YouTube chapters (0:00 start, ≥3, ≥10s) | SRT/VTT/JSON |
| **Retention Analyzer** | Hook leak, cliffs, slide + transcript context | Studio CSV |
| **Edit Decision List** | Dead air, filler words, repeat takes | Transcript |
| **Viral Research** | Rank outliers by channel-relative performance | Collected JSON |
| **SEO Optimizer** | Description, tags, hashtags for niche | Topic + niche |
| **Script Writer** | Beat-by-beat script with [ON SCREEN] cues | Topic + format |
| **Channel Audit** | THE single biggest fix from titles + retention | 10 titles + CSVs |
| **Content Planner** | Weekly/monthly calendar sized to capacity | Videos/week |
| **Comment Analyzer** | Sentiment, FAQ extraction, reply drafts | Comment thread |

---

## 🚀 Quick Start (Local)

```bash
# 1. Navigate to project
cd content-analyser

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run (choose one):
# Main app (both analyzers)
streamlit run main_app.py

# Channel analyzer only
streamlit run youtube_analyzer_streamlit.py

# Skills & tools only
streamlit run youtube_analyzer_app.py

# Or use launcher:
# Windows: double-click run_app.bat
# PowerShell: .\run_app.ps1
```

Open **http://localhost:8501** → Select analyzer in sidebar.

---

## 🔑 API Setup (For Channel Analyzer)

### YouTube Data API v3
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project → **Enable APIs** → Search "YouTube Data API v3" → Enable
3. **Credentials** → Create Credentials → **API Key**
4. Copy key (starts with `AIzaSy...`)
5. Paste in app sidebar

> **Note:** YouTube Analyzer (Skills & Tools) works **without API keys** — uses local Python tools and your voice profile.

---

## 🌐 Deploy to Streamlit Cloud (Free)

### Option 1: GitHub + Streamlit Cloud (Recommended)

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Content Analyser: Channel API + Skills Tools"
   git branch -M main
   git remote add origin https://github.com/JP007-star/content-analyser.git
   git push -u origin main
   ```

2. **Deploy:**
   - Go to [share.streamlit.io](https://share.streamlit.io/)
   - Sign in with GitHub
   - Click **"New app"**
   - Repository: `JP007-star/content-analyser`
   - Branch: `main`
   - Main file path: `main_app.py`
   - Click **Deploy!**

3. **Add Secrets** (for API keys):
   - Streamlit Cloud dashboard → App → **Settings** → **Secrets**
   ```toml
   YOUTUBE_API_KEY = "your_key_here"
   ```

### Option 2: Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "main_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
docker build -t content-analyser .
docker run -p 8501:8501 content-analyser
```

---

## 📁 Project Structure

```
content-analyser/
├── main_app.py                      # Main entry (both analyzers)
├── youtube_analyzer_streamlit.py    # Channel Analyzer (API)
├── youtube_analyzer_app.py          # Skills & Tools Analyzer
├── content_creator_analyzer.py      # Original multi-platform analyzer
├── requirements.txt                 # Python dependencies
├── .streamlit/
│   └── config.toml                 # Streamlit config
├── .claude/
│   ├── youtube/
│   │   ├── voice.md                # JP Cinematic Universe voice profile
│   │   ├── QUICKSTART.md           # Daily workflow guide
│   │   └── python-tools/           # 6 standalone tools
│   │       ├── hookscore.py
│   │       ├── title.py
│   │       ├── chapters.py
│   │       ├── retention.py
│   │       ├── deadair.py
│   │       └── swipe.py
│   └── skills/                     # 11 Claude Code skills
│       ├── yt-script/
│       ├── yt-package/
│       ├── yt-edit/
│       ├── yt-retention/
│       ├── yt-shorts/
│       ├── yt-viral/
│       ├── yt-seo/
│       ├── yt-chapters/
│       ├── yt-comment/
│       ├── yt-plan/
│       └── yt-audit/
└── README.md
```

---

## 🎬 Workflow: From Instagram Reel → YouTube Short

```
1. Instagram Reel posted (@trishul.stories)
       │
       ▼
2. Hook Scorer: Score your IG caption first line
       │
       ▼
3. Title + Thumb Linter: Optimize YT title/thumbnail pair
       │
       ▼
4. SEO Optimizer: Generate tags, description, hashtags
       │
       ▼
5. Script Writer: Beat-by-beat script with visual cues
       │
       ▼
6. Cross-post via GitHub Action or local script
       │
       ▼
7. After publish → Retention Analyzer (Studio CSV)
       │
       ▼
8. Weekly → Channel Audit (THE one fix)
```

---

## 🎯 Voice Profiles (Per Channel)

| Channel | Voice File | Niche |
|---------|------------|-------|
| JP Cinematic Universe | `.claude/youtube/voice.md` | Tech cinema, Trishul Stories |
| Java Prasad | `.claude/youtube/java-prasad-voice.md` | Java education, interviews |
| JP Pipeline | `.claude/youtube/jp-pipeline-voice.md` | DevOps, CI/CD, automation |

Create/edit voice profiles in the app sidebar → "Voice Profile" expander.

---

## 🛠 Tech Stack

- **Streamlit** — Web app framework
- **Plotly** — Interactive charts (Channel Analyzer)
- **Pandas** — Data manipulation
- **Requests** — YouTube Data API calls
- **Claude Code Skills** — 11 specialized YouTube skills
- **Custom Python Tools** — 6 standalone analyzers (no deps)

---

## 📄 License

MIT License — feel free to use, modify, and deploy.

---

## 🤝 Contributing

1. Fork the repo
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

---

**Built for JP Cinematic Universe — Where Code Meets Cinema** 🔱