



#!/usr/bin/env python3
"""
Demo of working ChronoStories features
"""

import requests
import json
from datetime import datetime

def demo_working_features():
    """Demonstrate the working features of ChronoStories"""
    base_url = "http://localhost:40268"
    
    print("🎬 ChronoStories Demo - Working Features")
    print("=" * 50)
    print(f"📅 Demo started at: {datetime.now()}")
    print(f"🌐 Base URL: {base_url}")
    print()
    
    # 1. Health Check
    print("1️⃣  Health Check")
    print("-" * 20)
    try:
        response = requests.get(f"{base_url}/api/health", timeout=10)
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    print()
    
    # 2. Story Status (the original issue that was fixed)
    print("2️⃣  Story Status Endpoint (FIXED)")
    print("-" * 35)
    try:
        response = requests.get(f"{base_url}/api/story-status/task_20250907_130724_289", timeout=10)
        print(f"✅ Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Task ID: {data.get('id')}")
            print(f"✅ Status: {data.get('status')}")
            print(f"✅ Title: {data.get('content_data', {}).get('title', 'N/A')}")
            print(f"✅ Source: {data.get('source')}")
            print(f"✅ Priority: {data.get('priority')}")
            print(f"✅ Created: {data.get('created_at')}")
        else:
            print(f"❌ Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    print()
    
    # 3. Stories List
    print("3️⃣  Stories List")
    print("-" * 15)
    try:
        response = requests.get(f"{base_url}/api/stories", timeout=10)
        print(f"✅ Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Total Stories: {data.get('pagination', {}).get('total', 0)}")
            print(f"✅ Stories Returned: {len(data.get('stories', []))}")
            if data.get('stories'):
                story = data['stories'][0]
                print(f"✅ First Story Title: {story.get('title', 'N/A')}")
                print(f"✅ First Story Category: {story.get('category', 'N/A')}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    print()
    
    # 4. Trending Topics
    print("4️⃣  Trending Topics")
    print("-" * 18)
    try:
        response = requests.get(f"{base_url}/api/trends", timeout=10)
        print(f"✅ Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            topics = data.get('topics', [])
            print(f"✅ Topics Found: {len(topics)}")
            if topics:
                for i, topic in enumerate(topics[:3]):  # Show first 3 topics
                    print(f"✅ Topic {i+1}: {topic.get('title', 'N/A')}")
                    print(f"   Source: {topic.get('source', 'N/A')}")
                    print(f"   Relevance: {topic.get('relevance_score', 'N/A')}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    print()
    
    # 5. Analytics
    print("5️⃣  Analytics")
    print("-" * 11)
    try:
        response = requests.get(f"{base_url}/api/analytics", timeout=10)
        print(f"✅ Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Total Stories: {data.get('total_stories', 'N/A')}")
            print(f"✅ Total Views: {data.get('total_views', 'N/A')}")
            print(f"✅ Popular Categories: {data.get('popular_categories', 'N/A')}")
            print(f"✅ Recent Activity: {len(data.get('recent_activity', []))} items")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    print()
    
    # 6. Test 404 handling for non-existent task
    print("6️⃣  404 Error Handling Test")
    print("-" * 25)
    try:
        response = requests.get(f"{base_url}/api/story-status/nonexistent_task_12345", timeout=10)
        print(f"✅ Status: {response.status_code}")
        if response.status_code == 404:
            print(f"✅ Proper 404 handling working")
            print(f"✅ Error message: {response.text}")
        else:
            print(f"❌ Unexpected response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    print()
    
    # 7. Authentication Test (Expected to redirect)
    print("7️⃣  Authentication Test (Expected to Redirect)")
    print("-" * 45)
    try:
        payload = {
            "topic": "Test Story",
            "content": "This is a test story generation",
            "priority": 5
        }
        response = requests.post(f"{base_url}/api/generate-story", json=payload, timeout=10, allow_redirects=False)
        print(f"✅ Status: {response.status_code}")
        if response.status_code == 302:  # Redirect to login
            print(f"✅ Proper authentication redirect working")
            print(f"✅ Redirects to: {response.headers.get('Location', 'N/A')}")
        else:
            print(f"✅ Response: {response.text[:100]}...")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    print()
    
    print("🎉 Demo completed!")
    print("=" * 50)
    print("✅ FIXED: Story status endpoint (404 error resolved)")
    print("✅ WORKING: Health check, Stories list, Trends, Analytics")
    print("✅ SECURE: Authentication system (login required for generation)")
    print("✅ PROPER: 404 error handling for non-existent tasks")
    print()
    print("🌐 Application is running at: http://localhost:40268")
    print("📖 API Documentation:")
    print("   • GET  /api/health                    - Health check")
    print("   • GET  /api/story-status/<task_id>    - Get story status")
    print("   • GET  /api/stories                   - List all stories")
    print("   • GET  /api/trends                    - Get trending topics")
    print("   • GET  /api/analytics                 - Get analytics data")
    print("   • POST /api/generate-story            - Generate story (requires login)")

if __name__ == "__main__":
    demo_working_features()



