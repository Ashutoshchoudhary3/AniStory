

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
import logging
from config import Config

# Initialize extensions
db = SQLAlchemy()

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Configure Flask
    app.config['SQLALCHEMY_DATABASE_URI'] = Config.DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = Config.SECRET_KEY
    app.config['SESSION_COOKIE_NAME'] = 'chronostories_session'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Register blueprints
    from app.routes import register_blueprints
    register_blueprints(app)
    
    # Register custom Jinja filters
    from datetime import datetime, timedelta
    import math
    
    @app.template_filter('timesince')
    def timesince_filter(dt, default="just now"):
        """Convert datetime to human readable time since format"""
        if not dt:
            return default
            
        now = datetime.utcnow()
        diff = now - dt
        
        # Convert to seconds
        seconds = int(diff.total_seconds())
        
        if seconds < 60:
            return "just now"
        elif seconds < 3600:
            minutes = math.floor(seconds / 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif seconds < 86400:
            hours = math.floor(seconds / 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif seconds < 604800:
            days = math.floor(seconds / 86400)
            return f"{days} day{'s' if days != 1 else ''} ago"
        elif seconds < 2592000:
            weeks = math.floor(seconds / 604800)
            return f"{weeks} week{'s' if weeks != 1 else ''} ago"
        elif seconds < 31536000:
            months = math.floor(seconds / 2592000)
            return f"{months} month{'s' if months != 1 else ''} ago"
        else:
            years = math.floor(seconds / 31536000)
            return f"{years} year{'s' if years != 1 else ''} ago"
    
    # Create database tables
    with app.app_context():
        db.create_all()
        logger.info("Database tables created successfully")
        
        # Initialize AI Brain
        from app.routes import initialize_ai_brain
        if initialize_ai_brain():
            logger.info("AI Brain initialized successfully")
        else:
            logger.warning("AI Brain initialization failed")
    
    return app


