# Content Creator Analyzer 🎬

A unified Streamlit dashboard for analyzing **YouTube** and **Instagram** channels. Built for content creators who manage multiple platforms.

## Features

| Platform | Metrics | Visualizations |
|----------|---------|----------------|
| **YouTube** | Subscribers, Views, Videos, Avg Views | Views/Video, Engagement Rate, Upload Frequency, Cumulative Growth |
| **Instagram** | Followers, Posts, Avg Engagement, Engagement Rate | Likes/Comments, Content Types, Post Frequency, Cumulative Likes |

- 🔄 **Switch platforms** with one click
- 📊 **Interactive Plotly charts** (zoom, hover, pan)
- 📥 **Export to CSV** for further analysis
- 🎯 **Demo mode** — test instantly without API keys
- ⚡ **Cached API calls** (5 min TTL) — no rate limit issues
- 🌐 **Deploy to Streamlit Cloud** in minutes

---

## Quick Start (Local)

```bash
# 1. Clone / navigate to project
cd youtube-analyzer

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
streamlit run content_creator_analyzer.py
```

Open `http://localhost:8501` — click **"Load YouTube Demo"** or **"Load Instagram Demo"** to see it work instantly.

---

## API Setup (For Real Data)

### YouTube Data API v3
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project → **Enable APIs** → Search "YouTube Data API v3" → Enable
3. **Credentials** → Create Credentials → **API Key**
4. Copy key (starts with `AIzaSy...`)
5. Paste in app sidebar

### Instagram Graph API
> Requires **Instagram Business/Creator account** linked to a **Facebook Page**

1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Create App → **Business** type
3. Add Product → **Instagram Graph API**
4. **Basic Display** → Generate **User Access Token**
5. **Token Debugger** → Extend to **Long-lived token** (60 days)
6. Required permissions: `instagram_graph_user_profile`, `instagram_graph_user_media`
7. Paste token + User ID (or use `me`) in app sidebar

---

## Deploy to Streamlit Cloud (Free)

### Option 1: GitHub + Streamlit Cloud (Recommended)

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Content Creator Analyzer"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/content-creator-analyzer.git
   git push -u origin main
   ```

2. **Deploy:**
   - Go to [share.streamlit.io](https://share.streamlit.io/)
   - Sign in with GitHub
   - Click **"New app"**
   - Repository: `your-username/content-creator-analyzer`
   - Branch: `main`
   - Main file path: `content_creator_analyzer.py`
   - Click **Deploy!**

3. **Add secrets** (for API keys in production):
   - In Streamlit Cloud dashboard → App → **Settings** → **Secrets**
   - Add:
   ```toml
   YOUTUBE_API_KEY = "your_key_here"
   INSTAGRAM_ACCESS_TOKEN = "your_token_here"
   INSTAGRAM_USER_ID = "your_user_id"
   ```
   - In code, read via `st.secrets["YOUTUBE_API_KEY"]`

### Option 2: Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "content_creator_analyzer.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
docker build -t content-creator-analyzer .
docker run -p 8501:8501 content-creator-analyzer
```

---

## Project Structure

```
youtube-analyzer/
├── content_creator_analyzer.py   # Main Streamlit app
├── requirements.txt              # Python dependencies
├── .streamlit/
│   └── config.toml              # Streamlit configuration
├── README.md                     # This file
└── .gitignore                   # Git ignore rules
```

---

## Screenshots

### YouTube Dashboard
- Channel overview cards (Subs, Views, Videos, Avg)
- 4 interactive charts + searchable video table
- CSV export

### Instagram Dashboard
- Profile overview (Followers, Posts, Engagement)
- Content type breakdown (Reels, Images, Carousels)
- Engagement trends + growth charts
- CSV export

---

## Tech Stack

- **Streamlit** — Web app framework
- **Plotly** — Interactive charts
- **Pandas** — Data manipulation
- **Requests** — API calls
- **YouTube Data API v3** — YouTube data
- **Instagram Graph API** — Instagram data

---

## License

MIT License — feel free to use, modify, and deploy.

---

## Contributing

1. Fork the repo
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

---

**Built for content creators who want data-driven insights across platforms.** 🚀