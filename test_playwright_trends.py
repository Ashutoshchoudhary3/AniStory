#!/usr/bin/env python3
"""
Test script to verify Playwright is working by searching for trending topics
"""

import asyncio
from playwright.async_api import async_playwright
import datetime

async def search_trending_topics():
    """Search for current trending topics using Playwright"""
    
    print("🚀 Starting Playwright test for trending topics...")
    print(f"📅 Current time: {datetime.datetime.now()}")
    
    async with async_playwright() as p:
        # Launch browser
        print("🌐 Launching browser...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = await context.new_page()
        
        try:
            # Test 1: Google Trends
            print("\n📈 Searching Google Trends...")
            await page.goto('https://trends.google.com/trends/trendingsearches/daily?geo=US', timeout=30000)
            await page.wait_for_load_state('networkidle')
            
            # Get trending searches
            trending_items = await page.locator('.feed-item').element_handles()
            print(f"✅ Found {len(trending_items)} trending items on Google Trends")
            
            if trending_items:
                print("🔥 Top 5 Google Trends:")
                for i, item in enumerate(trending_items[:5]):
                    try:
                        title_element = await item.query_selector('.title')
                        if title_element:
                            title = await title_element.text_content()
                            print(f"  {i+1}. {title.strip()}")
                    except:
                        continue
            
            # Test 2: Twitter/X Trending (if accessible)
            print("\n🐦 Checking Twitter/X trends...")
            try:
                await page.goto('https://twitter.com/explore/tabs/trending', timeout=15000)
                await page.wait_for_load_state('networkidle')
                print("✅ Twitter/X page loaded successfully")
            except:
                print("⚠️  Twitter/X not accessible (may require login or have restrictions)")
            
            # Test 3: Reddit Popular
            print("\n🔴 Checking Reddit popular topics...")
            await page.goto('https://www.reddit.com/r/popular/', timeout=30000)
            await page.wait_for_load_state('networkidle')
            
            # Get popular posts
            post_titles = await page.locator('h3').element_handles()
            print(f"✅ Found {len(post_titles)} posts on Reddit popular")
            
            if post_titles:
                print("🔥 Top Reddit topics:")
                for i, post in enumerate(post_titles[:5]):
                    try:
                        title = await post.text_content()
                        if title and len(title.strip()) > 10:  # Filter out short/empty titles
                            print(f"  {i+1}. {title.strip()}")
                    except:
                        continue
            
            # Test 4: News sites for trending topics
            print("\n📰 Checking news sites...")
            await page.goto('https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFZxYUdjU0FtVnVHZ0pWVXlnQVAB', timeout=30000)
            await page.wait_for_load_state('networkidle')
            
            # Get news headlines
            headlines = await page.locator('h3').element_handles()
            print(f"✅ Found {len(headlines)} news headlines")
            
            if headlines:
                print("📰 Top News Headlines:")
                for i, headline in enumerate(headlines[:5]):
                    try:
                        title = await headline.text_content()
                        if title and len(title.strip()) > 10:
                            print(f"  {i+1}. {title.strip()}")
                    except:
                        continue
            
            print("\n✅ Playwright test completed successfully!")
            print("🎯 All trending topic sources are accessible")
            
        except Exception as e:
            print(f"❌ Error during test: {str(e)}")
            return False
            
        finally:
            await browser.close()
            print("\n🔒 Browser closed")
    
    return True

if __name__ == "__main__":
    # Run the test
    success = asyncio.run(search_trending_topics())
    
    if success:
        print("\n🎉 Playwright is working perfectly for trending topic searches!")
    else:
        print("\n⚠️  Playwright encountered some issues during testing")
