# JP Cinematic Universe — YouTube Skills Quickstart

## 🎯 Skills Installed (in ~/.claude/skills/)
```
/yt-script      → Script writing with 21 hooks
/yt-package     → Title + thumbnail linting pair
/yt-edit        → Edit decision list from transcript
/yt-retention   → Drop-off moment analysis
/yt-shorts      → Extract Shorts from long-form
/yt-viral       → Niche outlier research (swipe.py)
/yt-seo         → Keywords, tags, descriptions
/yt-chapters    → Validated timestamps
/yt-comment     → Sentiment, FAQ extraction
/yt-plan        → Content calendar, series ideas
/yt-audit       → Channel health check
```

---

## 🚀 Daily Workflow for Cross-Posting

### 1. After Instagram Reel goes live
```bash
# In Claude:
/yt-shorts "https://instagram.com/reel/REEL_ID" --count=3 --voice=cinematic
```

### 2. Optimize title + thumbnail before upload
```bash
# In Claude:
/yt-package "Your draft title" "thumbnail concept description"
```

### 3. SEO for discoverability
```bash
# In Claude:
/yt-seo "Trishul Stories: HashMap visualization" --niche="tech cinema" --language="ta+en"
```

### 4. Weekly channel audit
```bash
# In Claude:
/yt-audit --channel=@jpcinematicuniverse --days=7
```

---

## 🐍 Python Tools (Standalone, No Deps)

```bash
cd ~/youtube-agent-skill  # or wherever you cloned it

# 1. Score your hook (1-100)
python hookscore.py "3 AM. Production down. One HashMap saved us."

# 2. Lint title + thumbnail together
python title.py "HashMap Visualized: The Memory Map" "Dark background, glowing hash buckets connecting to memory addresses, Tamil text overlay"

# 3. Generate edit decisions from transcript
python deadair.py transcript.txt

# 4. Create YouTube chapters
python chapters.py transcript.txt

# 5. Find exact retention drop-offs
python retention.py transcript.txt --threshold=10

# 6. Find viral outliers in your niche
python swipe.py --niche="tech storytelling" --limit=15
```

---

## 📝 Content Pipeline

```
Instagram Reel (@trishul.stories)
        │
        ▼
Download MP4 + caption
        │
        ▼
/yt-shorts → Extract 3 Short concepts
        │
        ▼
/yt-script → Write cinematic script for each
        │
        ▼
/yt-package → Optimize title + thumbnail
        │
        ▼
/yt-seo → Tags, description, hashtags
        │
        ▼
Upload to YouTube Shorts (@jpcinematicuniverse)
        │
        ▼
/yt-chapters → Add timestamps (if >60s)
        │
        ▼
/yt-comment → Analyze comments after 24h
```

---

## 🎬 For Your 3 Channels

| Channel | Voice File | Primary Skills |
|---------|------------|----------------|
| **JP Cinematic Universe** | `~/.claude/youtube/voice.md` ✅ | yt-shorts, yt-script, yt-package, yt-seo |
| **Java Prasad** | `~/.claude/youtube/java-prasad-voice.md` | yt-script, yt-chapters, yt-retention, yt-audit |
| **JP Pipeline** | `~/.claude/youtube/jp-pipeline-voice.md` | yt-script, yt-edit, yt-seo, yt-plan |

---

## 🔧 Create Voice Files for Other Channels

```bash
# Java Prasad (Education)
cat > ~/.claude/youtube/java-prasad-voice.md << 'EOF'
# Java Prasad — Voice Profile
## Channel Identity
- Name: Java Prasad
- Niche: Java education, interview prep, DSA
- Language: Tamil + English
- Tone: Encouraging mentor, clear explanations, interview-focused
## Hook Priority: Question → Data → Story → Visual
## Format: Tutorial with chapters, code-first, interview tips
EOF

# JP Pipeline (DevOps)
cat > ~/.claude/youtube/jp-pipeline-voice.md << 'EOF'
# JP Pipeline — Voice Profile
## Channel Identity
- Name: JP Pipeline
- Niche: DevOps, CI/CD, GitHub Actions, Infrastructure
- Language: English (technical)
- Tone: Senior engineer sharing battle scars, practical patterns
## Hook Priority: Data → Contrast → Story → Question
## Format: Technical deep-dive, copy-pasteable configs, war stories
EOF
```

---

## 📅 Automation Ideas

### GitHub Action: Auto-analyze new uploads
```yaml
# .github/workflows/analyze-upload.yml
on:
  workflow_run:
    workflows: ["Cross-post Instagram Reels → YouTube"]
    types: [completed]
jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: |
          # Get latest video ID from workflow
          # Run retention analysis
          # Post summary to Slack/Discord
```

### Local cron: Weekly viral research
```bash
# Add to crontab (run Mondays 9 AM)
0 9 * * 1 cd ~/youtube-agent-skill && python swipe.py --niche="tech cinema" --limit=10 >> ~/viral-report-$(date +\%Y\%m\%d).txt
```

---

## 🎯 Next Steps

1. **Test a skill**: In Claude, type `/yt-script "HashMap visualization" --format=shorts`
2. **Run hookscore** on your last 5 Instagram captions
3. **Create voice files** for Java Prasad & JP Pipeline
4. **Set up `/yt-audit`** as weekly habit

---

*Voice profile: ~/.claude/youtube/voice.md | Skills: ~/.claude/skills/yt-*