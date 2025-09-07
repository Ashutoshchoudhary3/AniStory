



from datetime import datetime
import json

# Import db from app package to avoid circular imports
from app import db

class Story(db.Model):
    """News story model"""
    __tablename__ = 'stories'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text)
    category = db.Column(db.String(100))
    tags = db.Column(db.Text)  # JSON array
    image_url = db.Column(db.String(500))
    image_prompt = db.Column(db.Text)
    source_url = db.Column(db.String(500))
    source_type = db.Column(db.String(50))  # news, trend, manual
    status = db.Column(db.String(50), default='draft')  # draft, published, failed
    views = db.Column(db.Integer, default=0)  # Changed from view_count to views for consistency
    engagement_score = db.Column(db.Float, default=0.0)
    
    # AI processing metadata
    ai_model_used = db.Column(db.String(100))
    processing_metadata = db.Column(db.Text)  # JSON for storing AI processing details
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Story {self.title[:50]}>'
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'summary': self.summary,
            'category': self.category,
            'tags': json.loads(self.tags) if self.tags else [],
            'image_url': self.image_url,
            'source_url': self.source_url,
            'source_type': self.source_type,
            'status': self.status,
            'views': self.views,  # Updated field name
            'engagement_score': self.engagement_score,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'published_at': self.published_at.isoformat() if self.published_at else None
        }

class Trend(db.Model):
    """Trending topics model"""
    __tablename__ = 'trends'
    
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(200), nullable=False)
    keywords = db.Column(db.Text)  # JSON array
    trend_score = db.Column(db.Float, default=0.0)
    volume = db.Column(db.Integer, default=0)
    source = db.Column(db.String(100))  # google_trends, twitter, reddit, etc.
    region = db.Column(db.String(10))  # country code
    category = db.Column(db.String(100))
    status = db.Column(db.String(50), default='active')  # active, processed, expired
    extra_data = db.Column(db.Text)  # JSON for additional data
    
    # Timestamps
    discovered_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Trend {self.topic[:50]}>'
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'topic': self.topic,
            'keywords': json.loads(self.keywords) if self.keywords else [],
            'trend_score': self.trend_score,
            'volume': self.volume,
            'source': self.source,
            'region': self.region,
            'category': self.category,
            'status': self.status,
            'extra_data': json.loads(self.extra_data) if self.extra_data else {},
            'discovered_at': self.discovered_at.isoformat() if self.discovered_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }

class Analytics(db.Model):
    """Analytics tracking model"""
    __tablename__ = 'analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    story_id = db.Column(db.Integer, db.ForeignKey('stories.id'))
    metric_type = db.Column(db.String(50))  # view, click, engagement, etc.
    metric_value = db.Column(db.Float, default=1.0)
    extra_data = db.Column(db.Text)  # JSON for additional context
    user_session = db.Column(db.String(100))
    user_agent = db.Column(db.String(500))
    ip_address = db.Column(db.String(45))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Analytics {self.metric_type}={self.metric_value}>'
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'story_id': self.story_id,
            'metric_type': self.metric_type,
            'metric_value': self.metric_value,
            'extra_data': json.loads(self.extra_data) if self.extra_data else {},
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class NewsSource(db.Model):
    """News sources configuration"""
    __tablename__ = 'news_sources'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(500))
    api_endpoint = db.Column(db.String(500))
    source_type = db.Column(db.String(50))  # rss, api, scraper
    region = db.Column(db.String(10))
    category = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    last_fetched = db.Column(db.DateTime)
    fetch_frequency = db.Column(db.Integer, default=3600)  # seconds
    
    # Configuration
    config = db.Column(db.Text)  # JSON for source-specific settings
    
    def __repr__(self):
        return f'<NewsSource {self.name}>'

class ImageGenerationLog(db.Model):
    """Log of image generation attempts"""
    __tablename__ = 'image_generation_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    story_id = db.Column(db.Integer, db.ForeignKey('stories.id'))
    prompt = db.Column(db.Text, nullable=False)
    model_used = db.Column(db.String(100))
    status = db.Column(db.String(50))  # success, failed, pending
    image_url = db.Column(db.String(500))
    error_message = db.Column(db.Text)
    generation_time = db.Column(db.Float)  # seconds
    cost = db.Column(db.Float)  # API cost if applicable
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ImageGenerationLog {self.story_id}:{self.status}>'

class Image(db.Model):
    """Generated images for stories"""
    __tablename__ = 'images'
    
    id = db.Column(db.Integer, primary_key=True)
    story_id = db.Column(db.Integer, db.ForeignKey('stories.id'), nullable=False)
    
    # Image metadata
    filename = db.Column(db.String(500))
    original_filename = db.Column(db.String(500))
    file_path = db.Column(db.String(1000))
    url = db.Column(db.String(1000))
    
    # Image properties
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    size = db.Column(db.Integer)  # File size in bytes
    format = db.Column(db.String(50))
    mode = db.Column(db.String(50))
    
    # AI generation data
    prompt = db.Column(db.Text)
    negative_prompt = db.Column(db.Text)
    model_name = db.Column(db.String(200))
    model_version = db.Column(db.String(100))
    generation_params = db.Column(db.Text)  # JSON string of generation parameters
    
    # Style and content
    style = db.Column(db.String(100), default='anime forge style')
    content_description = db.Column(db.Text)
    tags = db.Column(db.Text)  # JSON array of tags
    
    # Quality and validation
    quality_score = db.Column(db.Float)
    is_appropriate = db.Column(db.Boolean, default=True)
    content_warnings = db.Column(db.Text)  # JSON array of warnings
    
    # Usage tracking
    usage_count = db.Column(db.Integer, default=0)
    last_used_at = db.Column(db.DateTime)
    
    # Alternative versions
    is_primary = db.Column(db.Boolean, default=True)
    parent_image_id = db.Column(db.Integer, db.ForeignKey('images.id'))
    variation_number = db.Column(db.Integer, default=0)
    
    # Processing status
    status = db.Column(db.String(50), default='pending')  # pending, generating, completed, failed
    error_message = db.Column(db.Text)
    generation_time = db.Column(db.Float)  # Time in seconds
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    generated_at = db.Column(db.DateTime)
    
    # Relationships
    parent_image = db.relationship('Image', remote_side=[id], backref='variations')
    
    def __repr__(self):
        return f'<Image {self.filename}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'story_id': self.story_id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_path': self.file_path,
            'url': self.url,
            'width': self.width,
            'height': self.height,
            'size': self.size,
            'format': self.format,
            'mode': self.mode,
            'prompt': self.prompt,
            'negative_prompt': self.negative_prompt,
            'model_name': self.model_name,
            'model_version': self.model_version,
            'generation_params': self.generation_params,
            'style': self.style,
            'content_description': self.content_description,
            'tags': json.loads(self.tags) if self.tags else [],
            'quality_score': self.quality_score,
            'is_appropriate': self.is_appropriate,
            'content_warnings': json.loads(self.content_warnings) if self.content_warnings else [],
            'usage_count': self.usage_count,
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None,
            'is_primary': self.is_primary,
            'parent_image_id': self.parent_image_id,
            'variation_number': self.variation_number,
            'status': self.status,
            'error_message': self.error_message,
            'generation_time': self.generation_time,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'generated_at': self.generated_at.isoformat() if self.generated_at else None
        }
    
    def mark_as_used(self):
        """Mark image as used and update usage count"""
        self.usage_count += 1
        self.last_used_at = datetime.utcnow()
    
    def get_file_size_mb(self):
        """Get file size in MB"""
        if self.size:
            return round(self.size / (1024 * 1024), 2)
        return 0.0
    
    def get_aspect_ratio(self):
        """Get aspect ratio as a string"""
        if self.width and self.height:
            ratio = self.width / self.height
            return f"{ratio:.2f}:1"
        return None

class ScrapingLog(db.Model):
    """Log of scraping activities"""
    __tablename__ = 'scraping_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(100))
    url = db.Column(db.String(500))
    status = db.Column(db.String(50))  # success, failed, blocked
    items_found = db.Column(db.Integer, default=0)
    error_message = db.Column(db.Text)
    response_time = db.Column(db.Float)  # seconds
    user_agent = db.Column(db.String(500))
    proxy_used = db.Column(db.String(100))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ScrapingLog {self.source}:{self.status}>'



