


import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GNEWS_API_KEY = os.getenv('GNEWS_API_KEY')
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///chronostories.db')
    
    # Redis
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Flask
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')
    ENV = os.getenv('FLASK_ENV', 'development')
    SERVER_NAME = os.getenv('SERVER_NAME', 'localhost:40268')
    APPLICATION_ROOT = os.getenv('APPLICATION_ROOT', '/')
    PREFERRED_URL_SCHEME = os.getenv('PREFERRED_URL_SCHEME', 'http')
    
    # Image Generation
    GEMINI_IMAGE_MODEL = os.getenv('GEMINI_IMAGE_MODEL', 'gemini-2.5-flash-image-preview')
    
    # Scraping Configuration
    MAX_SCRAPE_THREADS = int(os.getenv('MAX_SCRAPE_THREADS', '5'))
    SCRAPING_DELAY = int(os.getenv('SCRAPING_DELAY', '2'))
    
    # Story Generation
    STORIES_PER_BATCH = int(os.getenv('STORIES_PER_BATCH', '3'))
    MAX_STORY_LENGTH = int(os.getenv('MAX_STORY_LENGTH', '500'))
    MIN_STORY_LENGTH = int(os.getenv('MIN_STORY_LENGTH', '100'))
    
    # Analytics
    ENABLE_ANALYTICS = os.getenv('ENABLE_ANALYTICS', 'true').lower() == 'true'
    ANALYTICS_RETENTION_DAYS = int(os.getenv('ANALYTICS_RETENTION_DAYS', '30'))
    
    # News Sources
    SUPPORTED_COUNTRIES = ['us', 'gb', 'ca', 'au', 'de', 'fr', 'jp', 'cn', 'in', 'br']
    TREND_SOURCES = ['google_trends', 'twitter', 'reddit', 'news_aggregators']
    
    # Image Settings
    IMAGE_STYLE = "anime forge style"
    IMAGE_QUALITY = "high"
    IMAGE_SIZE = "1024x1024"

