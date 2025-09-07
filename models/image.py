







from datetime import datetime
from app import db

class Image(db.Model):
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
        import json
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







