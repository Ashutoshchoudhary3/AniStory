


















import google.generativeai as genai
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from config import Config
import re
from textblob import TextBlob

logger = logging.getLogger(__name__)

@dataclass
class ContentAnalysis:
    """Structured content analysis results"""
    category: str
    quality_score: float
    relevance_score: float
    engagement_potential: float
    sentiment: str
    sentiment_score: float
    key_entities: List[str]
    key_topics: List[str]
    story_potential: float
    target_audience: str
    content_length: int
    readability_score: float
    emotional_appeal: float
    trending_keywords: List[str]
    geographic_relevance: str
    time_sensitivity: str
    content_hash: str

class ContentAnalyzer:
    """
    Advanced content analyzer using Gemini AI to evaluate news articles and trends
    for story generation potential
    """
    
    def __init__(self):
        self.model = None
        self.is_initialized = False
        
        # Analysis configuration
        self.config = {
            'min_content_length': 100,
            'max_content_length': 10000,
            'quality_threshold': 0.6,
            'relevance_threshold': 0.5,
            'engagement_threshold': 0.4,
            'sentiment_categories': ['positive', 'negative', 'neutral', 'mixed'],
            'content_categories': ['technology', 'business', 'politics', 'sports', 'entertainment', 'science', 'world', 'health', 'environment'],
            'target_audiences': ['general', 'tech-savvy', 'business', 'young-adults', 'global', 'regional'],
            'time_sensitivity_levels': ['breaking', 'trending', 'evergreen', 'outdated'],
            'geographic_relevance_levels': ['global', 'continental', 'national', 'regional', 'local']
        }
    
    async def initialize(self):
        """Initialize the content analyzer with Gemini API"""
        try:
            genai.configure(api_key=Config.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
            self.is_initialized = True
            logger.info("Content analyzer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize content analyzer: {e}")
            raise
    
    async def analyze_article(self, article_data: Dict) -> Dict:
        """
        Analyze a news article for story generation potential
        
        Args:
            article_data: Dictionary containing article information
            
        Returns:
            Content analysis results
        """
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # Extract article content
            title = article_data.get('title', '')
            description = article_data.get('description', '')
            content = article_data.get('content', '')
            url = article_data.get('url', '')
            published_at = article_data.get('publishedAt', '')
            source = article_data.get('source', {}).get('name', 'Unknown')
            
            # Combine content for analysis
            full_content = f"{title}\n\n{description}\n\n{content}"
            
            # Basic content validation
            if len(full_content.strip()) < self.config['min_content_length']:
                logger.warning(f"Article too short for analysis: {len(full_content)} characters")
                return self._create_empty_analysis()
            
            # Perform comprehensive analysis
            analysis = await self._perform_comprehensive_analysis(full_content, article_data)
            
            logger.info(f"Analyzed article: {title[:50]}... - Quality: {analysis['quality_score']:.2f}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing article: {e}")
            return self._create_error_analysis(str(e))
    
    async def analyze_trend(self, trend_data: Dict) -> Dict:
        """
        Analyze a trending topic for story generation potential
        
        Args:
            trend_data: Dictionary containing trend information
            
        Returns:
            Content analysis results
        """
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # Extract trend data
            trend_name = trend_data.get('name', '')
            trend_query = trend_data.get('query', '')
            trend_score = trend_data.get('trend_score', 0)
            related_queries = trend_data.get('related_queries', [])
            traffic_volume = trend_data.get('traffic_volume', 0)
            
            # Create content from trend data
            trend_content = self._create_trend_content(trend_name, trend_query, related_queries)
            
            # Perform analysis
            analysis = await self._perform_trend_analysis(trend_content, trend_data)
            
            logger.info(f"Analyzed trend: {trend_name} - Score: {analysis['story_potential']:.2f}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing trend: {e}")
            return self._create_error_analysis(str(e))
    
    async def _perform_comprehensive_analysis(self, content: str, metadata: Dict) -> Dict:
        """Perform comprehensive content analysis using multiple techniques"""
        
        # Basic text analysis
        basic_analysis = self._perform_basic_text_analysis(content)
        
        # AI-powered analysis
        ai_analysis = await self._perform_ai_analysis(content, metadata)
        
        # Sentiment analysis
        sentiment_analysis = self._perform_sentiment_analysis(content)
        
        # Entity extraction
        entity_analysis = await self._perform_entity_extraction(content)
        
        # Trending keyword analysis
        keyword_analysis = await self._perform_keyword_analysis(content)
        
        # Combine all analyses
        combined_analysis = {
            'category': ai_analysis['category'],
            'quality_score': self._calculate_quality_score(basic_analysis, ai_analysis),
            'relevance_score': ai_analysis['relevance_score'],
            'engagement_potential': self._calculate_engagement_potential(basic_analysis, ai_analysis, sentiment_analysis),
            'sentiment': sentiment_analysis['sentiment'],
            'sentiment_score': sentiment_analysis['sentiment_score'],
            'key_entities': entity_analysis['entities'],
            'key_topics': ai_analysis['key_topics'],
            'story_potential': ai_analysis['story_potential'],
            'target_audience': ai_analysis['target_audience'],
            'content_length': basic_analysis['content_length'],
            'readability_score': basic_analysis['readability_score'],
            'emotional_appeal': sentiment_analysis['emotional_appeal'],
            'trending_keywords': keyword_analysis['trending_keywords'],
            'geographic_relevance': ai_analysis['geographic_relevance'],
            'time_sensitivity': ai_analysis['time_sensitivity'],
            'content_hash': basic_analysis['content_hash'],
            'analysis_timestamp': datetime.utcnow().isoformat()
        }
        
        return combined_analysis
    
    async def _perform_ai_analysis(self, content: str, metadata: Dict) -> Dict:
        """Perform AI-powered content analysis"""
        
        prompt = f"""
        Analyze this news content for story generation potential:
        
        Content:
        {content[:2000]}  # Limit content length for API
        
        Metadata:
        - Title: {metadata.get('title', 'N/A')}
        - Source: {metadata.get('source', {}).get('name', 'N/A')}
        - Published Date: {metadata.get('publishedAt', 'N/A')}
        - URL: {metadata.get('url', 'N/A')}
        
        Provide a detailed analysis in JSON format with these fields:
        {{
            "category": "one of: technology, business, politics, sports, entertainment, science, world, health, environment",
            "relevance_score": "float 0-1, how relevant is this content to current global interests",
            "story_potential": "float 0-1, how suitable is this for creating an engaging story",
            "key_topics": ["list of main topics discussed"],
            "target_audience": "one of: general, tech-savvy, business, young-adults, global, regional",
            "geographic_relevance": "one of: global, continental, national, regional, local",
            "time_sensitivity": "one of: breaking, trending, evergreen, outdated",
            "narrative_angles": ["suggested narrative angles for storytelling"],
            "visual_elements": ["suggested visual elements for images"],
            "emotional_tone": "primary emotional tone of the content",
            "complexity_level": "simple, moderate, or complex",
            "cultural_sensitivity": "any cultural considerations",
            "controversy_level": "low, medium, or high"
        }}
        
        Be specific and provide actionable insights for story creation.
        """
        
        try:
            response = await self.model.generate_content(prompt)
            analysis_data = self._extract_json_from_response(response.text)
            
            # Validate and normalize AI analysis
            normalized_analysis = self._normalize_ai_analysis(analysis_data)
            
            return normalized_analysis
            
        except Exception as e:
            logger.error(f"Error in AI analysis: {e}")
            return self._get_default_ai_analysis()
    
    def _perform_basic_text_analysis(self, content: str) -> Dict:
        """Perform basic text analysis"""
        
        # Content length
        content_length = len(content)
        
        # Word count
        words = content.split()
        word_count = len(words)
        
        # Sentence count
        sentences = re.split(r'[.!?]+', content)
        sentence_count = len([s for s in sentences if s.strip()])
        
        # Average word length
        avg_word_length = sum(len(word) for word in words) / word_count if word_count > 0 else 0
        
        # Average sentence length
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
        
        # Readability score (simplified Flesch Reading Ease)
        readability_score = self._calculate_readability_score(word_count, sentence_count, content_length)
        
        # Content hash
        import hashlib
        content_hash = hashlib.md5(content.encode()).hexdigest()
        
        return {
            'content_length': content_length,
            'word_count': word_count,
            'sentence_count': sentence_count,
            'avg_word_length': avg_word_length,
            'avg_sentence_length': avg_sentence_length,
            'readability_score': readability_score,
            'content_hash': content_hash
        }
    
    def _perform_sentiment_analysis(self, content: str) -> Dict:
        """Perform sentiment analysis using TextBlob"""
        try:
            blob = TextBlob(content)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # Determine sentiment category
            if polarity > 0.1:
                sentiment = 'positive'
            elif polarity < -0.1:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            # Calculate emotional appeal
            emotional_appeal = abs(polarity) * subjectivity
            
            return {
                'sentiment': sentiment,
                'sentiment_score': polarity,
                'subjectivity': subjectivity,
                'emotional_appeal': emotional_appeal
            }
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return {
                'sentiment': 'neutral',
                'sentiment_score': 0.0,
                'subjectivity': 0.0,
                'emotional_appeal': 0.0
            }
    
    async def _perform_entity_extraction(self, content: str) -> Dict:
        """Extract key entities from content"""
        
        prompt = f"""
        Extract key entities from this text:
        
        {content[:1000]}
        
        Return JSON with these fields:
        {{
            "entities": ["list of important people, places, organizations, events"],
            "key_names": ["specific names mentioned"],
            "locations": ["geographic locations"],
            "organizations": ["companies, institutions, groups"],
            "events": ["specific events or incidents"]
        }}
        
        Focus on entities that would be important for creating a visual story.
        """
        
        try:
            response = await self.model.generate_content(prompt)
            entity_data = self._extract_json_from_response(response.text)
            
            # Flatten entities list
            all_entities = []
            for category in ['entities', 'key_names', 'locations', 'organizations', 'events']:
                if category in entity_data:
                    all_entities.extend(entity_data[category])
            
            return {
                'entities': list(set(all_entities))[:20]  # Limit to top 20
            }
            
        except Exception as e:
            logger.error(f"Error in entity extraction: {e}")
            return {'entities': []}
    
    async def _perform_keyword_analysis(self, content: str) -> Dict:
        """Analyze trending keywords in content"""
        
        prompt = f"""
        Identify trending keywords and phrases in this text:
        
        {content[:1000]}
        
        Return JSON with:
        {{
            "trending_keywords": ["list of keywords that are currently trending or likely to trend"],
            "hashtags": ["suggested hashtags for social media"],
            "search_terms": ["terms people might search for"],
            "viral_potential": "high, medium, or low"
        }}
        
        Focus on keywords that would help the content go viral or trend.
        """
        
        try:
            response = await self.model.generate_content(prompt)
            keyword_data = self._extract_json_from_response(response.text)
            
            return {
                'trending_keywords': keyword_data.get('trending_keywords', [])[:15],
                'hashtags': keyword_data.get('hashtags', [])[:10],
                'search_terms': keyword_data.get('search_terms', [])[:10],
                'viral_potential': keyword_data.get('viral_potential', 'medium')
            }
            
        except Exception as e:
            logger.error(f"Error in keyword analysis: {e}")
            return {
                'trending_keywords': [],
                'hashtags': [],
                'search_terms': [],
                'viral_potential': 'medium'
            }
    
    def _perform_trend_analysis(self, trend_content: str, trend_data: Dict) -> Dict:
        """Perform analysis specifically for trending topics"""
        
        # Base analysis on trend score
        trend_score = trend_data.get('trend_score', 0)
        traffic_volume = trend_data.get('traffic_volume', 0)
        
        # Calculate story potential based on trend metrics
        story_potential = min((trend_score + traffic_volume / 1000) / 200, 1.0)
        
        # Determine category based on trend name
        category = self._categorize_trend(trend_data.get('name', ''))
        
        return {
            'category': category,
            'quality_score': 0.8,  # Trends are generally high quality
            'relevance_score': min(trend_score / 100, 1.0),
            'engagement_potential': story_potential,
            'sentiment': 'neutral',
            'sentiment_score': 0.0,
            'key_entities': [trend_data.get('name', '')],
            'key_topics': [trend_data.get('name', '')],
            'story_potential': story_potential,
            'target_audience': 'general',
            'content_length': len(trend_content),
            'readability_score': 0.7,
            'emotional_appeal': 0.5,
            'trending_keywords': [trend_data.get('name', '')],
            'geographic_relevance': 'global',
            'time_sensitivity': 'trending',
            'content_hash': hashlib.md5(trend_content.encode()).hexdigest(),
            'analysis_timestamp': datetime.utcnow().isoformat()
        }
    
    def _create_trend_content(self, trend_name: str, trend_query: str, related_queries: List[str]) -> str:
        """Create content from trend data"""
        content_parts = [f"Trending: {trend_name}"]
        
        if trend_query:
            content_parts.append(f"Search query: {trend_query}")
        
        if related_queries:
            content_parts.append(f"Related searches: {', '.join(related_queries[:5])}")
        
        return ' '.join(content_parts)
    
    def _calculate_quality_score(self, basic_analysis: Dict, ai_analysis: Dict) -> float:
        """Calculate overall quality score"""
        scores = []
        
        # Content length score
        length_score = min(basic_analysis['content_length'] / 2000, 1.0)
        scores.append(length_score)
        
        # Readability score
        scores.append(basic_analysis['readability_score'])
        
        # AI quality score
        scores.append(ai_analysis.get('quality_score', 0.7))
        
        # Return average
        return sum(scores) / len(scores)
    
    def _calculate_engagement_potential(self, basic_analysis: Dict, ai_analysis: Dict, sentiment_analysis: Dict) -> float:
        """Calculate engagement potential score"""
        scores = []
        
        # Emotional appeal score
        scores.append(sentiment_analysis['emotional_appeal'])
        
        # Content length score (optimal length)
        optimal_length = 1500
        length_diff = abs(basic_analysis['content_length'] - optimal_length)
        length_score = max(0, 1 - (length_diff / optimal_length))
        scores.append(length_score)
        
        # AI engagement score
        scores.append(ai_analysis.get('engagement_potential', 0.5))
        
        # Return average
        return sum(scores) / len(scores)
    
    def _calculate_readability_score(self, word_count: int, sentence_count: int, content_length: int) -> float:
        """Calculate simplified readability score"""
        if sentence_count == 0 or word_count == 0:
            return 0.5
        
        # Average sentence length
        avg_sentence_length = word_count / sentence_count
        
        # Simplified score (lower is better for readability)
        if avg_sentence_length <= 15:
            return 0.9
        elif avg_sentence_length <= 20:
            return 0.7
        elif avg_sentence_length <= 25:
            return 0.5
        else:
            return 0.3
    
    def _categorize_trend(self, trend_name: str) -> str:
        """Categorize trend based on name"""
        trend_lower = trend_name.lower()
        
        # Technology keywords
        tech_keywords = ['tech', 'ai', 'artificial intelligence', 'robot', 'software', 'app', 'digital', 'cyber', 'blockchain', 'crypto', 'metaverse', 'vr', 'ar']
        if any(keyword in trend_lower for keyword in tech_keywords):
            return 'technology'
        
        # Business keywords
        business_keywords = ['stock', 'market', 'economy', 'business', 'company', 'finance', 'investment', 'trade', 'price']
        if any(keyword in trend_lower for keyword in business_keywords):
            return 'business'
        
        # Politics keywords
        politics_keywords = ['election', 'president', 'government', 'politics', 'vote', 'campaign', 'policy', 'law']
        if any(keyword in trend_lower for keyword in politics_keywords):
            return 'politics'
        
        # Sports keywords
        sports_keywords = ['football', 'basketball', 'soccer', 'tennis', 'game', 'match', 'team', 'player', 'championship', 'olympics']
        if any(keyword in trend_lower for keyword in sports_keywords):
            return 'sports'
        
        # Entertainment keywords
        entertainment_keywords = ['movie', 'film', 'music', 'celebrity', 'actor', 'singer', 'album', 'concert', 'show', 'netflix']
        if any(keyword in trend_lower for keyword in entertainment_keywords):
            return 'entertainment'
        
        # Science keywords
        science_keywords = ['science', 'research', 'study', 'discovery', 'space', 'nasa', 'climate', 'environment', 'health', 'medical']
        if any(keyword in trend_lower for keyword in science_keywords):
            return 'science'
        
        return 'world'  # Default category
    
    def _extract_json_from_response(self, response_text: str) -> Dict:
        """Extract JSON from AI response"""
        try:
            # Look for JSON in the response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # Try to parse the entire response as JSON
                return json.loads(response_text)
        except Exception as e:
            logger.error(f"Error extracting JSON from response: {e}")
            return {}
    
    def _normalize_ai_analysis(self, analysis_data: Dict) -> Dict:
        """Normalize and validate AI analysis data"""
        return {
            'category': analysis_data.get('category', 'world'),
            'relevance_score': float(analysis_data.get('relevance_score', 0.5)),
            'story_potential': float(analysis_data.get('story_potential', 0.5)),
            'key_topics': analysis_data.get('key_topics', []),
            'target_audience': analysis_data.get('target_audience', 'general'),
            'geographic_relevance': analysis_data.get('geographic_relevance', 'global'),
            'time_sensitivity': analysis_data.get('time_sensitivity', 'trending'),
            'narrative_angles': analysis_data.get('narrative_angles', []),
            'visual_elements': analysis_data.get('visual_elements', []),
            'emotional_tone': analysis_data.get('emotional_tone', 'neutral'),
            'complexity_level': analysis_data.get('complexity_level', 'moderate'),
            'cultural_sensitivity': analysis_data.get('cultural_sensitivity', 'none'),
            'controversy_level': analysis_data.get('controversy_level', 'low')
        }
    
    def _get_default_ai_analysis(self) -> Dict:
        """Get default AI analysis when analysis fails"""
        return {
            'category': 'world',
            'relevance_score': 0.5,
            'story_potential': 0.5,
            'key_topics': [],
            'target_audience': 'general',
            'geographic_relevance': 'global',
            'time_sensitivity': 'trending',
            'narrative_angles': ['informative'],
            'visual_elements': ['generic illustration'],
            'emotional_tone': 'neutral',
            'complexity_level': 'moderate',
            'cultural_sensitivity': 'none',
            'controversy_level': 'low'
        }
    
    def _create_empty_analysis(self) -> Dict:
        """Create empty analysis for insufficient content"""
        return {
            'category': 'unknown',
            'quality_score': 0.0,
            'relevance_score': 0.0,
            'engagement_potential': 0.0,
            'sentiment': 'neutral',
            'sentiment_score': 0.0,
            'key_entities': [],
            'key_topics': [],
            'story_potential': 0.0,
            'target_audience': 'general',
            'content_length': 0,
            'readability_score': 0.0,
            'emotional_appeal': 0.0,
            'trending_keywords': [],
            'geographic_relevance': 'unknown',
            'time_sensitivity': 'unknown',
            'content_hash': '',
            'analysis_timestamp': datetime.utcnow().isoformat()
        }
    
    def _create_error_analysis(self, error_message: str) -> Dict:
        """Create error analysis when analysis fails"""
        return {
            'category': 'error',
            'quality_score': 0.0,
            'relevance_score': 0.0,
            'engagement_potential': 0.0,
            'sentiment': 'neutral',
            'sentiment_score': 0.0,
            'key_entities': [],
            'key_topics': [],
            'story_potential': 0.0,
            'target_audience': 'general',
            'content_length': 0,
            'readability_score': 0.0,
            'emotional_appeal': 0.0,
            'trending_keywords': [],
            'geographic_relevance': 'unknown',
            'time_sensitivity': 'unknown',
            'content_hash': '',
            'analysis_timestamp': datetime.utcnow().isoformat(),
            'error': error_message
        }

# Example usage
async def example_usage():
    analyzer = ContentAnalyzer()
    
    try:
        await analyzer.initialize()
        
        # Example article
        article_data = {
            'title': 'Revolutionary AI Breakthrough in Medical Diagnosis',
            'description': 'Scientists develop new AI system that can diagnose rare diseases with 99% accuracy',
            'content': 'In a groundbreaking development, researchers at Stanford University have created an artificial intelligence system capable of diagnosing rare medical conditions with unprecedented accuracy. The system, trained on millions of medical records and images, can identify patterns that human doctors often miss. This breakthrough could revolutionize healthcare by enabling earlier detection of life-threatening conditions and reducing misdiagnosis rates significantly.',
            'url': 'https://example.com/ai-medical-breakthrough',
            'publishedAt': '2024-01-15T10:00:00Z',
            'source': {'name': 'Tech News Daily'}
        }
        
        # Analyze article
        analysis = await analyzer.analyze_article(article_data)
        print(f"Article Analysis:")
        print(f"Category: {analysis['category']}")
        print(f"Quality Score: {analysis['quality_score']:.2f}")
        print(f"Story Potential: {analysis['story_potential']:.2f}")
        print(f"Key Topics: {analysis['key_topics']}")
        print(f"Sentiment: {analysis['sentiment']}")
        
        # Example trend
        trend_data = {
            'name': 'AI Medical Diagnosis',
            'query': 'AI medical diagnosis breakthrough',
            'trend_score': 85.0,
            'traffic_volume': 50000,
            'related_queries': ['AI healthcare', 'medical AI', 'diagnosis technology']
        }
        
        # Analyze trend
        trend_analysis = await analyzer.analyze_trend(trend_data)
        print(f"\nTrend Analysis:")
        print(f"Category: {trend_analysis['category']}")
        print(f"Story Potential: {trend_analysis['story_potential']:.2f}")
        print(f"Relevance Score: {trend_analysis['relevance_score']:.2f}")
        
    except Exception as e:
        print(f"Error in example usage: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())


















