



# ChronoStories Troubleshooting Guide

## Quick Diagnostic Commands

Run these commands to quickly check system status:

```bash
# Check if Flask app is running
curl http://localhost:40268/api/health

# Check database connection
# Windows
py -c "from app import create_app, db; app = create_app(); with app.app_context(): print('Database connected:', db.engine.execute('SELECT 1').fetchone())"

# Linux/macOS
python -c "from app import create_app, db; app = create_app(); with app.app_context(): print('Database connected:', db.engine.execute('SELECT 1').fetchone())"

# Check Python version
# Windows
py --version

# Linux/macOS
python --version

# Check installed packages
pip list | grep -E "(Flask|SQLAlchemy|requests|google-generativeai)"
```

## Common Issues and Solutions

### 1. Flask App Won't Start

**Symptoms:**
- `py app.py` (Windows) or `python app.py` (Linux/macOS) fails with errors
- Port 40268 is not accessible
- Application crashes on startup

**Solutions:**

1. **Check Python version:**
```bash
# Windows
py --version  # Should be 3.8+

# Linux/macOS
python --version  # Should be 3.8+
```

2. **Verify virtual environment:**
```bash
# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

3. **Check for missing dependencies:**
```bash
pip install -r requirements.txt
```

4. **Check port availability:**
```bash
# Windows
netstat -ano | findstr :40268

# Linux/macOS
lsof -i :40268
```

5. **Check environment variables:**
```bash
# Verify .env file exists
cat .env

# Test configuration
# Windows
py -c "from config import Config; print('Config loaded successfully')"

# Linux/macOS
python -c "from config import Config; print('Config loaded successfully')"
```

### 2. Database Issues

**Symptoms:**
- "Task not found" errors
- Database connection failures
- Tables missing

**Solutions:**

1. **Initialize database manually:**
```python
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    print("Database initialized!")
```

2. **Check database location:**
```bash
# Find the actual database file
find . -name "*.db" -type f

# Check if database is in instance folder
ls -la instance/
```

3. **Recreate database (WARNING: This will delete all data):**
```bash
# Backup first
cp instance/chronostories.db instance/chronostories.db.backup

# Remove and recreate
rm instance/chronostories.db

# Windows
py -c "from app import create_app, db; app = create_app(); with app.app_context(): db.create_all()"

# Linux/macOS
python -c "from app import create_app, db; app = create_app(); with app.app_context(): db.create_all()"
```

4. **Check table structure:**
```python
# Windows
py -c "
from app import create_app, db
from app.models import User, Story, Trend
app = create_app()
with app.app_context():
    print('Users table exists:', db.engine.has_table('users'))
    print('Stories table exists:', db.engine.has_table('stories'))
    print('Trends table exists:', db.engine.has_table('trends'))
"

# Linux/macOS
python -c "
from app import create_app, db
from app.models import User, Story, Trend
app = create_app()
with app.app_context():
    print('Users table exists:', db.engine.has_table('users'))
    print('Stories table exists:', db.engine.has_table('stories'))
    print('Trends table exists:', db.engine.has_table('trends'))
"
```

### 3. API Endpoint 404 Errors

**Symptoms:**
- `/api/story-status/{task_id}` returns 404
- Other API endpoints return 404
- "Task not found" for existing tasks

**Solutions:**

1. **Check Flask server name configuration:**
```python
# In config.py, ensure SERVER_NAME matches your port
SERVER_NAME = 'localhost:40268'
```

2. **Verify blueprint registration:**
```python
# In app/__init__.py, check all blueprints are registered
from app.routes import api_bp, auth_bp, stories_bp, main_bp
app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(stories_bp, url_prefix='/stories')
app.register_blueprint(main_bp)
```

3. **Test route function directly:**
```python
# Windows
py -c "
from app import create_app
from app.routes import story_status
app = create_app()
with app.app_context():
    # Test the function directly
    result = story_status('task_20250907_130724_289')
    print('Function result:', result)
"

# Linux/macOS
python -c "
from app import create_app
from app.routes import story_status
app = create_app()
with app.app_context():
    # Test the function directly
    result = story_status('task_20250907_130724_289')
    print('Function result:', result)
"
```

4. **Check for missing imports:**
```python
# In app/routes.py, ensure all required imports are present
from functools import wraps  # For login_required decorator
```

### 4. Authentication Issues

**Symptoms:**
- Login fails
- Session not persisting
- "Unauthorized" errors

**Solutions:**

1. **Check session configuration:**
```python
# In app/__init__.py, ensure session config is set
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
```

2. **Clear browser cookies:**
- Open browser developer tools
- Go to Application/Storage tab
- Clear cookies for localhost:40268

3. **Check user exists in database:**
```python
# Windows
py -c "
from app import create_app, db
from app.models import User
app = create_app()
with app.app_context():
    user = User.query.filter_by(email='your-email@example.com').first()
    print('User found:', user)
    if user:
        print('Password hash:', user.password_hash)
"

# Linux/macOS
python -c "
from app import create_app, db
from app.models import User
app = create_app()
with app.app_context():
    user = User.query.filter_by(email='your-email@example.com').first()
    print('User found:', user)
    if user:
        print('Password hash:', user.password_hash)
"
```

### 5. Image Generation Issues

**Symptoms:**
- Images not generating
- Gemini API errors
- Image URLs returning 404

**Solutions:**

1. **Check Gemini API key:**
```bash
# Test API key
curl -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"Hello"}]}]}' \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=YOUR_API_KEY"
```

2. **Check image generation logs:**
```python
# Windows
py -c "
from app import create_app, db
from app.models import ImageGenerationLog
app = create_app()
with app.app_context():
    logs = ImageGenerationLog.query.order_by(ImageGenerationLog.created_at.desc()).limit(5).all()
    for log in logs:
        print(f'Status: {log.status}, Error: {log.error_message}')
"

# Linux/macOS
python -c "
from app import create_app, db
from app.models import ImageGenerationLog
app = create_app()
with app.app_context():
    logs = ImageGenerationLog.query.order_by(ImageGenerationLog.created_at.desc()).limit(5).all()
    for log in logs:
        print(f'Status: {log.status}, Error: {log.error_message}')
"
```

3. **Verify image directories exist:**
```bash
ls -la app/static/generated_images/
```

### 6. Scraping Issues

**Symptoms:**
- No new stories being generated
- Scraping tasks failing
- Trend data not updating

**Solutions:**

1. **Check Playwright installation:**
```bash
playwright install
playwright --version
```

2. **Test scraping manually:**
```python
# Windows
py -c "
from ai_brain.scraping import scrape_google_trends
result = scrape_google_trends()
print('Scraping result:', result)
"

# Linux/macOS
python -c "
from ai_brain.scraping import scrape_google_trends
result = scrape_google_trends()
print('Scraping result:', result)
"
```

3. **Check scraping logs:**
```python
# Windows
py -c "
from app import create_app, db
from app.models import ScrapingLog
app = create_app()
with app.app_context():
    logs = ScrapingLog.query.order_by(ScrapingLog.created_at.desc()).limit(5).all()
    for log in logs:
        print(f'Source: {log.source}, Status: {log.status}, Error: {log.error_message}')
"

# Linux/macOS
python -c "
from app import create_app, db
from app.models import ScrapingLog
app = create_app()
with app.app_context():
    logs = ScrapingLog.query.order_by(ScrapingLog.created_at.desc()).limit(5).all()
    for log in logs:
        print(f'Source: {log.source}, Status: {log.status}, Error: {log.error_message}')
"
```

### 7. Celery/Redis Issues

**Symptoms:**
- Background tasks not running
- Queue buildup
- Redis connection errors

**Solutions:**

1. **Check Redis is running:**
```bash
# Linux/macOS
redis-cli ping

# Windows (if using WSL)
sudo service redis-server status
```

2. **Start Redis if not running:**
```bash
# Linux/macOS
redis-server

# Windows
# Use Docker: docker run -d -p 6379:6379 redis
```

3. **Check Celery worker:**
```bash
# Start Celery worker
celery -A app.celery worker --loglevel=info
```

### 8. Port and Network Issues

**Symptoms:**
- Cannot access localhost:40268
- Connection refused errors
- Firewall blocking

**Solutions:**

1. **Check firewall settings:**
```bash
# Windows
netsh advfirewall firewall add rule name="ChronoStories" dir=in action=allow protocol=TCP localport=40268

# Linux (Ubuntu/Debian)
sudo ufw allow 40268/tcp

# macOS
sudo pfctl -sr | grep 40268
```

2. **Try different port:**
```python
# In config.py
SERVER_NAME = 'localhost:8080'
```

3. **Check hosts file:**
```bash
# Windows
notepad C:\Windows\System32\drivers\etc\hosts

# Linux/macOS
sudo nano /etc/hosts
# Ensure localhost is mapped to 127.0.0.1
```

## Advanced Debugging

### Enable Debug Mode

1. **Set Flask debug mode:**
```bash
# Windows
set FLASK_ENV=development
set FLASK_DEBUG=1
py app.py

# Linux/macOS
export FLASK_ENV=development
export FLASK_DEBUG=1
python app.py
```

2. **Enable detailed logging:**
```python
# In config.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Database Debugging

1. **Enable SQL query logging:**
```python
# In config.py
SQLALCHEMY_ECHO = True
```

2. **Check database migrations:**
```bash
# If using Flask-Migrate
flask db history
flask db current
```

### Performance Debugging

1. **Profile slow queries:**
```python
from sqlalchemy import event
from sqlalchemy.engine import Engine
import time

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.time())

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - conn.info['query_start_time'].pop(-1)
    print(f"Query: {statement} - Time: {total:.4f} seconds")
```

## Getting Help

If you're still experiencing issues:

1. **Check the logs:**
```bash
tail -f logs/app.log
tail -f logs/error.log
```

2. **Create a GitHub issue with:**
- Full error traceback
- Steps to reproduce
- Your environment (OS, Python version)
- Relevant configuration (remove API keys)

3. **Join the community:**
- Check existing GitHub issues
- Ask questions in discussions
- Share your setup experience

## Emergency Recovery

If everything fails:

1. **Fresh start:**
```bash
# Backup your .env file
cp .env .env.backup

# Remove everything and clone again
cd ..
rm -rf AniStory
git clone https://github.com/Ashutoshchoudhary3/AniStory.git
cd AniStory

# Restore your .env
cp ../.env.backup .env

# Run setup again
# Windows
py setup.py

# Linux/macOS
python setup.py
```

2. **Docker alternative:**
```dockerfile
# Create a Dockerfile for consistent environment
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

Remember: Always backup your `.env` file and any important data before major changes!



