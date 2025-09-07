




from datetime import datetime
from app import db
import json

class Trend(db.Model):
    __tablename__ = 'trends'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Trend identification
    keyword = db.Column(db.String(200), nullable=False)
    display_keyword = db.Column(db.String(200))
    source = db.Column(db.String(100))  # google_trends, twitter, reddit, etc.
    source_url = db.Column(db.String(1000))
    
    # Geographic and temporal data
    country = db.Column(db.String(10))
    region = db.Column(db.String(100))
    language = db.Column(db.String(10))
    
    # Trend metrics
    volume = db.Column(db.Integer)  # Search volume or mention count
    growth_rate = db.Column(db.Float)  # Percentage growth
    trend_score = db.Column(db.Float)  # Calculated trend significance
    is_breaking = db.Column(db.Boolean, default=False)
    
    # Categorization
    category = db.Column(db.String(100))
    related_topics = db.Column(db.Text)  # JSON array
    sentiment = db.Column(db.String(50))
    
    # Time data
    discovered_at = db.Column(db.DateTime, default=datetime.utcnow)
    trend_started_at = db.Column(db.DateTime)
    peak_time = db.Column(db.DateTime)
    
    # Processing status
    is_processed = db.Column(db.Boolean, default=False)
    processed_at = db.Column(db.DateTime)
    story_id = db.Column(db.Integer, db.ForeignKey('stories.id'))
    
    # AI analysis
    ai_summary = db.Column(db.Text)
    ai_narrative_angle = db.Column(db.Text)
    ai_confidence = db.Column(db.Float)
    
    # Related entities
    entities = db.Column(db.Text)  # JSON array of people, places, organizations
    hashtags = db.Column(db.Text)  # JSON array
    
    # Status
    status = db.Column(db.String(50), default='new')  # new, analyzing, processed, failed
    priority = db.Column(db.Integer, default=1)  # 1-10, higher is more important
    
    # Error tracking
    error_message = db.Column(db.Text)
    retry_count = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    story = db.relationship('Story', backref='trend', lazy=True)
    
    def __repr__(self):
        return f'<Trend {self.keyword}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'keyword': self.keyword,
            'display_keyword': self.display_keyword,
            'source': self.source,
            'source_url': self.source_url,
            'country': self.country,
            'region': self.region,
            'volume': self.volume,
            'growth_rate': self.growth_rate,
            'trend_score': self.trend_score,
            'is_breaking': self.is_breaking,
            'category': self.category,
            'related_topics': json.loads(self.related_topics) if self.related_topics else [],
            'sentiment': self.sentiment,
            'discovered_at': self.discovered_at.isoformat(),
            'trend_started_at': self.trend_started_at.isoformat() if self.trend_started_at else None,
            'peak_time': self.peak_time.isoformat() if self.peak_time else None,
            'is_processed': self.is_processed,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'ai_summary': self.ai_summary,
            'ai_narrative_angle': self.ai_narrative_angle,
            'ai_confidence': self.ai_confidence,
            'entities': json.loads(self.entities) if self.entities else [],
            'hashtags': json.loads(self.hashtags) if self.hashtags else [],
            'status': self.status,
            'priority': self.priority,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def calculate_trend_score(self):
        """Calculate trend significance based on volume and growth rate"""
        if self.volume and self.growth_rate:
            # Simple scoring algorithm - can be refined
            volume_score = min(self.volume / 1000, 10)  # Cap at 10
            growth_score = min(abs(self.growth_rate) / 10, 10)  # Cap at 10
            self.trend_score = (volume_score + growth_score) / 2
        else:
            self.trend_score = 0.0
    
    def mark_as_processed(self, story_id=None):
        """Mark trend as processed and optionally link to story"""
        self.is_processed = True
        self.processed_at = datetime.utcnow()
        if story_id:
            self.story_id = story_id
        self.status = 'processed'
        db.session.commit()




