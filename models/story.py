



from datetime import datetime
from app import db
import json

class Story(db.Model):
    __tablename__ = 'stories'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text)
    
    # Source information
    source_type = db.Column(db.String(50))  # 'news' or 'trend'
    source_url = db.Column(db.String(1000))
    source_title = db.Column(db.String(500))
    
    # AI-generated content
    ai_headline = db.Column(db.String(500))
    ai_caption = db.Column(db.Text)
    ai_narrative = db.Column(db.Text)
    
    # Image information
    image_url = db.Column(db.String(1000))
    image_prompt = db.Column(db.Text)
    image_style = db.Column(db.String(100), default='anime forge style')
    
    # Categorization
    category = db.Column(db.String(100))
    tags = db.Column(db.Text)  # JSON array
    sentiment = db.Column(db.String(50))  # positive, negative, neutral
    
    # Geographic and temporal data
    country = db.Column(db.String(10))
    language = db.Column(db.String(10))
    published_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Story sequence for multi-part stories
    is_part_of_series = db.Column(db.Boolean, default=False)
    series_id = db.Column(db.String(100))
    sequence_number = db.Column(db.Integer, default=1)
    total_parts = db.Column(db.Integer, default=1)
    
    # Analytics
    views = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    shares = db.Column(db.Integer, default=0)
    engagement_rate = db.Column(db.Float, default=0.0)
    
    # Status and workflow
    status = db.Column(db.String(50), default='draft')  # draft, published, archived
    workflow_stage = db.Column(db.String(50), default='created')  # created, processing, completed, failed
    
    # AI processing metadata
    ai_processing_time = db.Column(db.Float)
    ai_model_version = db.Column(db.String(100))
    ai_confidence_score = db.Column(db.Float)
    
    # Error tracking
    error_message = db.Column(db.Text)
    retry_count = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    
    # Relationships
    images = db.relationship('Image', backref='story', lazy=True, cascade='all, delete-orphan')
    analytics = db.relationship('Analytics', backref='story', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Story {self.title[:50]}...>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'summary': self.summary,
            'source_type': self.source_type,
            'source_url': self.source_url,
            'ai_headline': self.ai_headline,
            'ai_caption': self.ai_caption,
            'image_url': self.image_url,
            'category': self.category,
            'tags': json.loads(self.tags) if self.tags else [],
            'sentiment': self.sentiment,
            'country': self.country,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'is_part_of_series': self.is_part_of_series,
            'series_id': self.series_id,
            'sequence_number': self.sequence_number,
            'total_parts': self.total_parts,
            'views': self.views,
            'likes': self.likes,
            'shares': self.shares,
            'engagement_rate': self.engagement_rate,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def increment_views(self):
        self.views += 1
        db.session.commit()
    
    def increment_likes(self):
        self.likes += 1
        self.calculate_engagement_rate()
        db.session.commit()
    
    def increment_shares(self):
        self.shares += 1
        self.calculate_engagement_rate()
        db.session.commit()
    
    def calculate_engagement_rate(self):
        total_interactions = self.likes + self.shares
        if self.views > 0:
            self.engagement_rate = (total_interactions / self.views) * 100
        else:
            self.engagement_rate = 0.0



