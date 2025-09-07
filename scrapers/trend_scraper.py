

















import asyncio
import json
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import requests
from config import Config

logger = logging.getLogger(__name__)

class TrendScraper:
    def __init__(self):
        self.playwright_manager = None
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # Trend sources configuration
        self.trend_sources = {
            'google_trends': {
                'url': 'https://trends.google.com/trends/trendingsearches/daily/rss',
                'method': 'rss',
                'countries': Config.SUPPORTED_COUNTRIES
            },
            'google_trends_explore': {
                'url': 'https://trends.google.com/trends/explore',
                'method': 'playwright',
                'countries': ['us', 'gb', 'jp', 'de', 'fr']
            },
            'reddit': {
                'url': 'https://www.reddit.com/r/popular.json',
                'method': 'api',
                'subreddits': ['worldnews', 'technology', 'science', 'politics', 'entertainment']
            },
            'twitter_trends': {
                'url': 'https://twitter.com/i/api/2/guide.json',
                'method': 'api',
                'countries': ['us', 'gb', 'jp']
            }
        }
    
    async def initialize(self):
        """Initialize Playwright manager"""
        if not self.playwright_manager:
            self.playwright_manager = PlaywrightManager()
            await self.playwright_manager.initialize()
    
    async def scrape_all_trends(self, countries: List[str] = None) -> List[Dict]:
        """
        Scrape trends from all configured sources
        
        Args:
            countries: List of country codes to scrape trends for
            
        Returns:
            List of trend data
        """
        if countries is None:
            countries = Config.SUPPORTED_COUNTRIES
        
        all_trends = []
        
        # Scrape Google Trends RSS
        trends = await self._scrape_google_trends_rss(countries)
        all_trends.extend(trends)
        
        # Scrape Google Trends Explore (requires Playwright)
        trends = await self._scrape_google_trends_explore(countries)
        all_trends.extend(trends)
        
        # Scrape Reddit trends
        trends = await self._scrape_reddit_trends()
        all_trends.extend(trends)
        
        # Scrape Twitter trends (if possible)
        trends = await self._scrape_twitter_trends(countries)
        all_trends.extend(trends)
        
        # Remove duplicates and sort by trend score
        unique_trends = self._deduplicate_trends(all_trends)
        unique_trends.sort(key=lambda x: x.get('trend_score', 0), reverse=True)
        
        logger.info(f"Scraped {len(unique_trends)} unique trends from all sources")
        return unique_trends
    
    async def _scrape_google_trends_rss(self, countries: List[str]) -> List[Dict]:
        """Scrape Google Trends RSS feeds"""
        trends = []
        
        for country in countries:
            try:
                url = f"https://trends.google.com/trends/trendingsearches/daily/rss?geo={country.upper()}"
                response = self.session.get(url, timeout=30)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'xml')
                    items = soup.find_all('item')
                    
                    for item in items[:10]:  # Limit to top 10 trends per country
                        try:
                            title = item.find('title').text if item.find('title') else ''
                            description = item.find('description').text if item.find('description') else ''
                            pub_date = item.find('pubDate').text if item.find('pubDate') else ''
                            
                            # Extract traffic information
                            traffic_match = self._extract_traffic_info(description)
                            
                            trend = {
                                'keyword': title,
                                'display_keyword': title,
                                'source': 'google_trends_rss',
                                'source_url': item.find('link').text if item.find('link') else '',
                                'country': country,
                                'volume': traffic_match.get('volume', 0),
                                'growth_rate': traffic_match.get('growth_rate', 0),
                                'category': self._categorize_trend(title),
                                'discovered_at': datetime.utcnow(),
                                'trend_started_at': self._parse_trend_date(pub_date),
                                'sentiment': self._analyze_sentiment(title),
                                'trend_score': 0.0,
                                'is_breaking': False,
                                'entities': self._extract_entities(title),
                                'hashtags': self._extract_hashtags(title),
                                'status': 'new',
                                'priority': 1
                            }
                            
                            trend['trend_score'] = self._calculate_trend_score(trend)
                            trends.append(trend)
                            
                        except Exception as e:
                            logger.error(f"Error processing Google Trends RSS item: {e}")
                            continue
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error scraping Google Trends RSS for {country}: {e}")
                continue
        
        logger.info(f"Scraped {len(trends)} trends from Google Trends RSS")
        return trends
    
    async def _scrape_google_trends_explore(self, countries: List[str]) -> List[Dict]:
        """Scrape Google Trends Explore page using Playwright"""
        if not self.playwright_manager:
            await self.initialize()
        
        trends = []
        
        for country in countries:
            try:
                url = f"https://trends.google.com/trends/explore?geo={country.upper()}"
                
                # Use Playwright to scrape dynamic content
                page_content = await self.playwright_manager.scrape_page(url, wait_for='.fe-related-queries')
                
                if page_content:
                    soup = BeautifulSoup(page_content, 'html.parser')
                    
                    # Extract trending searches
                    trending_elements = soup.select('.fe-related-queries .item')
                    
                    for element in trending_elements[:10]:
                        try:
                            keyword = element.get_text(strip=True)
                            if keyword:
                                trend = {
                                    'keyword': keyword,
                                    'display_keyword': keyword,
                                    'source': 'google_trends_explore',
                                    'source_url': url,
                                    'country': country,
                                    'volume': 0,
                                    'growth_rate': 0,
                                    'category': self._categorize_trend(keyword),
                                    'discovered_at': datetime.utcnow(),
                                    'trend_started_at': datetime.utcnow(),
                                    'sentiment': self._analyze_sentiment(keyword),
                                    'trend_score': 0.0,
                                    'is_breaking': False,
                                    'entities': self._extract_entities(keyword),
                                    'hashtags': self._extract_hashtags(keyword),
                                    'status': 'new',
                                    'priority': 1
                                }
                                
                                trend['trend_score'] = self._calculate_trend_score(trend)
                                trends.append(trend)
                                
                        except Exception as e:
                            logger.error(f"Error processing Google Trends Explore item: {e}")
                            continue
                
                # Rate limiting
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Error scraping Google Trends Explore for {country}: {e}")
                continue
        
        logger.info(f"Scraped {len(trends)} trends from Google Trends Explore")
        return trends
    
    async def _scrape_reddit_trends(self) -> List[Dict]:
        """Scrape Reddit for trending topics"""
        trends = []
        
        try:
            # Scrape popular subreddits
            for subreddit in self.trend_sources['reddit']['subreddits']:
                try:
                    url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=10"
                    response = self.session.get(url, timeout=30)
                    
                    if response.status_code == 200:
                        data = response.json()
                        posts = data.get('data', {}).get('children', [])
                        
                        for post in posts:
                            try:
                                post_data = post.get('data', {})
                                title = post_data.get('title', '')
                                score = post_data.get('score', 0)
                                num_comments = post_data.get('num_comments', 0)
                                created_utc = post_data.get('created_utc', 0)
                                
                                # Calculate engagement rate
                                engagement_rate = (score + num_comments) / max(score, 1)
                                
                                trend = {
                                    'keyword': title[:100],  # Limit length
                                    'display_keyword': title,
                                    'source': f'reddit_{subreddit}',
                                    'source_url': f"https://www.reddit.com{post_data.get('permalink', '')}",
                                    'country': 'us',  # Default to US
                                    'volume': score,
                                    'growth_rate': engagement_rate * 100,
                                    'category': self._map_subreddit_to_category(subreddit),
                                    'discovered_at': datetime.utcnow(),
                                    'trend_started_at': datetime.fromtimestamp(created_utc),
                                    'sentiment': self._analyze_sentiment(title),
                                    'trend_score': 0.0,
                                    'is_breaking': score > 1000,  # High score indicates breaking
                                    'entities': self._extract_entities(title),
                                    'hashtags': self._extract_hashtags(title),
                                    'status': 'new',
                                    'priority': min(10, max(1, int(score / 100)))  # Priority based on score
                                }
                                
                                trend['trend_score'] = self._calculate_trend_score(trend)
                                trends.append(trend)
                                
                            except Exception as e:
                                logger.error(f"Error processing Reddit post: {e}")
                                continue
                    
                    # Rate limiting
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error scraping Reddit subreddit {subreddit}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error scraping Reddit trends: {e}")
        
        logger.info(f"Scraped {len(trends)} trends from Reddit")
        return trends
    
    async def _scrape_twitter_trends(self, countries: List[str]) -> List[Dict]:
        """Scrape Twitter trends (placeholder - requires API access)"""
        # Note: This is a placeholder implementation
        # Twitter API requires authentication and has rate limits
        trends = []
        
        logger.warning("Twitter scraping not implemented - requires API authentication")
        return trends
    
    def _extract_traffic_info(self, description: str) -> Dict:
        """Extract traffic volume and growth information"""
        import re
        
        traffic_info = {'volume': 0, 'growth_rate': 0}
        
        # Look for patterns like "100K+ searches" or "500% growth"
        volume_patterns = [
            r'(\d+(?:\.\d+)?)\s*K\+?\s*searches',
            r'(\d+(?:\.\d+)?)\s*M\+?\s*searches',
            r'(\d+(?:,\d+)*)\s*searches'
        ]
        
        growth_patterns = [
            r'(\d+(?:\.\d+)?)\s*%?\s*growth',
            r'(\d+(?:\.\d+)?)\s*%?\s*increase',
            r'\+(\d+(?:\.\d+)?)\s*%?'
        ]
        
        # Extract volume
        for pattern in volume_patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                value = match.group(1).replace(',', '')
                if 'K' in match.group(0):
                    traffic_info['volume'] = int(float(value) * 1000)
                elif 'M' in match.group(0):
                    traffic_info['volume'] = int(float(value) * 1000000)
                else:
                    traffic_info['volume'] = int(float(value))
                break
        
        # Extract growth rate
        for pattern in growth_patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                traffic_info['growth_rate'] = float(match.group(1))
                break
        
        return traffic_info
    
    def _categorize_trend(self, keyword: str) -> str:
        """Categorize trend based on keyword"""
        keyword_lower = keyword.lower()
        
        categories = {
            'technology': ['tech', 'ai', 'software', 'app', 'digital', 'cyber', 'internet', 'computer'],
            'business': ['business', 'market', 'economy', 'finance', 'stock', 'company'],
            'politics': ['politics', 'election', 'government', 'policy', 'president', 'vote'],
            'sports': ['sports', 'game', 'team', 'player', 'match', 'championship'],
            'entertainment': ['movie', 'music', 'celebrity', 'show', 'actor', 'entertainment'],
            'health': ['health', 'medical', 'disease', 'vaccine', 'hospital'],
            'science': ['science', 'research', 'study', 'discovery', 'space'],
            'world': ['international', 'global', 'world', 'foreign']
        }
        
        for category, keywords in categories.items():
            if any(kw in keyword_lower for kw in keywords):
                return category
        
        return 'general'
    
    def _map_subreddit_to_category(self, subreddit: str) -> str:
        """Map subreddit to trend category"""
        mapping = {
            'worldnews': 'world',
            'technology': 'technology',
            'science': 'science',
            'politics': 'politics',
            'entertainment': 'entertainment'
        }
        return mapping.get(subreddit, 'general')
    
    def _analyze_sentiment(self, text: str) -> str:
        """Simple sentiment analysis"""
        positive_words = ['good', 'great', 'amazing', 'excellent', 'positive', 'success', 'win', 'breakthrough']
        negative_words = ['bad', 'terrible', 'awful', 'negative', 'failure', 'loss', 'crisis', 'problem']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract entities from text (simple implementation)"""
        # This is a simplified implementation
        # In production, you'd use NER (Named Entity Recognition)
        import re
        
        # Extract capitalized words (potential names/organizations)
        entities = re.findall(r'\b[A-Z][a-z]+\b', text)
        
        # Extract hashtags
        hashtags = re.findall(r'#\w+', text)
        entities.extend(hashtags)
        
        return list(set(entities))[:10]  # Limit to 10 unique entities
    
    def _extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text"""
        import re
        hashtags = re.findall(r'#\w+', text)
        return hashtags
    
    def _calculate_trend_score(self, trend: Dict) -> float:
        """Calculate trend significance score"""
        score = 0.0
        
        # Volume score (0-40 points)
        volume = trend.get('volume', 0)
        if volume > 100000:
            score += 40
        elif volume > 10000:
            score += 30
        elif volume > 1000:
            score += 20
        elif volume > 100:
            score += 10
        
        # Growth rate score (0-30 points)
        growth_rate = abs(trend.get('growth_rate', 0))
        if growth_rate > 1000:
            score += 30
        elif growth_rate > 500:
            score += 25
        elif growth_rate > 100:
            score += 20
        elif growth_rate > 50:
            score += 15
        elif growth_rate > 10:
            score += 10
        
        # Breaking news bonus (0-20 points)
        if trend.get('is_breaking', False):
            score += 20
        
        # Priority bonus (0-10 points)
        priority = trend.get('priority', 1)
        score += min(priority, 10)
        
        return min(score, 100.0)  # Cap at 100
    
    def _parse_trend_date(self, date_string: str) -> Optional[datetime]:
        """Parse trend date string"""
        if not date_string:
            return datetime.utcnow()
        
        try:
            return datetime.strptime(date_string, '%a, %d %b %Y %H:%M:%S %z')
        except ValueError:
            try:
                return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            except ValueError:
                return datetime.utcnow()
    
    def _deduplicate_trends(self, trends: List[Dict]) -> List[Dict]:
        """Remove duplicate trends based on keyword and country"""
        seen = set()
        unique_trends = []
        
        for trend in trends:
            key = f"{trend['keyword'].lower()}|{trend['country']}"
            if key not in seen:
                seen.add(key)
                unique_trends.append(trend)
        
        return unique_trends

class PlaywrightManager:
    def __init__(self):
        self.browser = None
        self.context = None
    
    async def initialize(self):
        """Initialize Playwright browser"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
    
    async def scrape_page(self, url: str, wait_for: str = None, timeout: int = 30000) -> Optional[str]:
        """Scrape page content using Playwright"""
        if not self.context:
            await self.initialize()
        
        page = None
        try:
            page = await self.context.new_page()
            
            # Navigate to page
            await page.goto(url, wait_until='networkidle', timeout=timeout)
            
            # Wait for specific element if specified
            if wait_for:
                await page.wait_for_selector(wait_for, timeout=timeout)
            
            # Get page content
            content = await page.content()
            
            return content
            
        except Exception as e:
            logger.error(f"Error scraping page {url}: {e}")
            return None
            
        finally:
            if page:
                await page.close()
    
    async def close(self):
        """Close browser and cleanup"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()

# Example usage
async def main():
    scraper = TrendScraper()
    await scraper.initialize()
    
    trends = await scraper.scrape_all_trends()
    
    print(f"Found {len(trends)} trends")
    for trend in trends[:5]:
        print(f"- {trend['keyword']} (Score: {trend['trend_score']})")
    
    await scraper.playwright_manager.close()

if __name__ == "__main__":
    asyncio.run(main())

















