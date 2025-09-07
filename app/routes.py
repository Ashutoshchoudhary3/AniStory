


from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash, Response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import logging
from app.models import Story, Analytics, Trend
from ai_brain import AIBrain
from config import Config
from app import db

# Create blueprints
main_bp = Blueprint('main', __name__)
api_bp = Blueprint('api', __name__)
stories_bp = Blueprint('stories', __name__)

# Register blueprints
def register_blueprints(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(stories_bp, url_prefix='/stories')

logger = logging.getLogger(__name__)

def get_recent_activity(limit=5):
    """Get recent activity for dashboard"""
    try:
        # Get recent stories
        recent_stories = Story.query.order_by(Story.created_at.desc()).limit(limit).all()
        
        activity = []
        
        for story in recent_stories:
            activity.append({
                'type': 'story_created',
                'title': story.title,
                'timestamp': story.created_at.isoformat(),
                'category': story.category,
                'views': story.views
            })
        
        return activity
    except Exception as e:
        logger.error(f"Error getting recent activity: {e}")
        return []

@main_bp.route('/')
def index():
    """Home page with dashboard overview"""
    try:
        # Get statistics
        total_stories = Story.query.count()
        total_views = db.session.query(db.func.sum(Story.views)).scalar() or 0
        stories_today = Story.query.filter(
            Story.created_at >= datetime.utcnow() - timedelta(days=1)
        ).count()
        
        # Get recent stories
        recent_stories = Story.query.order_by(Story.created_at.desc()).limit(6).all()
        
        # Get popular stories
        popular_stories = Story.query.order_by(Story.views.desc()).limit(6).all()
        
        # Get recent activity
        recent_activity = get_recent_activity()
        
        return render_template('index.html',
                             total_stories=total_stories,
                             total_views=total_views,
                             stories_today=stories_today,
                             recent_stories=recent_stories,
                             popular_stories=popular_stories,
                             recent_activity=recent_activity)
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return render_template('index.html',
                             total_stories=0,
                             total_views=0,
                             stories_today=0,
                             recent_stories=[],
                             popular_stories=[],
                             recent_activity=[])

@main_bp.route('/dashboard')
def dashboard():
    """Admin dashboard for monitoring"""
    try:
        # Get system statistics
        total_stories = Story.query.count()
        published_stories = Story.query.filter_by(status='published').count()
        failed_stories = Story.query.filter_by(status='failed').count()
        
        # Get recent analytics
        recent_analytics = Analytics.query\
            .filter(Analytics.created_at >= datetime.utcnow() - timedelta(days=7))\
            .order_by(Analytics.created_at.desc())\
            .limit(100)\
            .all()
        
        # Calculate metrics
        success_rate = (published_stories / total_stories * 100) if total_stories > 0 else 0
        
        return render_template('dashboard.html',
                             metrics={
                                 'total_stories': total_stories,
                                 'published_stories': published_stories,
                                 'failed_stories': failed_stories,
                                 'success_rate': success_rate,
                                 'total_views': db.session.query(db.func.sum(Story.views)).scalar() or 0
                             },
                             recent_analytics=recent_analytics)
    except Exception as e:
        logger.error(f"Error loading dashboard: {e}")
        return render_template('error.html', error="Failed to load dashboard"), 500

@stories_bp.route('/')
def stories_list():
    """List all stories with filtering and pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        category_filter = request.args.get('category', '')
        search_query = request.args.get('search', '')
        sort_by = request.args.get('sort', 'newest')
        
        # Build query
        query = Story.query
        
        # Apply filters
        if category_filter and category_filter != 'all':
            query = query.filter(Story.category == category_filter)
        
        if search_query:
            query = query.filter(
                db.or_(
                    Story.title.contains(search_query),
                    Story.summary.contains(search_query),
                    Story.content.contains(search_query)
                )
            )
        
        # Apply sorting
        if sort_by == 'oldest':
            query = query.order_by(Story.created_at.asc())
        elif sort_by == 'popular':
            query = query.order_by(Story.views.desc())
        elif sort_by == 'views':
            query = query.order_by(Story.views.desc())
        else:  # newest
            query = query.order_by(Story.created_at.desc())
        
        # Paginate
        stories = query.paginate(page=page, per_page=12, error_out=False)
        
        return render_template('stories/list.html',
                             stories=stories,
                             categories=[],  # Will be populated in template
                             current_category=category_filter)
    except Exception as e:
        logger.error(f"Error loading stories list: {e}")
        return render_template('error.html', error="Failed to load stories"), 500

@stories_bp.route('/<int:story_id>')
def story_detail(story_id):
    """View a specific story"""
    try:
        story = Story.query.get_or_404(story_id)

        if story.status != 'published':
            return render_template('error.html', error="Story not found"), 404
        
        # Record view analytics
        analytics = Analytics(
            story_id=story_id,
            metric_type='view',
            metric_value=1,
            metadata={'user_agent': request.headers.get('User-Agent')}
        )
        db.session.add(analytics)
        db.session.commit()
        
        # Get related stories
        related_stories = Story.query.filter(
            Story.category == story.category,
            Story.id != story.id,
            Story.status == 'published'
        ).order_by(Story.created_at.desc()).limit(3).all()
        
        return render_template('stories/detail.html', 
                             story=story, 
                             related_stories=related_stories)
    except Exception as e:
        logger.error(f"Error loading story {story_id}: {e}")
        return render_template('error.html', error="Failed to load story"), 500

@api_bp.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

@api_bp.route('/stories')
def api_stories():
    """API endpoint for stories"""
    try:
        page = request.args.get('page', 1, type=int)
        limit = min(request.args.get('limit', 20, type=int), 100)
        category = request.args.get('category', '')
        
        query = Story.query.filter_by(status='published')
        
        if category:
            query = query.filter_by(category=category)
        
        stories = query.order_by(Story.created_at.desc())\
            .paginate(page=page, per_page=limit, error_out=False)
        
        return jsonify({
            'stories': [story.to_dict() for story in stories.items],
            'pagination': {
                'page': page,
                'per_page': limit,
                'total': stories.total,
                'pages': stories.pages,
                'has_next': stories.has_next,
                'has_prev': stories.has_prev
            }
        })
    except Exception as e:
        logger.error(f"Error in API stories endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/stories/<int:story_id>')
def api_story_detail(story_id):
    """API endpoint for specific story"""
    try:
        story = Story.query.get_or_404(story_id)
        
        if story.status != 'published':
            return jsonify({'error': 'Story not found'}), 404
        
        return jsonify(story.to_dict())
    except Exception as e:
        logger.error(f"Error in API story detail endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/trends')
def api_trends():
    """API endpoint for trending topics"""
    try:
        trends = Trend.query.filter_by(status='active')\
            .order_by(Trend.trend_score.desc())\
            .limit(20)\
            .all()
        
        return jsonify({
            'trends': [trend.to_dict() for trend in trends]
        })
    except Exception as e:
        logger.error(f"Error in API trends endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/generate-story', methods=['POST'])
def generate_story():
    """Trigger manual story generation"""
    try:
        data = request.get_json()
        content_source = data.get('source', 'news')
        topic = data.get('topic', '')
        
        # Initialize AI Brain
        ai_brain = AIBrain()
        
        # Generate story based on source
        if content_source == 'news':
            result = ai_brain.process_news_story(topic)
        elif content_source == 'trend':
            result = ai_brain.process_trend_story(topic)
        else:
            return jsonify({'error': 'Invalid source type'}), 400
        
        if result['success']:
            return jsonify({
                'success': True,
                'story_id': result['story_id'],
                'message': 'Story generation initiated'
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Story generation failed')
            }), 500
            
    except Exception as e:
        logger.error(f"Error in generate story endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/analytics')
def api_analytics():
    """API endpoint for analytics data"""
    try:
        # Get analytics for the last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        analytics = Analytics.query\
            .filter(Analytics.created_at >= thirty_days_ago)\
            .order_by(Analytics.created_at.desc())\
            .all()
        
        # Group by metric type
        grouped_analytics = {}
        for analytic in analytics:
            if analytic.metric_type not in grouped_analytics:
                grouped_analytics[analytic.metric_type] = []
            grouped_analytics[analytic.metric_type].append(analytic.to_dict())
        
        return jsonify({
            'analytics': grouped_analytics,
            'period': '30_days'
        })
    except Exception as e:
        logger.error(f"Error in API analytics endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500


