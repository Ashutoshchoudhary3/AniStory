

























import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json
import sqlite3
from pathlib import Path

from config import Config
from .story_generator import StoryGenerator
from .image_prompt_generator import ImagePromptGenerator
from .content_analyzer import ContentAnalyzer
# from .performance_analyzer import PerformanceAnalyzer
# from .scraping_controller import ScrapingController

logger = logging.getLogger(__name__)

class ContentSource(Enum):
    """Content source types"""
    GNEWS = "gnews"
    TRENDING = "trending"
    SCRAPED = "scraped"
    USER_SUBMITTED = "user_submitted"

class StoryStatus(Enum):
    """Story processing status"""
    PENDING = "pending"
    ANALYZING = "analyzing"
    GENERATING_STORY = "generating_story"
    GENERATING_IMAGES = "generating_images"
    ASSEMBLING = "assembling"
    PUBLISHED = "published"
    FAILED = "failed"

@dataclass
class ProcessingTask:
    """Content processing task"""
    id: str
    source: ContentSource
    content_data: Dict
    status: StoryStatus
    created_at: datetime
    priority: int
    retry_count: int
    story_type: str
    target_audience: str
    narrative_angle: str
    metadata: Dict

class AIBrain:
    """
    Central AI intelligence system that orchestrates the entire content pipeline
    from content ingestion to story publication
    """
    
    def __init__(self):
        self.is_initialized = False
        self.is_running = False
        
        # Initialize components
        self.story_generator = StoryGenerator()
        self.image_prompt_generator = ImagePromptGenerator()
        self.content_analyzer = ContentAnalyzer()
        # self.performance_analyzer = PerformanceAnalyzer()
        # self.scraping_controller = ScrapingController()
        
        # Processing queues
        self.pending_tasks: List[ProcessingTask] = []
        self.processing_tasks: Dict[str, ProcessingTask] = {}
        self.completed_tasks: List[ProcessingTask] = []
        
        # Configuration
        self.config = {
            'max_concurrent_tasks': 3,
            'retry_limit': 3,
            'processing_timeout': 300,  # 5 minutes
            'priority_weights': {
                'breaking_news': 10,
                'trending': 8,
                'scheduled': 5,
                'user_submitted': 7
            },
            'story_generation_config': {
                'default_story_type': 'in_depth_analysis',
                'default_target_audience': 'general',
                'default_narrative_angle': 'human_impact',
                'max_images_per_story': 5,
                'min_images_per_story': 3
            },
            'performance_learning': {
                'enable_adaptation': True,
                'learning_interval': 3600,  # 1 hour
                'adaptation_threshold': 0.1  # 10% improvement threshold
            }
        }
        
        # Performance tracking
        self.performance_metrics = {
            'stories_generated': 0,
            'images_generated': 0,
            'processing_time_avg': 0,
            'success_rate': 0,
            'engagement_metrics': {},
            'learning_data': {}
        }
        
        # Database connection
        self.db_path = getattr(Config, 'DATABASE_PATH', Config.DATABASE_URL)
        self._init_database()
    
    async def initialize(self):
        """Initialize the AI Brain and all its components"""
        try:
            logger.info("Initializing AI Brain...")
            
            # Initialize components
            await self.story_generator.initialize()
            await self.image_prompt_generator.initialize()
            await self.content_analyzer.initialize()
            # await self.performance_analyzer.initialize()
            # await self.scraping_controller.initialize()
            
            # Load performance data
            await self._load_performance_data()
            
            self.is_initialized = True
            logger.info("AI Brain initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI Brain: {e}")
            raise
    
    def _init_database(self):
        """Initialize database tables"""
        try:
            # Ensure directory exists
            import os
            db_dir = os.path.dirname(self.db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create processing tasks table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS processing_tasks (
                    id TEXT PRIMARY KEY,
                    source TEXT NOT NULL,
                    content_data TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    priority INTEGER NOT NULL,
                    retry_count INTEGER NOT NULL,
                    story_type TEXT,
                    target_audience TEXT,
                    narrative_angle TEXT,
                    metadata TEXT,
                    completed_at TIMESTAMP,
                    result_data TEXT,
                    error_message TEXT
                )
            ''')
            
            # Create performance metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP NOT NULL,
                    metric_type TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    metadata TEXT
                )
            ''')
            
            # Create learning data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learning_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP NOT NULL,
                    data_type TEXT NOT NULL,
                    data_content TEXT NOT NULL,
                    effectiveness_score REAL
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    async def start(self):
        """Start the AI Brain processing loop"""
        if not self.is_initialized:
            await self.initialize()
        
        self.is_running = True
        logger.info("AI Brain started")
        
        # Start processing loop
        asyncio.create_task(self._processing_loop())
        
        # Start performance monitoring
        asyncio.create_task(self._performance_monitoring_loop())
        
        # Start scraping controller
        asyncio.create_task(self.scraping_controller.start())
    
    async def stop(self):
        """Stop the AI Brain processing"""
        self.is_running = False
        await self.scraping_controller.stop()
        logger.info("AI Brain stopped")
    
    async def process_content(self, content_data: Dict, source: ContentSource, priority: int = 5, story_type: str = None, target_audience: str = None, narrative_angle: str = None) -> str:
        """
        Process new content through the AI pipeline
        
        Args:
            content_data: Raw content data
            source: Content source
            priority: Processing priority (1-10)
            story_type: Type of story to generate
            target_audience: Target audience
            narrative_angle: Narrative angle to take
            
        Returns:
            Task ID for tracking
        """
        
        # Create processing task
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(str(content_data)) % 10000}"
        
        task = ProcessingTask(
            id=task_id,
            source=source,
            content_data=content_data,
            status=StoryStatus.PENDING,
            created_at=datetime.now(),
            priority=priority,
            retry_count=0,
            story_type=story_type or self.config['story_generation_config']['default_story_type'],
            target_audience=target_audience or self.config['story_generation_config']['default_target_audience'],
            narrative_angle=narrative_angle or self.config['story_generation_config']['default_narrative_angle'],
            metadata={'source': source.value}
        )
        
        # Add to pending queue
        self.pending_tasks.append(task)
        self.pending_tasks.sort(key=lambda x: x.priority, reverse=True)
        
        # Save task to database immediately
        await self._update_task_status(task)
        
        logger.info(f"Created processing task {task_id} for {source.value} content")
        
        return task_id
    
    async def _processing_loop(self):
        """Main processing loop"""
        while self.is_running:
            try:
                # Process pending tasks
                if self.pending_tasks and len(self.processing_tasks) < self.config['max_concurrent_tasks']:
                    task = self.pending_tasks.pop(0)
                    asyncio.create_task(self._process_task(task))
                
                # Clean up completed tasks
                await self._cleanup_completed_tasks()
                
                # Small delay to prevent CPU spinning
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error in processing loop: {e}")
                await asyncio.sleep(5)
    
    async def _process_task(self, task: ProcessingTask):
        """Process a single task through the pipeline"""
        task_id = task.id
        self.processing_tasks[task_id] = task
        
        try:
            logger.info(f"Processing task {task_id}")
            
            # Step 1: Content Analysis
            task.status = StoryStatus.ANALYZING
            await self._update_task_status(task)
            
            analysis_result = await self.content_analyzer.analyze_content(
                task.content_data,
                task.source.value
            )
            
            # Step 2: Story Generation
            task.status = StoryStatus.GENERATING_STORY
            await self._update_task_status(task)
            
            story_content = await self.story_generator.generate_story(
                {
                    'data': task.content_data,
                    'analysis': analysis_result
                },
                story_type=task.story_type,
                narrative_angle=task.narrative_angle,
                target_audience=task.target_audience
            )
            
            # Step 3: Image Generation
            task.status = StoryStatus.GENERATING_IMAGES
            await self._update_task_status(task)
            
            # Generate image prompts
            image_prompts = await self.image_prompt_generator.generate_prompts(
                story_content,
                style='anime forge style',
                num_images=self.config['story_generation_config']['min_images_per_story']
            )
            
            # Generate images (this would integrate with actual image generation API)
            generated_images = await self._generate_images(image_prompts, task.id)
            
            # Step 4: Story Assembly
            task.status = StoryStatus.ASSEMBLING
            await self._update_task_status(task)
            
            # Create final story package
            story_package = {
                'story_content': story_content,
                'images': generated_images,
                'analysis': analysis_result,
                'metadata': {
                    'task_id': task.id,
                    'source': task.source.value,
                    'created_at': datetime.now().isoformat(),
                    'story_type': task.story_type,
                    'target_audience': task.target_audience,
                    'narrative_angle': task.narrative_angle
                }
            }
            
            # Step 5: Publish
            task.status = StoryStatus.PUBLISHED
            task.metadata['story_package'] = story_package
            await self._update_task_status(task)
            
            # Update performance metrics
            self.performance_metrics['stories_generated'] += 1
            self.performance_metrics['images_generated'] += len(generated_images)
            
            logger.info(f"Successfully processed task {task_id}")
            
        except Exception as e:
            logger.error(f"Error processing task {task_id}: {e}")
            await self._handle_task_failure(task, str(e))
    
    async def _generate_images(self, image_prompts: List, task_id: str) -> List[Dict]:
        """Generate images from prompts (placeholder for actual implementation)"""
        generated_images = []
        
        for i, prompt in enumerate(image_prompts):
            try:
                # This would integrate with actual image generation API
                # For now, return placeholder data
                image_data = {
                    'prompt': prompt.prompt,
                    'style': prompt.style,
                    'url': f'https://placeholder.image/{task_id}_{i}.jpg',
                    'metadata': {
                        'prompt_data': prompt.__dict__,
                        'generated_at': datetime.now().isoformat()
                    }
                }
                generated_images.append(image_data)
                
            except Exception as e:
                logger.error(f"Error generating image {i} for task {task_id}: {e}")
                continue
        
        return generated_images
    
    async def _handle_task_failure(self, task: ProcessingTask, error_message: str):
        """Handle task failure and retry logic"""
        task.retry_count += 1
        task.metadata['error_message'] = error_message
        
        if task.retry_count < self.config['retry_limit']:
            # Retry the task
            task.status = StoryStatus.PENDING
            task.priority += 1  # Increase priority for retry
            self.pending_tasks.append(task)
            logger.warning(f"Retrying task {task.id} (attempt {task.retry_count})")
        else:
            # Mark as failed
            task.status = StoryStatus.FAILED
            self.completed_tasks.append(task)
            logger.error(f"Task {task.id} failed after {task.retry_count} attempts")
    
    async def _update_task_status(self, task: ProcessingTask):
        """Update task status in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO processing_tasks 
                (id, source, content_data, status, created_at, priority, retry_count, 
                 story_type, target_audience, narrative_angle, metadata, completed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                task.id, task.source.value, json.dumps(task.content_data), 
                task.status.value, task.created_at, task.priority, task.retry_count,
                task.story_type, task.target_audience, task.narrative_angle,
                json.dumps(task.metadata), 
                datetime.now() if task.status in [StoryStatus.PUBLISHED, StoryStatus.FAILED] else None
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error updating task status: {e}")
    
    async def _cleanup_completed_tasks(self):
        """Clean up completed tasks"""
        current_time = datetime.now()
        tasks_to_remove = []
        
        for task in self.completed_tasks:
            if (current_time - task.created_at).total_seconds() > 3600:  # Keep for 1 hour
                tasks_to_remove.append(task)
        
        for task in tasks_to_remove:
            self.completed_tasks.remove(task)
    
    async def _performance_monitoring_loop(self):
        """Monitor and analyze performance"""
        while self.is_running:
            try:
                # Collect performance data
                await self._collect_performance_metrics()
                
                # Analyze and adapt
                if self.config['performance_learning']['enable_adaptation']:
                    await self._analyze_and_adapt()
                
                # Wait for next cycle
                await asyncio.sleep(self.config['performance_learning']['learning_interval'])
                
            except Exception as e:
                logger.error(f"Error in performance monitoring: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def _collect_performance_metrics(self):
        """Collect performance metrics"""
        try:
            # Get current metrics
            current_metrics = {
                'pending_tasks': len(self.pending_tasks),
                'processing_tasks': len(self.processing_tasks),
                'completed_tasks': len(self.completed_tasks),
                'stories_generated': self.performance_metrics['stories_generated'],
                'images_generated': self.performance_metrics['images_generated']
            }
            
            # Store in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for metric_type, metric_value in current_metrics.items():
                cursor.execute('''
                    INSERT INTO performance_metrics (timestamp, metric_type, metric_value)
                    VALUES (?, ?, ?)
                ''', (datetime.now(), metric_type, metric_value))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error collecting performance metrics: {e}")
    
    async def _analyze_and_adapt(self):
        """Analyze performance and adapt strategies"""
        try:
            # Get performance data from database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get recent performance data
            cursor.execute('''
                SELECT metric_type, AVG(metric_value) as avg_value
                FROM performance_metrics
                WHERE timestamp > datetime('now', '-1 hour')
                GROUP BY metric_type
            ''')
            
            performance_data = dict(cursor.fetchall())
            conn.close()
            
            # Analyze and adapt
            if performance_data:
                # await self.performance_analyzer.analyze_performance(performance_data)
                
                # Get adaptation recommendations
                # recommendations = await self.performance_analyzer.get_adaptation_recommendations()
                recommendations = []
                
                # Apply recommendations
                await self._apply_adaptations(recommendations)
                
        except Exception as e:
            logger.error(f"Error in performance analysis: {e}")
    
    async def _apply_adaptations(self, recommendations: Dict):
        """Apply performance-based adaptations"""
        try:
            # Update story generation strategies
            if 'story_types' in recommendations:
                self.config['story_generation_config']['default_story_type'] = recommendations['story_types'].get('preferred_type', 'in_depth_analysis')
            
            # Update target audiences
            if 'target_audiences' in recommendations:
                self.config['story_generation_config']['default_target_audience'] = recommendations['target_audiences'].get('preferred_audience', 'general')
            
            # Update processing priorities
            if 'processing' in recommendations:
                processing_config = recommendations['processing']
                if 'max_concurrent_tasks' in processing_config:
                    self.config['max_concurrent_tasks'] = processing_config['max_concurrent_tasks']
            
            logger.info(f"Applied performance adaptations: {list(recommendations.keys())}")
            
        except Exception as e:
            logger.error(f"Error applying adaptations: {e}")
    
    async def _load_performance_data(self):
        """Load historical performance data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Load recent performance metrics
            cursor.execute('''
                SELECT metric_type, AVG(metric_value) as avg_value
                FROM performance_metrics
                WHERE timestamp > datetime('now', '-24 hours')
                GROUP BY metric_type
            ''')
            
            metrics = dict(cursor.fetchall())
            
            # Load learning data
            cursor.execute('''
                SELECT data_type, data_content, effectiveness_score
                FROM learning_data
                WHERE timestamp > datetime('now', '-7 days')
                ORDER BY effectiveness_score DESC
            ''')
            
            learning_data = cursor.fetchall()
            
            conn.close()
            
            # Update performance metrics
            if metrics:
                self.performance_metrics.update(metrics)
            
            # Process learning data
            if learning_data:
                self.performance_metrics['learning_data'] = {
                    item[0]: {'content': item[1], 'score': item[2]} 
                    for item in learning_data
                }
            
            logger.info(f"Loaded performance data: {len(metrics)} metrics, {len(learning_data)} learning items")
            
        except Exception as e:
            logger.error(f"Error loading performance data: {e}")
    
    def get_status(self) -> Dict:
        """Get current status of the AI Brain"""
        return {
            'is_initialized': self.is_initialized,
            'is_running': self.is_running,
            'pending_tasks': len(self.pending_tasks),
            'processing_tasks': len(self.processing_tasks),
            'completed_tasks': len(self.completed_tasks),
            'performance_metrics': self.performance_metrics,
            'config': self.config
        }
    
    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Get status of a specific task"""
        # Check pending tasks
        for task in self.pending_tasks:
            if task.id == task_id:
                return {
                    'id': task.id,
                    'status': task.status.value,
                    'source': task.source.value,
                    'story_type': task.story_type,
                    'target_audience': task.target_audience,
                    'created_at': task.created_at.isoformat(),
                    'retry_count': task.retry_count,
                    'metadata': task.metadata
                }
        
        # Check processing tasks
        if task_id in self.processing_tasks:
            task = self.processing_tasks[task_id]
            return {
                'id': task.id,
                'status': task.status.value,
                'source': task.source.value,
                'story_type': task.story_type,
                'target_audience': task.target_audience,
                'created_at': task.created_at.isoformat(),
                'retry_count': task.retry_count,
                'metadata': task.metadata
            }
        
        # Check completed tasks
        for task in self.completed_tasks:
            if task.id == task_id:
                return {
                    'id': task.id,
                    'status': task.status.value,
                    'source': task.source.value,
                    'story_type': task.story_type,
                    'target_audience': task.target_audience,
                    'created_at': task.created_at.isoformat(),
                    'retry_count': task.retry_count,
                    'metadata': task.metadata
                }
        
        return None
    
    def process_news_story(self, topic: str) -> Dict:
        """Process a news story topic (synchronous wrapper for async process_content)"""
        try:
            # Create content data for news story
            content_data = {
                'title': topic,
                'content': f"News story about {topic}",
                'topic': topic
            }
            
            # Use asyncio to run the async method
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            task_id = loop.run_until_complete(
                self.process_content(
                    content_data=content_data,
                    source=ContentSource.GNEWS,
                    priority=8,
                    story_type='news',
                    target_audience='general',
                    narrative_angle='informative'
                )
            )
            
            loop.close()
            
            return {
                'success': True,
                'story_id': task_id,
                'message': 'News story generation initiated'
            }
            
        except Exception as e:
            logger.error(f"Error processing news story: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def process_trend_story(self, topic: str) -> Dict:
        """Process a trending topic story (synchronous wrapper for async process_content)"""
        try:
            # Create content data for trend story
            content_data = {
                'title': topic,
                'content': f"Trending story about {topic}",
                'topic': topic
            }
            
            # Use asyncio to run the async method
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            task_id = loop.run_until_complete(
                self.process_content(
                    content_data=content_data,
                    source=ContentSource.TRENDING,
                    priority=9,
                    story_type='trending',
                    target_audience='general',
                    narrative_angle='engaging'
                )
            )
            
            loop.close()
            
            return {
                'success': True,
                'story_id': task_id,
                'message': 'Trend story generation initiated'
            }
            
        except Exception as e:
            logger.error(f"Error processing trend story: {e}")
            return {
                'success': False,
                'error': str(e)
            }

# Example usage (outside the class)
async def example_usage():
    ai_brain = AIBrain()
    
    try:
        # Initialize
        await ai_brain.initialize()
        
        # Start processing
        await ai_brain.start()
        
        # Example content
        example_content = {
            'title': 'Revolutionary AI Breakthrough in Medical Diagnosis',
            'description': 'Scientists develop new AI system that can diagnose rare diseases with 99% accuracy',
            'content': 'In a groundbreaking development, researchers at Stanford University have created an artificial intelligence system capable of diagnosing rare medical conditions with unprecedented accuracy.',
            'publishedAt': '2024-01-15T10:00:00Z',
            'url': 'https://example.com/ai-medical-breakthrough',
            'source': 'Tech News Daily'
        }
        
        # Process content
        task_id = await ai_brain.process_content(
            content_data=example_content,
            source=ContentSource.GNEWS,
            priority=8,
            story_type='in_depth_analysis',
            target_audience='general',
            narrative_angle='human_impact'
        )
        
        print(f"Created processing task: {task_id}")
        
        # Check status
        status = ai_brain.get_status()
        print(f"AI Brain Status: {status['is_running']}")
        print(f"Pending tasks: {status['pending_tasks']}")
        
        # Wait a bit and check task status
        await asyncio.sleep(5)
        
        task_status = ai_brain.get_task_status(task_id)
        if task_status:
            print(f"Task Status: {task_status['status']}")
            print(f"Story Type: {task_status['story_type']}")
            print(f"Target Audience: {task_status['target_audience']}")
        
        # Let it run for a bit
        await asyncio.sleep(30)
        
        # Stop
        await ai_brain.stop()
        
    except Exception as e:
        print(f"Error in example usage: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())

























