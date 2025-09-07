

















from playwright.async_api import async_playwright
import logging
from typing import Optional, Dict, Any
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class PlaywrightManager:
    """
    Advanced Playwright manager for autonomous web scraping
    Handles CAPTCHAs, dynamic content, and adaptive scraping
    """
    
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.is_initialized = False
        
        # Scraping configuration
        self.config = {
            'default_timeout': 30000,
            'retry_attempts': 3,
            'retry_delay': 2,
            'anti_bot_detection': True,
            'human_like_behavior': True,
            'screenshot_on_error': True,
            'user_agents': [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ]
        }
        
        # Anti-detection measures
        self.stealth_scripts = [
            # Override navigator properties
            """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            """,
            # Override plugins
            """
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            """,
            # Override languages
            """
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            """
        ]
    
    async def initialize(self, headless: bool = True, browser_type: str = 'chromium'):
        """
        Initialize Playwright browser with anti-detection measures
        
        Args:
            headless: Whether to run in headless mode
            browser_type: Type of browser (chromium, firefox, webkit)
        """
        try:
            self.playwright = await async_playwright().start()
            
            # Launch browser
            if browser_type == 'chromium':
                self.browser = await self.playwright.chromium.launch(
                    headless=headless,
                    args=[
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-blink-features=AutomationControlled',
                        '--disable-features=IsolateOrigins,site-per-process',
                        '--disable-setuid-sandbox',
                        '--disable-web-security',
                        '--disable-features=VizDisplayCompositor'
                    ]
                )
            elif browser_type == 'firefox':
                self.browser = await self.playwright.firefox.launch(
                    headless=headless,
                    args=['--no-sandbox', '--disable-dev-shm-usage']
                )
            else:
                self.browser = await self.playwright.webkit.launch(
                    headless=headless,
                    args=['--no-sandbox', '--disable-dev-shm-usage']
                )
            
            # Create context with anti-detection settings
            user_agent = self.config['user_agents'][0]  # Use first user agent
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent=user_agent,
                locale='en-US',
                timezone_id='America/New_York',
                permissions=['geolocation'],
                extra_http_headers={
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                }
            )
            
            # Add anti-detection scripts
            if self.config['anti_bot_detection']:
                await self.context.add_init_script("""
                    // Remove webdriver property
                    delete navigator.__proto__.webdriver;
                    
                    // Override plugins
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5],
                    });
                    
                    // Override languages
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['en-US', 'en'],
                    });
                    
                    // Override platform
                    Object.defineProperty(navigator, 'platform', {
                        get: () => 'Win32',
                    });
                    
                    // Add chrome runtime
                    window.chrome = {
                        runtime: {},
                    };
                    
                    // Add permissions
                    const originalQuery = window.navigator.permissions.query;
                    window.navigator.permissions.query = (parameters) => (
                        parameters.name === 'notifications' ?
                            Promise.resolve({ state: Notification.permission }) :
                            originalQuery(parameters)
                    );
                """)
            
            self.is_initialized = True
            logger.info(f"Playwright manager initialized with {browser_type}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Playwright manager: {e}")
            raise
    
    async def scrape_page(self, url: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Advanced page scraping with anti-detection and retry logic
        
        Args:
            url: URL to scrape
            wait_for: CSS selector to wait for
            timeout: Timeout in milliseconds
            wait_time: Additional wait time after page load
            screenshot: Whether to take screenshot
            cookies: Cookies to set
            headers: Additional headers
            form_data: Form data to submit
            click_selector: Selector to click before scraping
            scroll: Whether to scroll the page
            human_like_delay: Whether to add human-like delays
            
        Returns:
            Dictionary containing scraped data and metadata
        """
        if not self.is_initialized:
            await self.initialize()
        
        # Extract parameters
        wait_for = kwargs.get('wait_for')
        timeout = kwargs.get('timeout', self.config['default_timeout'])
        wait_time = kwargs.get('wait_time', 2000)
        screenshot = kwargs.get('screenshot', self.config['screenshot_on_error'])
        cookies = kwargs.get('cookies', [])
        headers = kwargs.get('headers', {})
        form_data = kwargs.get('form_data')
        click_selector = kwargs.get('click_selector')
        scroll = kwargs.get('scroll', True)
        human_like_delay = kwargs.get('human_like_delay', self.config['human_like_behavior'])
        
        page = None
        result = {
            'url': url,
            'success': False,
            'content': None,
            'title': None,
            'screenshot_path': None,
            'error': None,
            'metadata': {
                'load_time': 0,
                'redirects': 0,
                'status_code': None,
                'content_size': 0
            }
        }
        
        try:
            # Create new page
            page = await self.context.new_page()
            
            # Set additional headers if provided
            if headers:
                await page.set_extra_http_headers(headers)
            
            # Set cookies if provided
            if cookies:
                await self.context.add_cookies(cookies)
            
            # Add human-like behavior
            if human_like_delay:
                await page.add_init_script("""
                    // Random mouse movements
                    document.addEventListener('mousemove', () => {
                        window.lastMouseMove = Date.now();
                    });
                    
                    // Random scroll behavior
                    window.addEventListener('scroll', () => {
                        window.lastScroll = Date.now();
                    });
                """)
            
            start_time = datetime.utcnow()
            
            # Navigate to page
            response = await page.goto(url, wait_until='networkidle', timeout=timeout)
            
            load_time = (datetime.utcnow() - start_time).total_seconds()
            result['metadata']['load_time'] = load_time
            result['metadata']['status_code'] = response.status if response else None
            
            # Wait for specific element if specified
            if wait_for:
                await page.wait_for_selector(wait_for, timeout=timeout)
            
            # Handle form submission if provided
            if form_data:
                await self._handle_form_submission(page, form_data)
            
            # Click element if specified
            if click_selector:
                await page.click(click_selector)
                await page.wait_for_load_state('networkidle')
            
            # Scroll page if requested
            if scroll:
                await self._scroll_page(page)
            
            # Add human-like delay
            if human_like_delay:
                await asyncio.sleep(wait_time / 1000)
            
            # Get page content
            result['content'] = await page.content()
            result['title'] = await page.title()
            result['metadata']['content_size'] = len(result['content'])
            
            # Take screenshot if requested
            if screenshot:
                screenshot_path = f"screenshots/{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{hash(url) % 10000}.png"
                await page.screenshot(path=screenshot_path, full_page=True)
                result['screenshot_path'] = screenshot_path
            
            result['success'] = True
            logger.info(f"Successfully scraped {url} in {load_time:.2f}s")
            
        except Exception as e:
            error_msg = f"Error scraping {url}: {str(e)}"
            result['error'] = error_msg
            logger.error(error_msg)
            
            # Take screenshot on error for debugging
            if screenshot and page:
                try:
                    error_screenshot = f"screenshots/error_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{hash(url) % 10000}.png"
                    await page.screenshot(path=error_screenshot, full_page=True)
                    result['screenshot_path'] = error_screenshot
                except:
                    pass
        
        finally:
            if page:
                await page.close()
        
        return result
    
    async def _handle_form_submission(self, page, form_data: Dict[str, Any]):
        """Handle form submission with anti-detection measures"""
        try:
            # Fill form fields
            for selector, value in form_data.get('fields', {}).items():
                await page.fill(selector, value)
                if self.config['human_like_behavior']:
                    await asyncio.sleep(0.5)  # Human-like typing delay
            
            # Submit form
            submit_selector = form_data.get('submit_selector', 'button[type="submit"]')
            await page.click(submit_selector)
            
            # Wait for navigation
            await page.wait_for_load_state('networkidle')
            
        except Exception as e:
            logger.error(f"Error handling form submission: {e}")
            raise
    
    async def _scroll_page(self, page):
        """Scroll page to load dynamic content"""
        try:
            # Get page height
            page_height = await page.evaluate('document.body.scrollHeight')
            
            # Scroll in increments
            scroll_increment = page_height // 3
            for i in range(1, 4):
                scroll_position = min(scroll_increment * i, page_height)
                await page.evaluate(f'window.scrollTo(0, {scroll_position})')
                
                if self.config['human_like_behavior']:
                    await asyncio.sleep(0.5)  # Human-like scroll delay
            
            # Scroll back to top
            await page.evaluate('window.scrollTo(0, 0)')
            
        except Exception as e:
            logger.error(f"Error scrolling page: {e}")
    
    async def solve_captcha(self, page, captcha_selector: str) -> bool:
        """
        Attempt to solve CAPTCHA (basic implementation)
        
        Args:
            page: Playwright page object
            captcha_selector: CSS selector for CAPTCHA element
            
        Returns:
            True if CAPTCHA was solved, False otherwise
        """
        try:
            # Check if CAPTCHA exists
            captcha_element = await page.query_selector(captcha_selector)
            if not captcha_element:
                return True  # No CAPTCHA found
            
            logger.warning("CAPTCHA detected - attempting to solve")
            
            # Basic CAPTCHA solving strategies
            # Note: This is a simplified implementation
            # In production, you'd use CAPTCHA solving services
            
            # Strategy 1: Wait for manual intervention (if not headless)
            if not self.config.get('headless', True):
                logger.info("Waiting for manual CAPTCHA solving...")
                await asyncio.sleep(30)  # Wait 30 seconds for manual solving
                return True
            
            # Strategy 2: Try to bypass (click checkbox for reCAPTCHA)
            checkbox_selector = '.recaptcha-checkbox-checkmark'
            checkbox = await page.query_selector(checkbox_selector)
            if checkbox:
                await checkbox.click()
                await asyncio.sleep(5)
                return True
            
            logger.error("CAPTCHA solving failed")
            return False
            
        except Exception as e:
            logger.error(f"Error solving CAPTCHA: {e}")
            return False
    
    async def adaptive_scrape(self, url: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Adaptive scraping with retry logic and strategy adjustment
        
        Args:
            url: URL to scrape
            **kwargs: Additional scraping parameters
            
        Returns:
            Scraped data or None if all attempts failed
        """
        max_retries = kwargs.get('max_retries', self.config['retry_attempts'])
        
        for attempt in range(max_retries):
            try:
                # Adjust strategy based on attempt
                if attempt > 0:
                    logger.info(f"Retry attempt {attempt + 1} for {url}")
                    
                    # Change user agent
                    if attempt == 1:
                        user_agent = self.config['user_agents'][attempt % len(self.config['user_agents'])]
                        await self.context.set_extra_http_headers({'User-Agent': user_agent})
                    
                    # Add longer delays
                    if attempt == 2:
                        kwargs['wait_time'] = kwargs.get('wait_time', 2000) * 2
                    
                    # Try different wait conditions
                    if attempt == 3:
                        kwargs['wait_for'] = 'body'
                
                result = await self.scrape_page(url, **kwargs)
                
                if result['success']:
                    return result
                
                # If failed, wait before retry
                await asyncio.sleep(self.config['retry_delay'] * (attempt + 1))
                
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {e}")
                await asyncio.sleep(self.config['retry_delay'] * (attempt + 1))
        
        logger.error(f"All scraping attempts failed for {url}")
        return None
    
    async def close(self):
        """Close browser and cleanup resources"""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            
            self.is_initialized = False
            logger.info("Playwright manager closed")
            
        except Exception as e:
            logger.error(f"Error closing Playwright manager: {e}")

# Example usage
async def example_usage():
    manager = PlaywrightManager()
    
    try:
        await manager.initialize()
        
        # Basic scraping
        result = await manager.scrape_page(
            'https://example.com',
            wait_for='h1',
            screenshot=True
        )
        
        if result['success']:
            print(f"Scraped {len(result['content'])} characters")
            print(f"Title: {result['title']}")
        
        # Adaptive scraping with retries
        result = await manager.adaptive_scrape(
            'https://example.com',
            wait_for='.content',
            max_retries=3
        )
        
    finally:
        await manager.close()

if __name__ == "__main__":
    asyncio.run(example_usage())

















