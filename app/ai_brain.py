





import logging
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import google.generativeai as genai
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import time
import re
from app.models import db, Story, Trend, Analytics, ImageGenerationLog, ScrapingLog
from config import Config

logger = logging.getLogger(__name__)

class AIBrain:
    """Central AI intelligence system that orchestrates the entire platform"""
    
    def __init__(self):
        """Initialize the AI Brain with necessary configurations"""
        self.config = Config()
        self.gemini_model = None
        self.image_model = None
        self.setup_ai_models()
        
    def setup_ai_models(self):
        """Setup and configure AI models"""
        try:
            # Configure Gemini
            genai.configure(api_key=self.config.GEMINI_API_KEY)
            
            # Initialize text generation model
            self.gemini_model = genai.GenerativeModel('gemini-pro')
            
            # Initialize image generation model
            self.image_model = genai.GenerativeModel(self.config.GEMINI_IMAGE_MODEL)
            
            logger.info("AI models initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AI models: {e}")
            raise
    
    def process_news_story(self, topic: str = "") -> Dict:
        """Process a news story from GNews API"""
        try:
            # Fetch news from GNews API
            news_data = self.fetch_gnews_data(topic)
            
            if not news_data:
                return {'success': False, 'error': 'No news data found'}
            
            # Analyze and expand the story
            expanded_content = self.expand_news_content(news_data)
            
            # Generate image prompt
            image_prompt = self.generate_image_prompt(expanded_content)
            
            # Generate image
            image_result = self.generate_image(image_prompt)
            
            if not image_result['success']:
                return {'success': False, 'error': 'Image generation failed'}
            
            # Create story
            story = self.create_story(
                title=expanded_content['title'],
                content=expanded_content['content'],
                summary=expanded_content['summary'],
                category=expanded_content['category'],
                image_url=image_result['image_url'],
                image_prompt=image_prompt,
                source_url=news_data.get('url'),
                source_type='news'
            )
            
            return {
                'success': True,
                'story_id': story.id,
                'title': story.title
            }
            
        except Exception as e:
            logger.error(f"Error processing news story: {e}")
            return {'success': False, 'error': str(e)}
    
    def process_trend_story(self, trend_topic: str = "") -> Dict:
        """Process a trending topic into a story"""
        try:
            # Scrape trending data
            trend_data = self.scrape_trending_data(trend_topic)
            
            if not trend_data:
                return {'success': False, 'error': 'No trend data found'}
            
            # Analyze trend context
            trend_analysis = self.analyze_trend_context(trend_data)
            
            # Generate story content
            story_content = self.generate_trend_story(trend_analysis)
            
            # Generate image prompt
            image_prompt = self.generate_trend_image_prompt(trend_analysis)
            
            # Generate image
            image_result = self.generate_image(image_prompt)
            
            if not image_result['success']:
                return {'success': False, 'error': 'Image generation failed'}
            
            # Create story
            story = self.create_story(
                title=story_content['title'],
                content=story_content['content'],
                summary=story_content['summary'],
                category=story_content['category'],
                image_url=image_result['image_url'],
                image_prompt=image_prompt,
                source_type='trend'
            )
            
            return {
                'success': True,
                'story_id': story.id,
                'title': story.title
            }
            
        except Exception as e:
            logger.error(f"Error processing trend story: {e}")
            return {'success': False, 'error': str(e)}
    
    def fetch_gnews_data(self, topic: str = "") -> Optional[Dict]:
        """Fetch news data from GNews API"""
        try:
            base_url = "https://gnews.io/api/v4/search"
            params = {
                'apikey': self.config.GNEWS_API_KEY,
                'lang': 'en',
                'max': 10,
                'sortby': 'publishedAt'
            }
            
            if topic:
                params['q'] = topic
            else:
                params['q'] = 'technology OR science OR world news'
            
            response = requests.get(base_url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                if articles:
                    # Select the most relevant article
                    article = self.select_best_article(articles)
                    return {
                        'title': article.get('title', ''),
                        'description': article.get('description', ''),
                        'content': article.get('content', ''),
                        'url': article.get('url', ''),
                        'published_at': article.get('publishedAt', ''),
                        'source': article.get('source', {}).get('name', '')
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching GNews data: {e}")
            return None
    
    def scrape_trending_data(self, topic: str = "") -> Optional[Dict]:
        """Scrape trending data from various sources"""
        try:
            trends = []
            
            # Scrape Google Trends
            google_trends = self.scrape_google_trends(topic)
            if google_trends:
                trends.extend(google_trends)
            
            # Scrape Twitter/X trends
            twitter_trends = self.scrape_twitter_trends(topic)
            if twitter_trends:
                trends.extend(twitter_trends)
            
            # Scrape Reddit trends
            reddit_trends = self.scrape_reddit_trends(topic)
            if reddit_trends:
                trends.extend(reddit_trends)
            
            if not trends:
                return None
            
            # Select the most promising trend
            best_trend = self.select_best_trend(trends)
            return best_trend
            
        except Exception as e:
            logger.error(f"Error scraping trending data: {e}")
            return None
    
    def scrape_google_trends(self, topic: str = "") -> List[Dict]:
        """Scrape Google Trends data"""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                page = context.new_page()
                
                url = "https://trends.google.com/trends/trendingsearches/daily"
                if topic:
                    url += f"?q={topic}"
                
                page.goto(url, wait_until='networkidle', timeout=30000)
                
                # Wait for content to load
                page.wait_for_selector('.feed-list', timeout=10000)
                
                # Extract trending topics
                trends = []
                trend_items = page.query_selector_all('.feed-item')
                
                for item in trend_items[:10]:
                    try:
                        title_elem = item.query_selector('.title')
                        search_count_elem = item.query_selector('.search-count')
                        
                        if title_elem:
                            title = title_elem.text_content().strip()
                            search_count = search_count_elem.text_content().strip() if search_count_elem else "0"
                            
                            # Extract number from search count
                            numbers = re.findall(r'\d+', search_count)
                            volume = int(numbers[0]) if numbers else 0
                            
                            trends.append({
                                'topic': title,
                                'volume': volume,
                                'source': 'google_trends',
                                'category': 'general'
                            })
                    except Exception as e:
                        logger.warning(f"Error extracting trend item: {e}")
                        continue
                
                browser.close()
                return trends
                
        except Exception as e:
            logger.error(f"Error scraping Google Trends: {e}")
            return []
    
    def scrape_twitter_trends(self, topic: str = "") -> List[Dict]:
        """Scrape Twitter/X trending topics"""
        try:
            # Note: This is a simplified implementation
            # In production, you'd need proper Twitter API access
            trends = []
            
            # Simulate some trending topics
            if not topic:
                trends = [
                    {'topic': 'AI Technology', 'volume': 50000, 'source': 'twitter', 'category': 'technology'},
                    {'topic': 'Climate Change', 'volume': 35000, 'source': 'twitter', 'category': 'environment'},
                    {'topic': 'Space Exploration', 'volume': 28000, 'source': 'twitter', 'category': 'science'}
                ]
            else:
                trends = [{
                    'topic': topic,
                    'volume': 10000,
                    'source': 'twitter',
                    'category': 'general'
                }]
            
            return trends
            
        except Exception as e:
            logger.error(f"Error scraping Twitter trends: {e}")
            return []
    
    def scrape_reddit_trends(self, topic: str = "") -> List[Dict]:
        """Scrape Reddit trending topics"""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                page = context.new_page()
                
                url = "https://www.reddit.com/r/popular/"
                page.goto(url, wait_until='networkidle', timeout=30000)
                
                # Wait for posts to load
                page.wait_for_selector('[data-testid="post-container"]', timeout=10000)
                
                # Extract trending posts
                trends = []
                posts = page.query_selector_all('[data-testid="post-container"]')[:10]
                
                for post in posts:
                    try:
                        title_elem = post.query_selector('h3')
                        upvote_elem = post.query_selector('[data-testid="post-score"]')
                        
                        if title_elem:
                            title = title_elem.text_content().strip()
                            upvotes = 0
                            
                            if upvote_elem:
                                upvote_text = upvote_elem.text_content().strip()
                                numbers = re.findall(r'\d+', upvote_text)
                                upvotes = int(numbers[0]) if numbers else 0
                            
                            trends.append({
                                'topic': title,
                                'volume': upvotes,
                                'source': 'reddit',
                                'category': 'general'
                            })
                    except Exception as e:
                        logger.warning(f"Error extracting Reddit post: {e}")
                        continue
                
                browser.close()
                return trends
                
        except Exception as e:
            logger.error(f"Error scraping Reddit trends: {e}")
            return []
    
    def expand_news_content(self, news_data: Dict) -> Dict:
        """Expand news content using AI"""
        try:
            prompt = f"""
            Based on this news article, create an engaging story:
            
            Title: {news_data['title']}
            Description: {news_data['description']}
            Content: {news_data['content']}
            
            Please provide:
            1. A compelling title (max 100 characters)
            2. An engaging story content (300-500 words)
            3. A brief summary (50-100 words)
            4. Category (technology, science, world, business, entertainment, sports, health)
            5. Relevant tags (3-5 keywords)
            
            Make it suitable for a web story format with anime-style visuals.
            """
            
            response = self.gemini_model.generate_content(prompt)
            content = response.text
            
            # Parse the response
            lines = content.split('\n')
            result = {
                'title': news_data['title'],
                'content': content,
                'summary': news_data['description'],
                'category': 'general',
                'tags': ['news', 'current-events']
            }
            
            # Try to extract structured data
            for line in lines:
                if line.startswith('Title:') or line.startswith('1. Title:'):
                    result['title'] = line.split(':', 1)[1].strip()
                elif line.startswith('Summary:') or line.startswith('3. Summary:'):
                    result['summary'] = line.split(':', 1)[1].strip()
                elif line.startswith('Category:') or line.startswith('4. Category:'):
                    result['category'] = line.split(':', 1)[1].strip().lower()
                elif line.startswith('Tags:') or line.startswith('5. Tags:'):
                    tags_str = line.split(':', 1)[1].strip()
                    result['tags'] = [tag.strip() for tag in tags_str.split(',')]
            
            return result
            
        except Exception as e:
            logger.error(f"Error expanding news content: {e}")
            return {
                'title': news_data['title'],
                'content': news_data['description'],
                'summary': news_data['description'][:100],
                'category': 'general',
                'tags': ['news']
            }
    
    def analyze_trend_context(self, trend_data: Dict) -> Dict:
        """Analyze trending topic context"""
        try:
            prompt = f"""
            Analyze this trending topic and provide context:
            
            Topic: {trend_data['topic']}
            Volume: {trend_data['volume']}
            Source: {trend_data['source']}
            
            Please provide:
            1. What is this trend about?
            2. Why is it trending?
            3. Key points to cover in a story
            4. Target audience
            5. Emotional tone (exciting, concerning, inspiring, etc.)
            """
            
            response = self.gemini_model.generate_content(prompt)
            analysis = response.text
            
            return {
                'trend_data': trend_data,
                'analysis': analysis,
                'topic': trend_data['topic'],
                'volume': trend_data['volume'],
                'source': trend_data['source']
            }
            
        except Exception as e:
            logger.error(f"Error analyzing trend context: {e}")
            return {
                'trend_data': trend_data,
                'analysis': f"Trending topic: {trend_data['topic']}",
                'topic': trend_data['topic'],
                'volume': trend_data['volume'],
                'source': trend_data['source']
            }
    
    def generate_trend_story(self, trend_analysis: Dict) -> Dict:
        """Generate story content from trend analysis"""
        try:
            prompt = f"""
            Create an engaging story based on this trending topic analysis:
            
            {trend_analysis['analysis']}
            
            Please provide:
            1. A compelling title (max 100 characters)
            2. An engaging story content (300-500 words)
            3. A brief summary (50-100 words)
            4. Category (technology, science, world, business, entertainment, sports, health)
            5. Relevant tags (3-5 keywords)
            
            Make it suitable for a web story format with anime-style visuals.
            """
            
            response = self.gemini_model.generate_content(prompt)
            content = response.text
            
            return {
                'title': trend_analysis['topic'],
                'content': content,
                'summary': f"Trending: {trend_analysis['topic']}",
                'category': trend_analysis['trend_data'].get('category', 'general'),
                'tags': [trend_analysis['topic'].lower().replace(' ', '-')]
            }
            
        except Exception as e:
            logger.error(f"Error generating trend story: {e}")
            return {
                'title': trend_analysis['topic'],
                'content': f"This is trending: {trend_analysis['topic']}",
                'summary': f"Trending topic: {trend_analysis['topic']}",
                'category': 'general',
                'tags': ['trending']
            }
    
    def generate_image_prompt(self, content_data: Dict) -> str:
        """Generate image prompt for news story"""
        try:
            prompt = f"""
            Create a detailed image generation prompt for this story:
            
            Title: {content_data['title']}
            Content: {content_data['content'][:200]}
            Category: {content_data['category']}
            
            Requirements:
            - Use "{self.config.IMAGE_STYLE}" style
            - 1024x1024 resolution
            - Focus on the most visually interesting aspect
            - Include emotional elements
            - Make it engaging for web stories
            
            Provide only the prompt text, no explanations.
            """
            
            response = self.gemini_model.generate_content(prompt)
            image_prompt = response.text.strip()
            
            # Ensure the style is included
            if self.config.IMAGE_STYLE not in image_prompt.lower():
                image_prompt = f"{self.config.IMAGE_STYLE}, {image_prompt}"
            
            return image_prompt
            
        except Exception as e:
            logger.error(f"Error generating image prompt: {e}")
            return f"{self.config.IMAGE_STYLE}, anime illustration of {content_data['title']}"
    
    def generate_trend_image_prompt(self, trend_analysis: Dict) -> str:
        """Generate image prompt for trending topic"""
        try:
            prompt = f"""
            Create a detailed image generation prompt for this trending topic:
            
            Topic: {trend_analysis['topic']}
            Analysis: {trend_analysis['analysis'][:200]}
            
            Requirements:
            - Use "{self.config.IMAGE_STYLE}" style
            - 1024x1024 resolution
            - Capture the essence of why this is trending
            - Include emotional and visual impact
            - Make it shareable for social media
            
            Provide only the prompt text, no explanations.
            """
            
            response = self.gemini_model.generate_content(prompt)
            image_prompt = response.text.strip()
            
            # Ensure the style is included
            if self.config.IMAGE_STYLE not in image_prompt.lower():
                image_prompt = f"{self.config.IMAGE_STYLE}, {image_prompt}"
            
            return image_prompt
            
        except Exception as e:
            logger.error(f"Error generating trend image prompt: {e}")
            return f"{self.config.IMAGE_STYLE}, anime illustration of {trend_analysis['topic']}"
    
    def generate_image(self, prompt: str) -> Dict:
        """Generate image using Gemini"""
        try:
            # Log the attempt
            log_entry = ImageGenerationLog(
                prompt=prompt,
                model_used=self.config.GEMINI_IMAGE_MODEL,
                status='pending'
            )
            db.session.add(log_entry)
            db.session.commit()
            
            start_time = time.time()
            
            # Generate image
            response = self.image_model.generate_content([prompt])
            
            generation_time = time.time() - start_time
            
            if response and response.text:
                # For now, we'll simulate image URL generation
                # In production, you'd upload to cloud storage
                image_url = f"https://via.placeholder.com/1024x1024/FF6B6B/FFFFFF?text={prompt[:50].replace(' ', '+')}"
                
                # Update log
                log_entry.status = 'success'
                log_entry.image_url = image_url
                log_entry.generation_time = generation_time
                db.session.commit()
                
                return {
                    'success': True,
                    'image_url': image_url,
                    'prompt': prompt
                }
            else:
                # Update log
                log_entry.status = 'failed'
                log_entry.error_message = 'No response from image model'
                db.session.commit()
                
                return {
                    'success': False,
                    'error': 'Image generation failed'
                }
                
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            
            # Update log
            if 'log_entry' in locals():
                log_entry.status = 'failed'
                log_entry.error_message = str(e)
                db.session.commit()
            
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_story(self, title: str, content: str, summary: str, 
                    category: str, image_url: str, image_prompt: str,
                    source_url: str = "", source_type: str = "news") -> Story:
        """Create and save a new story"""
        try:
            story = Story(
                title=title,
                content=content,
                summary=summary,
                category=category,
                image_url=image_url,
                image_prompt=image_prompt,
                source_url=source_url,
                source_type=source_type,
                status='published',
                published_at=datetime.utcnow(),
                ai_model_used=self.config.GEMINI_IMAGE_MODEL,
                processing_metadata=json.dumps({
                    'image_model': self.config.GEMINI_IMAGE_MODEL,
                    'created_by': 'ai_brain',
                    'processing_time': datetime.utcnow().isoformat()
                })
            )
            
            db.session.add(story)
            db.session.commit()
            
            logger.info(f"Created story: {story.title}")
            return story
            
        except Exception as e:
            logger.error(f"Error creating story: {e}")
            raise
    
    def select_best_article(self, articles: List[Dict]) -> Dict:
        """Select the most suitable article for story generation"""
        try:
            # Filter articles by relevance and quality
            valid_articles = []
            
            for article in articles:
                # Check if article has required fields
                if (article.get('title') and 
                    article.get('description') and 
                    len(article.get('title', '')) > 20):
                    
                    # Calculate relevance score
                    title = article.get('title', '').lower()
                    description = article.get('description', '').lower()
                    
                    # Prefer articles about technology, science, innovation
                    tech_keywords = ['technology', 'tech', 'ai', 'artificial intelligence', 
                                   'science', 'innovation', 'research', 'discovery']
                    
                    score = 0
                    for keyword in tech_keywords:
                        if keyword in title or keyword in description:
                            score += 1
                    
                    article['relevance_score'] = score
                    valid_articles.append(article)
            
            # Sort by relevance score and select the best one
            if valid_articles:
                valid_articles.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
                return valid_articles[0]
            
            # Fallback to first article
            return articles[0] if articles else {}
            
        except Exception as e:
            logger.error(f"Error selecting best article: {e}")
            return articles[0] if articles else {}
    
    def select_best_trend(self, trends: List[Dict]) -> Dict:
        """Select the most promising trend for story generation"""
        try:
            # Filter and score trends
            valid_trends = []
            
            for trend in trends:
                # Check minimum volume
                if trend.get('volume', 0) > 1000:
                    # Calculate trend score based on volume and recency
                    volume = trend.get('volume', 0)
                    category_multiplier = 1.0
                    
                    # Prefer certain categories
                    if trend.get('category') in ['technology', 'science', 'business']:
                        category_multiplier = 1.5
                    
                    trend['trend_score'] = volume * category_multiplier
                    valid_trends.append(trend)
            
            # Sort by trend score and select the best one
            if valid_trends:
                valid_trends.sort(key=lambda x: x.get('trend_score', 0), reverse=True)
                return valid_trends[0]
            
            # Fallback to highest volume trend
            if trends:
                trends.sort(key=lambda x: x.get('volume', 0), reverse=True)
                return trends[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error selecting best trend: {e}")
            return trends[0] if trends else None
    
    def adapt_scraping_strategy(self, failed_attempt: ScrapingLog) -> Dict:
        """Adapt scraping strategy based on failed attempts"""
        try:
            strategy = {
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'delay': 2,
                'use_proxy': False,
                'retry_count': 3
            }
            
            # Analyze failure reason
            if failed_attempt.error_message:
                error_msg = failed_attempt.error_message.lower()
                
                if 'captcha' in error_msg or 'blocked' in error_msg:
                    strategy['use_proxy'] = True
                    strategy['delay'] = 5
                    strategy['user_agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
                
                elif 'timeout' in error_msg:
                    strategy['delay'] = 1
                    strategy['retry_count'] = 5
                
                elif 'rate limit' in error_msg:
                    strategy['delay'] = 10
                    strategy['retry_count'] = 2
            
            return strategy
            
        except Exception as e:
            logger.error(f"Error adapting scraping strategy: {e}")
            return {
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'delay': 2,
                'use_proxy': False,
                'retry_count': 3
            }
    
    def analyze_performance_metrics(self) -> Dict:
        """Analyze platform performance and user engagement"""
        try:
            # Get recent analytics data
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            
            analytics = Analytics.query\
                .filter(Analytics.created_at >= thirty_days_ago)\
                .all()
            
            # Calculate metrics
            total_views = sum(a.metric_value for a in analytics if a.metric_type == 'view')
            total_stories = Story.query.filter_by(status='published').count()
            
            # Get category performance
            category_stats = {}
            stories = Story.query.filter_by(status='published').all()
            
            for story in stories:
                if story.category not in category_stats:
                    category_stats[story.category] = {
                        'count': 0,
                        'total_views': 0,
                        'avg_engagement': 0
                    }
                
                category_stats[story.category]['count'] += 1
                category_stats[story.category]['total_views'] += story.views
                category_stats[story.category]['avg_engagement'] += story.engagement_score
            
            # Calculate averages
            for category in category_stats:
                stats = category_stats[category]
                if stats['count'] > 0:
                    stats['avg_views'] = stats['total_views'] / stats['count']
                    stats['avg_engagement'] = stats['avg_engagement'] / stats['count']
            
            return {
                'total_views': total_views,
                'total_stories': total_stories,
                'avg_views_per_story': total_views / total_stories if total_stories > 0 else 0,
                'category_performance': category_stats,
                'top_performing_categories': sorted(
                    category_stats.items(), 
                    key=lambda x: x[1]['avg_views'], 
                    reverse=True
                )[:5]
            }
            
        except Exception as e:
            logger.error(f"Error analyzing performance metrics: {e}")
            return {
                'total_views': 0,
                'total_stories': 0,
                'avg_views_per_story': 0,
                'category_performance': {},
                'top_performing_categories': []
            }



