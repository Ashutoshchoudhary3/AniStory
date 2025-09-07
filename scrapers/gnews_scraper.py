









import requests
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from config import Config
import logging

logger = logging.getLogger(__name__)

class GNewsScraper:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or Config.GNEWS_API_KEY
        self.base_url = "https://gnews.io/api/v4"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ChronoStories/1.0 (AI News Story Generator)'
        })
        
        if not self.api_key:
            logger.warning("GNews API key not provided. Using demo mode with limited functionality.")
    
    def search_news(self, 
                   query: str = None,
                   country: str = None,
                   language: str = 'en',
                   max_results: int = 10,
                   from_date: datetime = None,
                   to_date: datetime = None,
                   category: str = None) -> List[Dict]:
        """
        Search for news articles using GNews API
        
        Args:
            query: Search query (optional)
            country: Country code (e.g., 'us', 'gb', 'jp')
            language: Language code (default: 'en')
            max_results: Maximum number of results (max: 100)
            from_date: Start date for search
            to_date: End date for search
            category: News category (general, world, nation, business, technology, etc.)
        
        Returns:
            List of news articles
        """
        if not self.api_key:
            logger.error("GNews API key is required for searching news")
            return []
        
        params = {
            'apikey': self.api_key,
            'lang': language,
            'max': min(max_results, 100),  # API limit
        }
        
        if query:
            params['q'] = query
        
        if country:
            params['country'] = country
        
        if category:
            params['category'] = category
        
        if from_date:
            params['from'] = from_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        if to_date:
            params['to'] = to_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        try:
            response = self.session.get(f"{self.base_url}/search", params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            articles = data.get('articles', [])
            
            logger.info(f"Retrieved {len(articles)} articles from GNews")
            return self._process_articles(articles, country)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching news from GNews: {e}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing GNews response: {e}")
            return []
    
    def get_top_news(self, 
                    country: str = None,
                    language: str = 'en',
                    max_results: int = 10,
                    category: str = None) -> List[Dict]:
        """
        Get top news headlines
        
        Args:
            country: Country code
            language: Language code
            max_results: Maximum number of results
            category: News category
        
        Returns:
            List of top news articles
        """
        return self.search_news(
            country=country,
            language=language,
            max_results=max_results,
            category=category
        )
    
    def monitor_breaking_news(self, 
                             countries: List[str] = None,
                             check_interval: int = 300) -> List[Dict]:
        """
        Monitor for breaking news by comparing with previous results
        
        Args:
            countries: List of country codes to monitor
            check_interval: Time in seconds between checks
        
        Returns:
            List of new breaking news articles
        """
        if countries is None:
            countries = Config.SUPPORTED_COUNTRIES
        
        breaking_news = []
        seen_articles = set()
        
        # Load previously seen articles from cache
        try:
            with open('gnews_cache.json', 'r') as f:
                cache = json.load(f)
                seen_articles = set(cache.get('seen_articles', []))
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        
        for country in countries:
            try:
                # Get recent news for this country
                recent_news = self.get_top_news(
                    country=country,
                    max_results=20,
                    from_date=datetime.utcnow() - timedelta(hours=2)
                )
                
                for article in recent_news:
                    article_id = self._generate_article_id(article)
                    
                    # Check if this is a new article
                    if article_id not in seen_articles:
                        # Check if it's breaking news (published within last hour)
                        published_at = self._parse_date(article.get('publishedAt'))
                        if published_at and (datetime.utcnow() - published_at) < timedelta(hours=1):
                            article['is_breaking'] = True
                            article['country'] = country
                            breaking_news.append(article)
                        
                        seen_articles.add(article_id)
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error monitoring {country} news: {e}")
                continue
        
        # Save updated cache
        try:
            with open('gnews_cache.json', 'w') as f:
                json.dump({
                    'seen_articles': list(seen_articles),
                    'last_updated': datetime.utcnow().isoformat()
                }, f)
        except Exception as e:
            logger.error(f"Error saving GNews cache: {e}")
        
        logger.info(f"Found {len(breaking_news)} breaking news articles")
        return breaking_news
    
    def _process_articles(self, articles: List[Dict], country: str = None) -> List[Dict]:
        """Process and normalize article data"""
        processed_articles = []
        
        for article in articles:
            try:
                processed_article = {
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'content': article.get('content', ''),
                    'url': article.get('url', ''),
                    'image': article.get('image', ''),
                    'published_at': article.get('publishedAt', ''),
                    'source': {
                        'name': article.get('source', {}).get('name', ''),
                        'url': article.get('source', {}).get('url', '')
                    },
                    'country': country,
                    'language': article.get('lang', 'en'),
                    'scraped_at': datetime.utcnow().isoformat()
                }
                
                # Extract category from source or content
                processed_article['category'] = self._categorize_article(processed_article)
                
                # Calculate relevance score
                processed_article['relevance_score'] = self._calculate_relevance_score(processed_article)
                
                processed_articles.append(processed_article)
                
            except Exception as e:
                logger.error(f"Error processing article: {e}")
                continue
        
        return processed_articles
    
    def _categorize_article(self, article: Dict) -> str:
        """Categorize article based on content and source"""
        title_desc = f"{article['title']} {article['description']}".lower()
        
        categories = {
            'technology': ['tech', 'ai', 'software', 'hardware', 'internet', 'cyber', 'digital', 'app'],
            'business': ['business', 'economy', 'market', 'finance', 'stock', 'company', 'corporate'],
            'politics': ['politics', 'government', 'election', 'policy', 'law', 'political'],
            'sports': ['sports', 'game', 'team', 'player', 'match', 'tournament', 'championship'],
            'entertainment': ['movie', 'film', 'music', 'celebrity', 'entertainment', 'show', 'actor'],
            'health': ['health', 'medical', 'disease', 'vaccine', 'hospital', 'doctor'],
            'science': ['science', 'research', 'study', 'discovery', 'scientist', 'experiment'],
            'world': ['international', 'global', 'world', 'foreign', 'diplomatic']
        }
        
        for category, keywords in categories.items():
            if any(keyword in title_desc for keyword in keywords):
                return category
        
        return 'general'
    
    def _calculate_relevance_score(self, article: Dict) -> float:
        """Calculate relevance score for story generation"""
        score = 0.0
        
        # Length score
        content_length = len(article.get('content', ''))
        if content_length > 1000:
            score += 0.3
        elif content_length > 500:
            score += 0.2
        elif content_length > 200:
            score += 0.1
        
        # Source credibility score
        source_name = article.get('source', {}).get('name', '').lower()
        credible_sources = ['reuters', 'ap', 'associated press', 'bbc', 'cnn', 'guardian', 'times']
        if any(source in source_name for source in credible_sources):
            score += 0.3
        
        # Recency score
        published_at = self._parse_date(article.get('published_at'))
        if published_at:
            hours_old = (datetime.utcnow() - published_at).total_seconds() / 3600
            if hours_old < 6:
                score += 0.4
            elif hours_old < 24:
                score += 0.2
        
        return min(score, 1.0)
    
    def _generate_article_id(self, article: Dict) -> str:
        """Generate unique ID for article"""
        title = article.get('title', '')
        source = article.get('source', {}).get('name', '')
        published_at = article.get('publishedAt', '')
        return f"{title}|{source}|{published_at}"
    
    def _parse_date(self, date_string: str) -> Optional[datetime]:
        """Parse ISO date string to datetime object"""
        if not date_string:
            return None
        
        try:
            return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            try:
                return datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%SZ')
            except ValueError:
                logger.error(f"Could not parse date: {date_string}")
                return None

# Example usage
if __name__ == "__main__":
    scraper = GNewsScraper()
    
    # Search for recent tech news
    tech_news = scraper.search_news(
        query="artificial intelligence",
        category="technology",
        max_results=5
    )
    
    print(f"Found {len(tech_news)} tech news articles")
    for article in tech_news:
        print(f"- {article['title']}")









