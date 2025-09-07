

















import google.generativeai as genai
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from config import Config
from .content_analyzer import ContentAnalyzer
from .image_prompt_generator import ImagePromptGenerator
from .story_generator import StoryGenerator
# from .performance_analyzer import PerformanceAnalyzer
from scrapers import GNewsScraper, TrendScraper, PlaywrightManager
from app.models import Story, Trend, Image, Analytics
from app import db

logger = logging.getLogger(__name__)

@dataclass
class AIDecision:
    """Represents an AI decision with confidence score"""
    action: str
    parameters: Dict[str, Any]
    confidence: float
    reasoning: str
    timestamp: datetime

class AIBrain:
    """
    Central AI Brain that orchestrates the entire ChronoStories platform
    Makes intelligent decisions about content generation, scraping strategies,
    and performance optimization
    """
    
    def __init__(self):
        self.model = None
        self.content_analyzer = ContentAnalyzer()
        self.image_prompt_generator = ImagePromptGenerator()
        self.story_generator = StoryGenerator()
        # self.performance_analyzer = PerformanceAnalyzer()
        
        self.gnews_scraper = GNewsScraper()
        self.trend_scraper = TrendScraper()
        
        self.decision_history = []
        self.learning_data = {}
        self.is_initialized = False
        
        # AI Brain configuration
        self.config = {
            'max_stories_per_hour': 10,
            'min_trend_score': 70.0,
            'content_quality_threshold': 0.7,
            'image_generation_timeout': 300,
            'story_generation_timeout': 120,
            'adaptive_learning_enabled': True,
            'performance_optimization_enabled': True,
            'scraping_strategy': 'adaptive',  # adaptive, aggressive, conservative
            'content_categories': ['technology', 'business', 'politics', 'sports', 'entertainment', 'science', 'world'],
            'preferred_image_styles': ['anime forge style', 'digital art', 'illustration'],
            'target_audience': 'global',
            'language_preference': 'en'
        }
    
    async def initialize(self):
        """Initialize the AI Brain with Gemini API"""
        try:
            # Configure Gemini API
            genai.configure(api_key=Config.GEMINI_API_KEY)
            
            # Initialize the main model
            self.model = genai.GenerativeModel('gemini-1.5-pro')
            
            # Initialize sub-components
            await self.content_analyzer.initialize()
            await self.image_prompt_generator.initialize()
            await self.story_generator.initialize()
            # await self.performance_analyzer.initialize()
            
            # Initialize scrapers
            await self.trend_scraper.initialize()
            
            self.is_initialized = True
            logger.info("AI Brain initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI Brain: {e}")
            raise
    
    async def run_autonomous_cycle(self):
        """Run one autonomous cycle of the AI Brain"""
        if not self.is_initialized:
            await self.initialize()
        
        logger.info("Starting autonomous AI cycle")
        
        try:
            # Phase 1: Data Collection and Analysis
            logger.info("Phase 1: Data Collection and Analysis")
            news_data = await self._collect_news_data()
            trend_data = await self._collect_trend_data()
            
            # Phase 2: Content Analysis and Prioritization
            logger.info("Phase 2: Content Analysis and Prioritization")
            analyzed_content = await self._analyze_and_prioritize_content(news_data, trend_data)
            
            # Phase 3: Decision Making
            logger.info("Phase 3: Decision Making")
            decisions = await self._make_content_decisions(analyzed_content)
            
            # Phase 4: Content Generation
            logger.info("Phase 4: Content Generation")
            await self._execute_content_generation(decisions)
            
            # Phase 5: Performance Analysis and Learning
            logger.info("Phase 5: Performance Analysis and Learning")
            await self._analyze_performance_and_learn()
            
            logger.info("Autonomous AI cycle completed successfully")
            
        except Exception as e:
            logger.error(f"Error in autonomous AI cycle: {e}")
            await self._handle_error_recovery(e)
    
    async def _collect_news_data(self) -> List[Dict]:
        """Collect news data from various sources"""
        logger.info("Collecting news data")
        
        news_data = []
        
        # Collect from GNews API
        try:
            breaking_news = self.gnews_scraper.monitor_breaking_news()
            news_data.extend(breaking_news)
            logger.info(f"Collected {len(breaking_news)} breaking news articles")
        except Exception as e:
            logger.error(f"Error collecting breaking news: {e}")
        
        # Collect from specific categories
        for category in self.config['content_categories']:
            try:
                category_news = self.gnews_scraper.search_news(
                    category=category,
                    max_results=5,
                    from_date=datetime.utcnow() - timedelta(hours=6)
                )
                news_data.extend(category_news)
                logger.info(f"Collected {len(category_news)} {category} news articles")
            except Exception as e:
                logger.error(f"Error collecting {category} news: {e}")
        
        return news_data
    
    async def _collect_trend_data(self) -> List[Dict]:
        """Collect trend data from various sources"""
        logger.info("Collecting trend data")
        
        try:
            trends = await self.trend_scraper.scrape_all_trends()
            logger.info(f"Collected {len(trends)} trends")
            return trends
        except Exception as e:
            logger.error(f"Error collecting trend data: {e}")
            return []
    
    async def _analyze_and_prioritize_content(self, news_data: List[Dict], trend_data: List[Dict]) -> List[Dict]:
        """Analyze and prioritize content for story generation"""
        logger.info("Analyzing and prioritizing content")
        
        analyzed_content = []
        
        # Analyze news articles
        for article in news_data:
            try:
                analysis = await self.content_analyzer.analyze_article(article)
                if analysis['quality_score'] >= self.config['content_quality_threshold']:
                    analyzed_content.append({
                        'type': 'news',
                        'data': article,
                        'analysis': analysis,
                        'priority_score': analysis['relevance_score'] * 0.6 + analysis['engagement_potential'] * 0.4,
                        'timestamp': datetime.utcnow()
                    })
            except Exception as e:
                logger.error(f"Error analyzing news article: {e}")
                continue
        
        # Analyze trends
        for trend in trend_data:
            try:
                if trend.get('trend_score', 0) >= self.config['min_trend_score']:
                    analysis = await self.content_analyzer.analyze_trend(trend)
                    analyzed_content.append({
                        'type': 'trend',
                        'data': trend,
                        'analysis': analysis,
                        'priority_score': trend['trend_score'] * 0.7 + analysis['story_potential'] * 0.3,
                        'timestamp': datetime.utcnow()
                    })
            except Exception as e:
                logger.error(f"Error analyzing trend: {e}")
                continue
        
        # Sort by priority score
        analyzed_content.sort(key=lambda x: x['priority_score'], reverse=True)
        
        logger.info(f"Analyzed {len(analyzed_content)} content items")
        return analyzed_content
    
    async def _make_content_decisions(self, analyzed_content: List[Dict]) -> List[AIDecision]:
        """Make intelligent decisions about content generation"""
        logger.info("Making content decisions")
        
        decisions = []
        max_stories = self.config['max_stories_per_hour']
        
        # Get recent performance data
        # performance_data = await self.performance_analyzer.get_recent_performance()
        performance_data = {}
        
        for content in analyzed_content[:max_stories]:
            try:
                # Use Gemini to make decision
                decision_prompt = self._create_decision_prompt(content, performance_data)
                
                response = await self.model.generate_content(decision_prompt)
                decision_data = self._parse_decision_response(response.text)
                
                if decision_data['should_generate']:
                    decision = AIDecision(
                        action='generate_story',
                        parameters={
                            'content': content,
                            'story_type': decision_data['story_type'],
                            'image_style': decision_data['image_style'],
                            'target_audience': decision_data['target_audience'],
                            'narrative_angle': decision_data['narrative_angle']
                        },
                        confidence=decision_data['confidence'],
                        reasoning=decision_data['reasoning'],
                        timestamp=datetime.utcnow()
                    )
                    decisions.append(decision)
                
            except Exception as e:
                logger.error(f"Error making decision for content: {e}")
                continue
        
        # Store decisions in history
        self.decision_history.extend(decisions)
        
        logger.info(f"Made {len(decisions)} content generation decisions")
        return decisions
    
    async def _execute_content_generation(self, decisions: List[AIDecision]):
        """Execute content generation based on AI decisions"""
        logger.info("Executing content generation")
        
        for decision in decisions:
            try:
                if decision.action == 'generate_story':
                    await self._generate_story_content(decision.parameters)
                
            except Exception as e:
                logger.error(f"Error executing decision: {e}")
                continue
    
    async def _generate_story_content(self, parameters: Dict):
        """Generate story content including images and text"""
        try:
            content = parameters['content']
            story_type = parameters['story_type']
            image_style = parameters['image_style']
            narrative_angle = parameters['narrative_angle']
            
            # Generate story text
            story_data = await self.story_generator.generate_story(
                content=content,
                story_type=story_type,
                narrative_angle=narrative_angle,
                target_audience=parameters['target_audience']
            )
            
            # Generate image prompts
            image_prompts = await self.image_prompt_generator.generate_prompts(
                story_data=story_data,
                style=image_style,
                num_images=3  # Generate 3 images per story
            )
            
            # Generate images (this will be implemented in the next component)
            generated_images = []
            for prompt in image_prompts:
                # Placeholder for image generation
                image_data = {
                    'prompt': prompt,
                    'style': image_style,
                    'status': 'pending'
                }
                generated_images.append(image_data)
            
            # Create story in database
            story = Story(
                title=story_data['title'],
                content=story_data['content'],
                summary=story_data['summary'],
                category=content['analysis']['category'],
                source_type=content['type'],
                source_url=content['data'].get('url', ''),
                language='en',
                status='published',
                view_count=0,
                like_count=0,
                share_count=0,
                ai_generated=True,
                generation_metadata=json.dumps({
                    'content_type': content['type'],
                    'original_data': content['data'],
                    'analysis': content['analysis'],
                    'decision_confidence': parameters.get('confidence', 0.0),
                    'narrative_angle': narrative_angle,
                    'image_style': image_style
                })
            )
            
            db.session.add(story)
            db.session.commit()
            
            logger.info(f"Generated story: {story.title}")
            
        except Exception as e:
            logger.error(f"Error generating story content: {e}")
            raise
    
    async def _analyze_performance_and_learn(self):
        """Analyze performance and update learning data"""
        try:
            # Get recent analytics data
            # analytics_data = await self.performance_analyzer.get_analytics_data()
            analytics_data = {}
            
            # Analyze what content performs best
            # performance_insights = await self.performance_analyzer.analyze_performance(analytics_data)
            performance_insights = {}
            
            # Update AI configuration based on insights
            if self.config['adaptive_learning_enabled']:
                await self._update_ai_configuration(performance_insights)
            
            # Store learning data
            self.learning_data[datetime.utcnow().isoformat()] = performance_insights
            
            logger.info("Performance analysis and learning completed")
            
        except Exception as e:
            logger.error(f"Error in performance analysis: {e}")
    
    async def _update_ai_configuration(self, insights: Dict):
        """Update AI configuration based on performance insights"""
        try:
            # Update content categories based on performance
            if 'top_categories' in insights:
                top_categories = insights['top_categories'][:5]
                self.config['content_categories'] = top_categories
            
            # Update image styles based on engagement
            if 'top_image_styles' in insights:
                top_styles = insights['top_image_styles'][:3]
                self.config['preferred_image_styles'] = top_styles
            
            # Update scraping strategy based on success rates
            if 'scraping_success_rate' in insights:
                success_rate = insights['scraping_success_rate']
                if success_rate < 0.5:
                    self.config['scraping_strategy'] = 'conservative'
                elif success_rate > 0.8:
                    self.config['scraping_strategy'] = 'aggressive'
                else:
                    self.config['scraping_strategy'] = 'adaptive'
            
            logger.info("AI configuration updated based on performance insights")
            
        except Exception as e:
            logger.error(f"Error updating AI configuration: {e}")
    
    def _create_decision_prompt(self, content: Dict, performance_data: Dict) -> str:
        """Create prompt for AI decision making"""
        prompt = f"""
        You are the AI Brain of ChronoStories, an autonomous news story generation platform.
        
        Content Analysis:
        - Type: {content['type']}
        - Category: {content['analysis']['category']}
        - Quality Score: {content['analysis']['quality_score']}
        - Relevance Score: {content['analysis']['relevance_score']}
        - Engagement Potential: {content['analysis'].get('engagement_potential', 0)}
        
        Content Data:
        {json.dumps(content['data'], indent=2)}
        
        Recent Performance Data:
        {json.dumps(performance_data, indent=2)}
        
        Current AI Configuration:
        {json.dumps(self.config, indent=2)}
        
        Decision Criteria:
        1. Should this content be turned into a story? (Consider quality, relevance, engagement potential)
        2. What type of story should it be? (breaking news, in-depth analysis, trending topic, etc.)
        3. What image style should be used? (anime forge style, digital art, illustration, etc.)
        4. What narrative angle should be taken?
        5. What target audience should be considered?
        
        Respond in JSON format:
        {{
            "should_generate": boolean,
            "confidence": float (0-1),
            "reasoning": "detailed reasoning for the decision",
            "story_type": "type of story",
            "image_style": "image style to use",
            "narrative_angle": "narrative angle to take",
            "target_audience": "target audience"
        }}
        """
        
        return prompt
    
    def _parse_decision_response(self, response_text: str) -> Dict:
        """Parse AI decision response"""
        try:
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # Fallback to default decision
                return {
                    'should_generate': True,
                    'confidence': 0.5,
                    'reasoning': 'Default decision due to parsing error',
                    'story_type': 'general',
                    'image_style': 'anime forge style',
                    'narrative_angle': 'informative',
                    'target_audience': 'general'
                }
        except Exception as e:
            logger.error(f"Error parsing decision response: {e}")
            return {
                'should_generate': False,
                'confidence': 0.0,
                'reasoning': f'Error parsing response: {e}',
                'story_type': 'general',
                'image_style': 'anime forge style',
                'narrative_angle': 'informative',
                'target_audience': 'general'
            }
    
    async def _handle_error_recovery(self, error: Exception):
        """Handle errors and attempt recovery"""
        logger.error(f"Handling error recovery: {error}")
        
        try:
            # Log error for analysis
            error_data = {
                'error': str(error),
                'timestamp': datetime.utcnow().isoformat(),
                'context': 'autonomous_cycle',
                'recovery_actions': []
            }
            
            # Attempt recovery actions
            if 'rate_limit' in str(error).lower():
                error_data['recovery_actions'].append('rate_limit_wait')
                await asyncio.sleep(60)  # Wait 1 minute for rate limit
            
            if 'network' in str(error).lower():
                error_data['recovery_actions'].append('network_retry')
                await asyncio.sleep(10)  # Wait 10 seconds for network issues
            
            if 'api' in str(error).lower():
                error_data['recovery_actions'].append('api_reinitialize')
                await self.initialize()  # Reinitialize APIs
            
            # Store error data for learning
            self.learning_data[f"error_{datetime.utcnow().isoformat()}"] = error_data
            
        except Exception as e:
            logger.error(f"Error during recovery: {e}")
    
    def get_decision_history(self, limit: int = 100) -> List[AIDecision]:
        """Get recent decision history"""
        return self.decision_history[-limit:]
    
    def get_learning_summary(self) -> Dict:
        """Get summary of learning data"""
        return {
            'total_decisions': len(self.decision_history),
            'learning_data_points': len(self.learning_data),
            'current_config': self.config,
            'last_updated': datetime.utcnow().isoformat()
        }

# Example usage
async def example_usage():
    ai_brain = AIBrain()
    
    try:
        await ai_brain.initialize()
        
        # Run one autonomous cycle
        await ai_brain.run_autonomous_cycle()
        
        # Get decision history
        decisions = ai_brain.get_decision_history(10)
        print(f"Made {len(decisions)} decisions in the last cycle")
        
        # Get learning summary
        learning_summary = ai_brain.get_learning_summary()
        print(f"Learning summary: {learning_summary}")
        
    except Exception as e:
        print(f"Error in example usage: {e}")

if __name__ == "__main__":
    asyncio.run(example_usage())

















