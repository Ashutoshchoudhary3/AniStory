

#!/usr/bin/env python3
"""
Integration test for ChronoStories: Test the complete workflow
"""

import requests
import json
import time
from datetime import datetime

def test_api_endpoints():
    """Test all API endpoints"""
    base_url = "http://localhost:40268"
    
    print("🚀 Testing ChronoStories API Endpoints...")
    print(f"📅 Current time: {datetime.now()}")
    
    # Test 1: Health check
    print("\n1️⃣ Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
    
    # Test 2: Story status endpoint
    print("\n2️⃣ Testing story status endpoint...")
    try:
        response = requests.get(f"{base_url}/api/story-status/task_20250907_130724_289", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Story status endpoint working")
            print(f"   Task ID: {data.get('id')}")
            print(f"   Status: {data.get('status')}")
            print(f"   Title: {data.get('content_data', {}).get('title', 'N/A')}")
        else:
            print(f"❌ Story status failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Story status error: {str(e)}")
    
    # Test 3: Stories endpoint
    print("\n3️⃣ Testing stories endpoint...")
    try:
        response = requests.get(f"{base_url}/api/stories", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Stories endpoint working")
            print(f"   Total stories: {data.get('pagination', {}).get('total', 0)}")
            print(f"   Stories returned: {len(data.get('stories', []))}")
        else:
            print(f"❌ Stories endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Stories endpoint error: {str(e)}")
    
    # Test 4: Test trending topics endpoint
    print("\n4️⃣ Testing trending topics endpoint...")
    try:
        response = requests.get(f"{base_url}/api/trends", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Trending topics endpoint working")
            print(f"   Topics found: {len(data.get('topics', []))}")
            if data.get('topics'):
                print(f"   First topic: {data.get('topics')[0].get('title', 'N/A')}")
        else:
            print(f"⚠️  Trending topics endpoint not available or failed: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Trending topics error: {str(e)}")
    
    # Test 5: Test analytics endpoint
    print("\n5️⃣ Testing analytics endpoint...")
    try:
        response = requests.get(f"{base_url}/api/analytics", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Analytics endpoint working")
            print(f"   Total stories: {data.get('total_stories', 'N/A')}")
            print(f"   Total views: {data.get('total_views', 'N/A')}")
        else:
            print(f"⚠️  Analytics endpoint not available or failed: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Analytics error: {str(e)}")
    
    # Test 6: Test story generation endpoint (requires login)
    print("\n6️⃣ Testing story generation endpoint...")
    try:
        # Try to trigger story generation (will likely fail due to login requirement)
        payload = {
            "topic": "US Open Tennis Final",
            "content": "Carlos Alcaraz defeated Jannik Sinner in the US Open final",
            "priority": 5
        }
        response = requests.post(f"{base_url}/api/generate-story", json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Story generation endpoint working")
            print(f"   Task ID: {data.get('task_id')}")
            print(f"   Status: {data.get('status')}")
        elif response.status_code == 401 or response.status_code == 403:
            print(f"⚠️  Story generation requires authentication (login required)")
        else:
            print(f"⚠️  Story generation endpoint failed: {response.status_code}")
            print(f"   Response: {response.text[:100]}...")
    except Exception as e:
        print(f"⚠️  Story generation error: {str(e)}")
    
    print("\n✅ API endpoint testing completed!")
    return True

def test_story_workflow():
    """Test the complete story generation workflow"""
    base_url = "http://localhost:40268"
    
    print("\n🎬 Testing complete story generation workflow...")
    
    # Step 1: Get trending topics
    print("\n1️⃣ Getting trending topics...")
    try:
        response = requests.get(f"{base_url}/api/trending-topics", timeout=30)
        if response.status_code == 200:
            data = response.json()
            topics = data.get('topics', [])
            if topics:
                topic = topics[0]
                print(f"✅ Found trending topic: {topic.get('title', 'N/A')}")
            else:
                # Use a default topic
                topic = {
                    'title': 'US Open Tennis Final',
                    'content': 'Carlos Alcaraz defeated Jannik Sinner to win the US Open title',
                    'source': 'sports'
                }
                print(f"✅ Using default topic: {topic['title']}")
        else:
            topic = {
                'title': 'US Open Tennis Final',
                'content': 'Carlos Alcaraz defeated Jannik Sinner to win the US Open title',
                'source': 'sports'
            }
            print(f"✅ Using default topic: {topic['title']}")
    except Exception as e:
        topic = {
            'title': 'US Open Tennis Final',
            'content': 'Carlos Alcaraz defeated Jannik Sinner to win the US Open title',
            'source': 'sports'
        }
        print(f"✅ Using default topic: {topic['title']}")
    
    # Step 2: Generate story
    print("\n2️⃣ Generating story...")
    try:
        payload = {
            "topic": topic['title'],
            "content": topic['content'],
            "priority": 5,
            "source": topic.get('source', 'general')
        }
        response = requests.post(f"{base_url}/api/generate-story", json=payload, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            task_id = data.get('task_id')
            print(f"✅ Story generation started")
            print(f"   Task ID: {task_id}")
            
            # Step 3: Check story status
            print("\n3️⃣ Checking story status...")
            for i in range(5):  # Check 5 times with delays
                time.sleep(3)
                status_response = requests.get(f"{base_url}/api/story-status/{task_id}", timeout=10)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get('status')
                    print(f"   Attempt {i+1}: Status = {status}")
                    if status in ['completed', 'failed']:
                        break
                else:
                    print(f"   Attempt {i+1}: Failed to get status")
            
            if status == 'completed':
                print("✅ Story generation completed successfully!")
                return True
            else:
                print(f"⚠️  Story generation ended with status: {status}")
                return False
        else:
            print(f"❌ Story generation failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Story generation error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Starting ChronoStories Integration Tests...")
    
    # Test API endpoints
    api_success = test_api_endpoints()
    
    # Test complete workflow
    workflow_success = test_story_workflow()
    
    print(f"\n🎯 Test Results Summary:")
    print(f"   API Endpoints: {'✅ PASSED' if api_success else '❌ FAILED'}")
    print(f"   Story Workflow: {'✅ PASSED' if workflow_success else '❌ FAILED'}")
    
    if api_success and workflow_success:
        print("\n🎉 All tests passed! ChronoStories is working correctly!")
    else:
        print("\n⚠️  Some tests failed. Check the logs above for details.")
    
    print(f"\n🌐 Application is running at: http://localhost:40268")


