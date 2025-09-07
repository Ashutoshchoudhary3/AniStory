





from datetime import datetime
from app import db
import json

class Analytics(db.Model):
    __tablename__ = 'analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    story_id = db.Column(db.Integer, db.ForeignKey('stories.id'), nullable=False)
    
    # Time-based analytics
    date = db.Column(db.Date, default=datetime.utcnow().date)
    hour = db.Column(db.Integer)  # 0-23 for hourly tracking
    
    # Engagement metrics
    views = db.Column(db.Integer, default=0)
    unique_views = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    shares = db.Column(db.Integer, default=0)
    comments = db.Column(db.Integer, default=0)
    click_through_rate = db.Column(db.Float, default=0.0)
    time_spent = db.Column(db.Float, default=0.0)  # Average time in seconds
    
    # Geographic data
    country_views = db.Column(db.Text)  # JSON object with country codes as keys
    device_types = db.Column(db.Text)  # JSON object with device breakdown
    
    # Traffic sources
    direct_views = db.Column(db.Integer, default=0)
    search_views = db.Column(db.Integer, default=0)
    social_views = db.Column(db.Integer, default=0)
    referral_views = db.Column(db.Integer, default=0)
    
    # User behavior
    bounce_rate = db.Column(db.Float, default=0.0)
    scroll_depth = db.Column(db.Float, default=0.0)  # Average scroll percentage
    interaction_rate = db.Column(db.Float, default=0.0)
    
    # Story-specific metrics
    completion_rate = db.Column(db.Float, default=0.0)  # For multi-part stories
    story_progress = db.Column(db.Text)  # JSON object tracking progress through story parts
    
    # AI learning data
    user_feedback_score = db.Column(db.Float)  # Explicit user ratings
    ai_predicted_engagement = db.Column(db.Float)
    ai_confidence = db.Column(db.Float)
    
    # Technical metrics
    load_time = db.Column(db.Float, default=0.0)
    error_rate = db.Column(db.Float, default=0.0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Analytics Story:{self.story_id} Date:{self.date}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'story_id': self.story_id,
            'date': self.date.isoformat(),
            'hour': self.hour,
            'views': self.views,
            'unique_views': self.unique_views,
            'likes': self.likes,
            'shares': self.shares,
            'comments': self.comments,
            'click_through_rate': self.click_through_rate,
            'time_spent': self.time_spent,
            'country_views': json.loads(self.country_views) if self.country_views else {},
            'device_types': json.loads(self.device_types) if self.device_types else {},
            'direct_views': self.direct_views,
            'search_views': self.search_views,
            'social_views': self.social_views,
            'referral_views': self.referral_views,
            'bounce_rate': self.bounce_rate,
            'scroll_depth': self.scroll_depth,
            'interaction_rate': self.interaction_rate,
            'completion_rate': self.completion_rate,
            'story_progress': json.loads(self.story_progress) if self.story_progress else {},
            'user_feedback_score': self.user_feedback_score,
            'ai_predicted_engagement': self.ai_predicted_engagement,
            'ai_confidence': self.ai_confidence,
            'load_time': self.load_time,
            'error_rate': self.error_rate,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def increment_view(self, country=None, device_type=None, source='direct'):
        """Increment view count with optional metadata"""
        self.views += 1
        self.unique_views += 1
        
        # Update country views
        if country:
            country_data = json.loads(self.country_views) if self.country_views else {}
            country_data[country] = country_data.get(country, 0) + 1
            self.country_views = json.dumps(country_data)
        
        # Update device types
        if device_type:
            device_data = json.loads(self.device_types) if self.device_types else {}
            device_data[device_type] = device_data.get(device_type, 0) + 1
            self.device_types = json.dumps(device_data)
        
        # Update traffic sources
        if source == 'direct':
            self.direct_views += 1
        elif source == 'search':
            self.search_views += 1
        elif source == 'social':
            self.social_views += 1
        elif source == 'referral':
            self.referral_views += 1
    
    def calculate_engagement_rate(self):
        """Calculate overall engagement rate"""
        if self.unique_views > 0:
            total_interactions = self.likes + self.shares + self.comments
            return (total_interactions / self.unique_views) * 100
        return 0.0
    
    def get_top_countries(self, limit=5):
        """Get top countries by views"""
        if not self.country_views:
            return []
        
        country_data = json.loads(self.country_views)
        return sorted(country_data.items(), key=lambda x: x[1], reverse=True)[:limit]





