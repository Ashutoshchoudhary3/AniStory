#!/usr/bin/env python3
"""
Script to add sample data to the ChronoStories database
"""

from app import create_app, db
from app.models import Story, Trend, Analytics, User
from datetime import datetime, timedelta
import random

def add_sample_data():
    app = create_app()
    with app.app_context():
        # Clear existing data
        print("Clearing existing data...")
        Story.query.delete()
        Trend.query.delete()
        Analytics.query.delete()
        db.session.commit()
        
        # Sample story data
        sample_stories = [
            {
                "title": "Revolutionary AI Breakthrough Transforms Healthcare",
                "summary": "Scientists develop new AI system capable of diagnosing rare diseases with 99% accuracy, potentially saving millions of lives worldwide.",
                "content": "In a groundbreaking development, researchers at leading universities have collaborated to create an artificial intelligence system that can identify rare medical conditions with unprecedented accuracy. The system, trained on millions of medical records and imaging data, promises to revolutionize how doctors approach diagnosis and treatment planning.",
                "category": "technology",
                "image_url": "https://images.unsplash.com/photo-1579546929518-9e396f3cc809?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80",
                "source_url": "https://example.com/ai-healthcare",
                "ai_prompt": "Futuristic AI healthcare system, anime style, glowing medical interface, doctor and AI working together"
            },
            {
                "title": "Climate Summit Reaches Historic Agreement",
                "summary": "World leaders unite on ambitious climate action plan targeting net-zero emissions by 2040.",
                "content": "Representatives from 195 countries have signed a historic climate agreement that sets the most ambitious carbon reduction targets to date. The comprehensive plan includes massive investments in renewable energy, reforestation projects, and innovative carbon capture technologies.",
                "category": "environment",
                "image_url": "https://images.unsplash.com/photo-1569163139394-de4798aa4e9a?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80",
                "source_url": "https://example.com/climate-summit",
                "ai_prompt": "Beautiful green earth with renewable energy, anime style, solar panels and wind turbines, hopeful atmosphere"
            },
            {
                "title": "Space Tourism Takes Flight",
                "summary": "Commercial space flights become accessible to general public with new affordable pricing models.",
                "content": "The space tourism industry has reached a new milestone as several companies announce significantly reduced prices for suborbital flights. With tickets now starting at $50,000, space travel is becoming accessible to a broader segment of the population.",
                "category": "science",
                "image_url": "https://images.unsplash.com/photo-1446776653964-20c1d3a81b06?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80",
                "source_url": "https://example.com/space-tourism",
                "ai_prompt": "Anime style spaceship in space, tourists looking at earth, wonder and excitement"
            },
            {
                "title": "Quantum Computing Solves Complex Protein Folding",
                "summary": "Quantum computers successfully model protein folding patterns, opening new doors for drug discovery.",
                "content": "Researchers have successfully used quantum computers to predict protein folding patterns that were previously impossible to calculate. This breakthrough could accelerate the development of treatments for Alzheimer's, cancer, and other diseases.",
                "category": "science",
                "image_url": "https://images.unsplash.com/photo-1518152006812-edab29b069ac?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80",
                "ai_prompt": "Quantum computer with glowing protein structures, anime style, scientific breakthrough"
            },
            {
                "title": "Renewable Energy Breakthrough: Solar Paint",
                "summary": "New solar paint technology can convert any surface into a solar panel, revolutionizing clean energy.",
                "content": "Scientists have developed an innovative paint that can harvest solar energy from any surface it's applied to. This breakthrough technology could transform buildings, vehicles, and even clothing into energy-generating surfaces.",
                "category": "technology",
                "image_url": "https://images.unsplash.com/photo-1509391366360-2e959784a276?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80",
                "source_url": "https://example.com/solar-paint",
                "ai_prompt": "Building covered in glowing solar paint, anime style, clean energy concept"
            },
            {
                "title": "Ocean Cleanup Project Achieves Major Milestone",
                "summary": "Advanced ocean cleanup system removes 100,000 tons of plastic from Pacific Ocean.",
                "content": "The Ocean Cleanup Project has successfully removed over 100,000 tons of plastic waste from the Great Pacific Garbage Patch. The innovative system uses autonomous vessels and advanced filtering technology to collect and process ocean plastic.",
                "category": "environment",
                "image_url": "https://images.unsplash.com/photo-1559827260-dc66d52bef19?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80",
                "source_url": "https://example.com/ocean-cleanup",
                "ai_prompt": "Clean ocean with marine life, anime style, environmental success story"
            }
        ]
        
        # Add stories with different dates
        print("Adding sample stories...")
        for i, story_data in enumerate(sample_stories):
            story = Story(
                title=story_data["title"],
                summary=story_data["summary"],
                content=story_data["content"],
                category=story_data["category"],
                image_url=story_data.get("image_url", ""),
                source_url=story_data.get("source_url", ""),
                ai_prompt=story_data.get("ai_prompt", ""),
                views=random.randint(100, 5000),
                likes=random.randint(10, 500),
                shares=random.randint(5, 200),
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                updated_at=datetime.utcnow() - timedelta(days=random.randint(0, 29))
            )
            db.session.add(story)
        
        # Sample trending topics
        trending_topics = [
            {"topic": "Artificial Intelligence", "source": "google_trends", "trend_score": 95.5, "volume": 125000},
            {"topic": "Climate Change", "source": "twitter", "trend_score": 88.2, "volume": 98000},
            {"topic": "Space Exploration", "source": "reddit", "trend_score": 76.8, "volume": 67000},
            {"topic": "Quantum Computing", "source": "google_trends", "trend_score": 72.1, "volume": 45000},
            {"topic": "Renewable Energy", "source": "twitter", "trend_score": 69.4, "volume": 52000},
            {"topic": "Ocean Conservation", "source": "reddit", "trend_score": 65.7, "volume": 38000}
        ]
        
        print("Adding trending topics...")
        for topic_data in trending_topics:
            trend = Trend(
                topic=topic_data["topic"],
                source=topic_data["source"],
                trend_score=topic_data["trend_score"],
                volume=topic_data["volume"],
                created_at=datetime.utcnow() - timedelta(hours=random.randint(1, 24))
            )
            db.session.add(trend)
        
        # Sample analytics data
        print("Adding analytics data...")
        for i in range(30):  # Last 30 days
            analytics = Analytics(
                metric_type="story_views",
                metric_value=random.randint(50, 200),
                timestamp=datetime.utcnow() - timedelta(days=i)
            )
            db.session.add(analytics)
            
            analytics2 = Analytics(
                metric_type="user_sessions",
                metric_value=random.randint(20, 100),
                timestamp=datetime.utcnow() - timedelta(days=i)
            )
            db.session.add(analytics2)
        
        # Commit all changes
        print("Committing changes...")
        db.session.commit()
        
        # Print summary
        story_count = Story.query.count()
        trend_count = Trend.query.count()
        analytics_count = Analytics.query.count()
        
        print(f"\nSample data added successfully!")
        print(f"Stories: {story_count}")
        print(f"Trending topics: {trend_count}")
        print(f"Analytics records: {analytics_count}")
        
        # Show first few stories
        print("\nFirst 3 stories:")
        for story in Story.query.limit(3).all():
            print(f"- {story.title[:60]}... (Views: {story.views})")
            
    except Exception as e:
        print(f"Error adding sample data: {e}")
        db.session.rollback()
        raise

if __name__ == "__main__":
    add_sample_data()

