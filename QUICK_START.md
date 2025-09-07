



# ChronoStories Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Option 1: Automated Setup (Recommended)

**Windows:**
```cmd
git clone https://github.com/Ashutoshchoudhary3/AniStory.git
cd AniStory
install.bat
```

**Linux/macOS:**
```bash
git clone https://github.com/Ashutoshchoudhary3/AniStory.git
cd AniStory
chmod +x install.sh
./install.sh
```

### Option 2: Manual Setup

1. **Clone and setup:**
```bash
git clone https://github.com/Ashutoshchoudhary3/AniStory.git
cd AniStory

# Windows
py -m venv venv
venv\Scripts\activate

# Linux/macOS
python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
playwright install
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. **Initialize database:**
```bash
# Windows
py -c "from app import create_app, db; app = create_app(); with app.app_context(): db.create_all()"

# Linux/macOS
python -c "from app import create_app, db; app = create_app(); with app.app_context(): db.create_all()"
```

4. **Start the app:**
```bash
# Windows
py app.py

# Linux/macOS
python app.py
```

## 🔑 Get Your API Keys

### Required (Free)
1. **Gemini API** - For AI image generation
   - Visit: https://makersuite.google.com/app/apikey
   - Sign in with Google account
   - Copy your API key

2. **GNews API** - For news ingestion
   - Visit: https://gnews.io/
   - Sign up for free account
   - Get your API key from dashboard

### Optional (Premium)
3. **OpenAI API** - Alternative AI provider
4. **Anthropic API** - Claude AI access

## 🎯 First Steps

### 1. Test the API
```bash
# Check if app is running
curl http://localhost:40268/api/health

# Get all stories
curl http://localhost:40268/api/stories
```

### 2. Create Your First Story
```bash
# Generate a story (requires login first)
curl -X POST http://localhost:40268/api/generate-story \
  -H "Content-Type: application/json" \
  -d '{
    "source_url": "https://example.com/news/ai-breakthrough",
    "category": "technology",
    "generate_images": true
  }'
```

### 3. Monitor Progress
```bash
# Check task status
curl http://localhost:40268/api/story-status/TASK_ID_HERE
```

## 📱 Access the Web Interface

1. **Homepage:** http://localhost:40268
2. **Login:** http://localhost:40268/auth/login
3. **Dashboard:** http://localhost:40268/dashboard
4. **API Docs:** http://localhost:40268/api (when available)

## 🎨 Customize Your Experience

### Change Image Style
Edit `.env` file:
```bash
GEMINI_IMAGE_MODEL=gemini-2.5-flash-image-preview
DEFAULT_AI_PROVIDER=gemini
```

### Modify Story Settings
```bash
MAX_STORY_LENGTH=500
MIN_STORY_LENGTH=100
STORIES_PER_BATCH=3
```

### Configure Scraping
```bash
MAX_SCRAPE_THREADS=5
SCRAPING_DELAY=2
```

## 🔧 Common Commands

### Daily Operations
```bash
# Start the app
python app.py

# Check logs
tail -f logs/app.log

# Restart with debug mode
FLASK_DEBUG=1 python app.py
```

### Database Management
```bash
# Backup database
cp instance/chronostories.db backup_$(date +%Y%m%d).db

# Reset database (WARNING: deletes all data)
rm instance/chronostories.db
python -c "from app import create_app, db; app = create_app(); with app.app_context(): db.create_all()"
```

### Troubleshooting
```bash
# Check Python version
python --version

# Verify dependencies
pip list | grep -E "(Flask|SQLAlchemy|google-generativeai)"

# Test database connection
python -c "from app import create_app, db; app = create_app(); with app.app_context(): print('DB connected:', db.engine.execute('SELECT 1').fetchone())"
```

## 🆘 Quick Fixes

### "Task not found" Error
1. Check task ID is correct
2. Verify database is initialized
3. Check Flask is running on port 40268

### 404 API Errors
1. Check SERVER_NAME in config.py matches your port
2. Verify blueprints are registered in app/__init__.py
3. Ensure all imports are present

### Database Connection Failed
1. Check instance/ directory exists
2. Verify database file permissions
3. Reinitialize database

### Images Not Generating
1. Verify Gemini API key is valid
2. Check image generation logs
3. Ensure image directories exist

## 📈 Next Steps

### After Successful Setup
1. **Configure API keys** in `.env` file
2. **Test story generation** with sample topics
3. **Customize anime prompts** for your brand
4. **Set up automated scraping** schedules
5. **Monitor analytics** to optimize content

### Advanced Features
- Set up Redis for background tasks
- Configure email notifications
- Integrate with social media
- Set up monitoring dashboards
- Deploy to production server

## 🎉 Success Indicators

✅ **App is working if:**
- Homepage loads at http://localhost:40268
- API health check returns success
- You can login/create account
- Story generation starts successfully
- Task status endpoint returns data

✅ **Story generation works if:**
- Task ID is created when you submit
- Task status shows progress
- Final story appears in database
- Images are generated successfully

## 🚀 Need Help?

1. **Check troubleshooting guide:** `TROUBLESHOOTING.md`
2. **Review API docs:** `API_DOCUMENTATION.md`
3. **Check GitHub issues:** https://github.com/Ashutoshchoudhary3/AniStory/issues
4. **Run diagnostic commands** in troubleshooting guide

## 📚 Learn More

- **Full README:** `README.md`
- **API Documentation:** `API_DOCUMENTATION.md`
- **Troubleshooting:** `TROUBLESHOOTING.md`
- **Setup Scripts:** `setup.py`, `install.sh`, `install.bat`

---

**🎨 Happy storytelling with ChronoStories!** 

Your AI-powered news story engine is ready to create amazing anime-style content! 🗞️✨




