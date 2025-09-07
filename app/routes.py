


from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash, Response, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import logging
from functools import wraps
from app.models import Story, Analytics, Trend, User
from ai_brain.ai_brain import AIBrain
from config import Config
from app import db
import sqlite3
import json
import re

# Create blueprints
main_bp = Blueprint('main', __name__)
api_bp = Blueprint('api', __name__)
stories_bp = Blueprint('stories', __name__)
auth_bp = Blueprint('auth', __name__)

# Register blueprints
def register_blueprints(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(stories_bp, url_prefix='/stories')
    app.register_blueprint(auth_bp, url_prefix='/auth')

logger = logging.getLogger(__name__)

# Global AI Brain instance
ai_brain_instance = None

def get_ai_brain():
    """Get or create the global AI Brain instance"""
    global ai_brain_instance
    if ai_brain_instance is None:
        ai_brain_instance = AIBrain()
    return ai_brain_instance

def login_required(f):
    """Decorator to require login for a route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def initialize_ai_brain():
    """Initialize the AI Brain system"""
    try:
        ai_brain = get_ai_brain()
        # Note: In a production environment, you'd want to properly initialize
        # and start the AI Brain with background processing loops
        logger.info("AI Brain instance created")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize AI Brain: {e}")
        return False

def get_task_status_from_db(task_id):
    """Get task status from database"""
    try:
        db_path = getattr(Config, 'DATABASE_PATH', Config.DATABASE_URL)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, source, content_data, status, created_at, priority, retry_count,
                   story_type, target_audience, narrative_angle, metadata, completed_at,
                   result_data, error_message
            FROM processing_tasks 
            WHERE id = ?
        ''', (task_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'source': row[1],
                'content_data': json.loads(row[2]) if row[2] else {},
                'status': row[3],
                'created_at': row[4],
                'priority': row[5],
                'retry_count': row[6],
                'story_type': row[7],
                'target_audience': row[8],
                'narrative_angle': row[9],
                'metadata': json.loads(row[10]) if row[10] and row[10] != 'null' and row[10] != 'None' else {},
                'completed_at': row[11],
                'result_data': json.loads(row[12]) if row[12] and row[12] != 'null' and row[12] != 'None' else {},
                'error_message': row[13]
            }
        return None
        
    except Exception as e:
        logger.error(f"Error getting task status from database: {e}")
        return None

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
        # Check if user is logged in
        current_user = get_current_user()
        is_logged_in_flag = is_logged_in()
        
        # Get statistics - filter based on authentication
        if is_logged_in_flag:
            # Logged-in users can see all stories
            total_stories = Story.query.count()
        else:
            # Non-logged-in users can only see public stories
            total_stories = Story.query.filter(Story.user_id.is_(None)).count()
        
        total_views = db.session.query(db.func.sum(Story.views)).scalar() or 0
        stories_today = Story.query.filter(
            Story.created_at >= datetime.utcnow() - timedelta(days=1)
        ).count()
        
        # Get recent stories - filter based on authentication
        if is_logged_in_flag:
            recent_stories = Story.query.order_by(Story.created_at.desc()).limit(6).all()
        else:
            recent_stories = Story.query.filter(Story.user_id.is_(None)).order_by(Story.created_at.desc()).limit(6).all()
        
        # Get popular stories - filter based on authentication
        if is_logged_in_flag:
            popular_stories = Story.query.order_by(Story.views.desc()).limit(6).all()
        else:
            popular_stories = Story.query.filter(Story.user_id.is_(None)).order_by(Story.views.desc()).limit(6).all()
        
        # Get recent activity
        recent_activity = get_recent_activity()
        
        # Get trending topics (safe defaults for now)
        trending_topics = []
        
        return render_template('index.html',
                             total_stories=total_stories,
                             total_views=total_views,
                             stories_today=stories_today,
                             recent_stories=recent_stories,
                             popular_stories=popular_stories,
                             recent_activity=recent_activity,
                             trending_topics=trending_topics,
                             is_logged_in=is_logged_in_flag,
                             current_user=current_user)
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return render_template('index.html',
                             total_stories=0,
                             total_views=0,
                             stories_today=0,
                             recent_stories=[],
                             popular_stories=[],
                             recent_activity=[],
                             trending_topics=[],
                             is_logged_in=False,
                             current_user=None)

@main_bp.route('/dashboard')
def dashboard():
    """Admin dashboard for monitoring"""
    import logging
    logger = logging.getLogger(__name__)
    logger.debug("DEBUG: Dashboard function called")
    
    try:
        logger.debug("DEBUG: Starting dashboard data collection")
        
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
        
        # Calculate additional metrics
        total_views = db.session.query(db.func.sum(Story.views)).scalar() or 0
        avg_views_per_story = total_views / total_stories if total_stories > 0 else 0
        
        # Debug logging
        logger.debug(f"DEBUG: total_stories={total_stories}, type={type(total_stories)}")
        logger.debug(f"DEBUG: published_stories={published_stories}, type={type(published_stories)}")
        logger.debug(f"DEBUG: failed_stories={failed_stories}, type={type(failed_stories)}")
        logger.debug(f"DEBUG: success_rate={success_rate}, type={type(success_rate)}")
        logger.debug(f"DEBUG: total_views={total_views}, type={type(total_views)}")
        logger.debug(f"DEBUG: avg_views_per_story={avg_views_per_story}, type={type(avg_views_per_story)}")
        
        # Ensure all values are safe for template
        metrics = {
            'total_stories': int(total_stories) if total_stories is not None else 0,
            'published_stories': int(published_stories) if published_stories is not None else 0,
            'failed_stories': int(failed_stories) if failed_stories is not None else 0,
            'success_rate': float(success_rate) if success_rate is not None else 0.0,
            'total_views': int(total_views) if total_views is not None else 0,
            'avg_views_per_story': float(avg_views_per_story) if avg_views_per_story is not None else 0.0
        }
        
        return render_template('dashboard.html',
                             metrics=metrics,
                             recent_analytics=recent_analytics,
                             active_trends=0,
                             category_performance={},
                             max_views=1)
    except Exception as e:
        logger.error(f"DEBUG: Dashboard error details: {e}", exc_info=True)
        import traceback
        traceback.print_exc()
        # Return safe defaults
        return render_template('dashboard.html',
                             metrics={
                                 'total_stories': 0,
                                 'published_stories': 0,
                                 'failed_stories': 0,
                                 'success_rate': 0,
                                 'total_views': 0,
                                 'avg_views_per_story': 0
                             },
                             recent_analytics=[],
                             active_trends=0,
                             category_performance={},
                             max_views=1)

@stories_bp.route('/')
def stories_list():
    """List all stories with filtering and pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        category_filter = request.args.get('category', '')
        search_query = request.args.get('search', '')
        sort_by = request.args.get('sort', 'newest')
        
        # Build query
        if is_logged_in():
            # Logged-in users can see all stories (public + their own)
            query = Story.query
        else:
            # Non-logged-in users can only see public stories (where user_id is NULL)
            query = Story.query.filter(Story.user_id.is_(None))
        
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
        
        return render_template('stories_list.html',
                             stories=stories,
                             categories=[],  # Will be populated in template
                             current_category=category_filter,
                             is_logged_in=is_logged_in())
    except Exception as e:
        logger.error(f"Error loading stories list: {e}")
        return render_template('error.html', error="Failed to load stories"), 500

@stories_bp.route('/<int:story_id>')
def story_detail(story_id):
    """View a specific story"""
    try:
        story = Story.query.get_or_404(story_id)

        # Check if story is accessible
        if story.user_id is not None and not is_logged_in():
            # Private story but user not logged in
            return render_template('error.html', error="Please login to view this story"), 401
        
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
        
        return render_template('story_detail.html', 
                             story=story, 
                             related_stories=related_stories,
                             is_logged_in=is_logged_in(),
                             current_user=get_current_user())
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
@login_required
def generate_story():
    """Trigger manual story generation"""
    try:
        data = request.get_json()
        content_source = data.get('source', 'news')
        topic = data.get('topic', '')
        
        # Get current user
        current_user = get_current_user()
        
        # Get AI Brain instance
        ai_brain = get_ai_brain()
        
        # Generate story based on source
        if content_source == 'news':
            result = ai_brain.process_news_story(topic)
        elif content_source == 'trend':
            result = ai_brain.process_trend_story(topic)
        else:
            return jsonify({'error': 'Invalid source type'}), 400
        
        if result['success']:
            # Assign story to current user
            story = Story.query.get(result['story_id'])
            if story:
                story.user_id = current_user.id
                db.session.commit()
            
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

@api_bp.route('/story-status/<task_id>')
def story_status(task_id):
    """Get the status of a story generation task"""
    try:
        logger.info(f"Checking status for task: {task_id}")
        
        # First try to get status from AI Brain instance
        ai_brain = get_ai_brain()
        status = ai_brain.get_task_status(task_id)
        
        logger.info(f"AI Brain status result: {status}")
        
        # If not found in memory, try database
        if not status:
            logger.info(f"Task not found in AI Brain, checking database...")
            status = get_task_status_from_db(task_id)
            logger.info(f"Database status result: {status}")
        
        if status:
            return jsonify(status)
        else:
            return jsonify({'error': 'Task not found'}), 404
            
    except Exception as e:
        logger.error(f"Error getting story status: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Authentication Routes
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        if not username or not password:
            flash('Username and password are required', 'danger')
            return render_template('login.html')
        
        # Find user by username
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account has been deactivated', 'danger')
                return render_template('login.html')
            
            # Set session
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Set session timeout (30 minutes)
            session.permanent = True
            
            flash(f'Welcome back, {user.username}!', 'success')
            
            # Redirect to dashboard or previous page
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        terms = request.form.get('terms', False)
        
        # Validation
        if not username or not email or not password:
            flash('All fields are required', 'danger')
            return render_template('signup.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('signup.html')
        
        if not terms:
            flash('You must agree to the terms and conditions', 'danger')
            return render_template('signup.html')
        
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return render_template('signup.html')
        
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return render_template('signup.html')
        
        # Validate password strength
        if len(password) < 8:
            flash('Password must be at least 8 characters long', 'danger')
            return render_template('signup.html')
        
        if not re.search(r'[A-Z]', password):
            flash('Password must contain at least one uppercase letter', 'danger')
            return render_template('signup.html')
        
        if not re.search(r'[a-z]', password):
            flash('Password must contain at least one lowercase letter', 'danger')
            return render_template('signup.html')
        
        if not re.search(r'[0-9]', password):
            flash('Password must contain at least one number', 'danger')
            return render_template('signup.html')
        
        # Create new user
        user = User(
            username=username,
            email=email,
            full_name=username  # Default username to full_name
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('signup.html')

@auth_bp.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('main.index'))

@auth_bp.route('/profile')
def profile():
    """User profile page"""
    if 'user_id' not in session:
        flash('Please login to access your profile', 'danger')
        return redirect(url_for('auth.login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('auth.login'))
    
    # Get user's stories
    user_stories = Story.query.filter_by(user_id=user.id).order_by(Story.created_at.desc()).all()
    
    return render_template('profile.html', user=user, stories=user_stories)

@auth_bp.route('/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    """Edit user profile"""
    if 'user_id' not in session:
        flash('Please login to edit your profile', 'danger')
        return redirect(url_for('auth.login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        bio = request.form.get('bio')
        theme_preference = request.form.get('theme_preference', 'light')
        
        user.full_name = full_name
        user.bio = bio
        user.theme_preference = theme_preference
        
        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('edit_profile.html', user=user)

@auth_bp.route('/change-password', methods=['GET', 'POST'])
def change_password():
    """Change user password"""
    if 'user_id' not in session:
        flash('Please login to change your password', 'danger')
        return redirect(url_for('auth.login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not current_password or not new_password or not confirm_password:
            flash('All fields are required', 'danger')
            return render_template('change_password.html')
        
        if not user.check_password(current_password):
            flash('Current password is incorrect', 'danger')
            return render_template('change_password.html')
        
        if new_password != confirm_password:
            flash('New passwords do not match', 'danger')
            return render_template('change_password.html')
        
        if len(new_password) < 8:
            flash('New password must be at least 8 characters long', 'danger')
            return render_template('change_password.html')
        
        user.set_password(new_password)
        db.session.commit()
        
        flash('Password changed successfully', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('change_password.html')

# Helper functions
def login_required(f):
    """Decorator to require login"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def admin_required(f):
    """Decorator to require admin privileges"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'danger')
            return redirect(url_for('auth.login'))
        
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            flash('Admin access required', 'danger')
            return redirect(url_for('main.index'))
        
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def get_current_user():
    """Get current logged in user"""
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

def is_logged_in():
    """Check if user is logged in"""
    return 'user_id' in session

def is_admin():
    """Check if current user is admin"""
    if 'user_id' not in session:
        return False
    user = User.query.get(session['user_id'])
    return user and user.is_admin


