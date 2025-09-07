




















import google.generativeai as genai
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from config import Config

logger = logging.getLogger(__name__)

@dataclass
class StoryContent:
    """Structured story content"""
    title: str
    content: str
    summary: str
    headline: str
    subheadline: str
    captions: List[str]
    hashtags: List[str]
    call_to_action: str
    story_structure: Dict[str, Any]
    visual_descriptions: List[str]
    emotional_journey: List[str]
    target_audience: str
    reading_time: int
    complexity_level: str

class StoryGenerator:
    """
    Advanced story generator that creates engaging, anime-style web stories
    from news content and trending topics
    """
    
    def __init__(self):
        self.model = None
        self.is_initialized = False
        
        # Story generation configuration
        self.config = {
            'default_story_type': 'informative',
            'available_story_types': [
                'breaking_news',
                'in_depth_analysis',
                'trending_topic',
                'human_interest',
                'explainer',
                'visual_story',
                'emotional_journey',
                'character_focused',
                'timeline',
                'comparison'
            ],
            'target_audiences': ['general', 'young_adults', 'professionals', 'global', 'regional'],
            'complexity_levels': ['simple', 'moderate', 'complex'],
            'story_structures': {
                'breaking_news': ['hook', 'key_facts', 'impact', 'what_next'],
                'in_depth_analysis': ['context', 'problem', 'analysis', 'implications', 'conclusion'],
                'trending_topic': ['trend_intro', 'why_it_matters', 'different_perspectives', 'future_outlook'],
                'human_interest': ['personal_story', 'broader_context', 'emotional_impact', 'takeaway'],
                'explainer': ['question', 'simple_explanation', 'examples', 'key_takeaways'],
                'visual_story': ['visual_hook', 'scene_setting', 'character_introduction', 'story_progression'],
                'emotional_journey': ['emotional_setup', 'conflict_challenge', 'resolution_growth', 'emotional_payoff'],
                'character_focused': ['character_intro', 'challenge_faced', 'journey_taken', 'outcome_achieved'],
                'timeline': ['starting_point', 'key_events', 'turning_points', 'current_status'],
                'comparison': ['subject_a', 'subject_b', 'similarities', 'differences', 'conclusion']
            },
            'default_reading_time': 60,  # seconds
            'min_content_length': 100,
            'max_content_length': 2000,
            'caption_length_range': [20, 100],
            'hashtag_count_range': [3, 8],
            'emotional_arc_stages': ['setup', 'tension', 'climax', 'resolution']
        }
        
        # Anime storytelling elements
        self.anime_storytelling_elements = {
            'emotional_beats': ['hopeful beginning', 'rising tension', 'emotional climax', 'satisfying resolution'],
            'visual_storytelling': ['expressive character moments', 'dramatic scene transitions', 'symbolic imagery', 'atmospheric backgrounds'],
            'narrative_techniques': ['show_dont_tell', 'emotional_foreshadowing', 'character_driven_narrative', 'visual_metaphors'],
            'audience_engagement': ['relatable_characters', 'universal_themes', 'emotional_authenticity', 'visual_surprise']
        }
    
    async def initialize(self):
        """Initialize the story generator with Gemini API"""
        try:
            genai.configure(api_key=Config.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
            self.is_initialized = True
            logger.info("Story generator initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize story generator: {e}")
            raise
    
    async def generate_story(self, content: Dict, story_type: str = None, narrative_angle: str = None, target_audience: str = None) -> Dict:
        """
        Generate a complete story from content data
        
        Args:
            content: Content data with analysis
            story_type: Type of story to generate
            narrative_angle: Specific narrative angle to take
            target_audience: Target audience for the story
            
        Returns:
            Generated story content
        """
        if not self.is_initialized:
            await self.initialize()
        
        try:
            story_type = story_type or self.config['default_story_type']
            target_audience = target_audience or 'general'
            
            # Extract content data
            original_data = content.get('data', {})
            analysis = content.get('analysis', {})
            
            # Generate story structure
            story_structure = await self._generate_story_structure(
                content, story_type, narrative_angle, target_audience
            )
            
            # Generate story content
            story_content = await self._generate_story_content(
                story_structure, content, story_type, target_audience
            )
            
            # Generate visual descriptions
            visual_descriptions = await self._generate_visual_descriptions(
                story_content, story_type, target_audience
            )
            
            # Generate captions and hashtags
            captions = await self._generate_captions(story_content, target_audience)
            hashtags = await self._generate_hashtags(story_content, analysis)
            
            # Calculate reading time
            reading_time = self._calculate_reading_time(story_content['content'])
            
            # Create final story content
            final_story = StoryContent(
                title=story_content['title'],
                content=story_content['content'],
                summary=story_content['summary'],
                headline=story_content['headline'],
                subheadline=story_content['subheadline'],
                captions=captions,
                hashtags=hashtags,
                call_to_action=story_content['call_to_action'],
                story_structure=story_structure,
                visual_descriptions=visual_descriptions,
                emotional_journey=story_content['emotional_journey'],
                target_audience=target_audience,
                reading_time=reading_time,
                complexity_level=story_content['complexity_level']
            )
            
            logger.info(f"Generated story: {final_story.title} (Type: {story_type}, Audience: {target_audience})")
            
            # Convert to dict for return
            return {
                'title': final_story.title,
                'content': final_story.content,
                'summary': final_story.summary,
                'headline': final_story.headline,
                'subheadline': final_story.subheadline,
                'captions': final_story.captions,
                'hashtags': final_story.hashtags,
                'call_to_action': final_story.call_to_action,
                'story_structure': final_story.story_structure,
                'visual_descriptions': final_story.visual_descriptions,
                'emotional_journey': final_story.emotional_journey,
                'target_audience': final_story.target_audience,
                'reading_time': final_story.reading_time,
                'complexity_level': final_story.complexity_level
            }
            
        except Exception as e:
            logger.error(f"Error generating story: {e}")
            return self._create_fallback_story(content, story_type, target_audience)
    
    async def _generate_story_structure(self, content: Dict, story_type: str, narrative_angle: str, target_audience: str) -> Dict:
        """Generate story structure based on content and parameters"""
        
        # Get base structure for story type
        base_structure = self.config['story_structures'].get(story_type, self.config['story_structures']['in_depth_analysis'])
        
        # Create detailed structure prompt
        prompt = f"""
        Create a detailed story structure for this content:
        
        Content Type: {content.get('type', 'unknown')}
        Story Type: {story_type}
        Narrative Angle: {narrative_angle or 'default'}
        Target Audience: {target_audience}
        
        Original Content:
        {json.dumps(content.get('data', {}), indent=2)}
        
        Analysis:
        {json.dumps(content.get('analysis', {}), indent=2)}
        
        Base Structure: {base_structure}
        
        Return JSON with:
        {{
            "story_structure": {{
                "sections": [
                    {{
                        "name": "section_name",
                        "purpose": "what this section accomplishes",
                        "content_focus": "what content to include",
                        "emotional_goal": "emotional response to evoke",
                        "visual_elements": ["visual elements to include"],
                        "length_estimate": "estimated length in words"
                    }}
                ]
            }},
            "narrative_arc": {{
                "setup": "how to establish the story",
                "development": "how to develop the narrative",
                "climax": "the key moment or revelation",
                "resolution": "how to conclude the story"
            }},
            "audience_considerations": {{
                "tone": "appropriate tone for audience",
                "language_level": "complexity level",
                "cultural_sensitivity": "cultural considerations",
                "engagement_hooks": ["ways to keep audience engaged"]
            }},
            "anime_storytelling_elements": {{
                "emotional_beats": ["specific emotional moments"],
                "visual_storytelling": ["visual narrative techniques"],
                "character_focus": "how to humanize the story",
                "dramatic_moments": ["key dramatic moments"]
            }}
        }}
        
        Make it engaging and suitable for anime-style visual storytelling.
        """
        
        try:
            response = await self.model.generate_content(prompt)
            structure_data = self._extract_json_from_response(response.text)
            
            return structure_data
            
        except Exception as e:
            logger.error(f"Error generating story structure: {e}")
            return self._create_fallback_structure(story_type, base_structure)
    
    async def _generate_story_content(self, story_structure: Dict, content: Dict, story_type: str, target_audience: str) -> Dict:
        """Generate actual story content based on structure"""
        
        original_data = content.get('data', {})
        analysis = content.get('analysis', {})
        
        prompt = f"""
        Generate engaging story content for this structure:
        
        Story Structure:
        {json.dumps(story_structure, indent=2)}
        
        Original Content:
        {json.dumps(original_data, indent=2)}
        
        Analysis:
        {json.dumps(analysis, indent=2)}
        
        Story Type: {story_type}
        Target Audience: {target_audience}
        
        Create content that:
        1. Tells a compelling story
        2. Is suitable for anime-style visual presentation
        3. Engages the target audience
        4. Follows the provided structure
        5. Includes emotional journey elements
        
        Return JSON with:
        {{
            "title": "engaging story title",
            "headline": "attention-grabbing headline",
            "subheadline": "supporting subheadline",
            "content": "full story content",
            "summary": "brief summary",
            "emotional_journey": ["emotional stages"],
            "call_to_action": "what readers should do next",
            "complexity_level": "simple, moderate, or complex",
            "key_visual_moments": ["moments that should be illustrated"],
            "character_elements": ["human elements to include"],
            "narrative_voice": "first_person, second_person, or third_person"
        }}
        
        Make it engaging, informative, and perfect for visual storytelling.
        """
        
        try:
            response = await self.model.generate_content(prompt)
            content_data = self._extract_json_from_response(response.text)
            
            return content_data
            
        except Exception as e:
            logger.error(f"Error generating story content: {e}")
            return self._create_fallback_content(content, story_type, target_audience)
    
    async def _generate_visual_descriptions(self, story_content: Dict, story_type: str, target_audience: str) -> List[str]:
        """Generate visual descriptions for story images"""
        
        prompt = f"""
        Create visual descriptions for images to accompany this story:
        
        Story Title: {story_content.get('title', '')}
        Story Content: {story_content.get('content', '')[:500]}
        Story Type: {story_type}
        Target Audience: {target_audience}
        
        Key Visual Moments: {story_content.get('key_visual_moments', [])}
        
        Create descriptions for 3 images:
        1. Hero image (main story image)
        2. Supporting image 1
        3. Supporting image 2
        
        Each description should:
        - Be suitable for anime-style illustration
        - Capture key story moments
        - Be visually engaging
        - Work well in web story format
        
        Return JSON with:
        {{
            "visual_descriptions": [
                "detailed description of hero image",
                "detailed description of supporting image 1",
                "detailed description of supporting image 2"
            ],
            "visual_consistency_notes": "notes on maintaining visual consistency",
            "style_elements": ["specific style elements to include"],
            "color_suggestions": ["color palette suggestions"]
        }}
        """
        
        try:
            response = await self.model.generate_content(prompt)
            visual_data = self._extract_json_from_response(response.text)
            
            return visual_data.get('visual_descriptions', [])
            
        except Exception as e:
            logger.error(f"Error generating visual descriptions: {e}")
            return self._create_fallback_visual_descriptions(story_content)
    
    async def _generate_captions(self, story_content: Dict, target_audience: str) -> List[str]:
        """Generate captions for story images"""
        
        content = story_content.get('content', '')
        title = story_content.get('title', '')
        
        prompt = f"""
        Create engaging captions for story images:
        
        Story Title: {title}
        Story Content: {content[:300]}
        Target Audience: {target_audience}
        
        Create 3 captions:
        1. For hero image
        2. For supporting image 1  
        3. For supporting image 2
        
        Each caption should:
        - Be concise (20-100 characters)
        - Be engaging and attention-grabbing
        - Work well with anime-style images
        - Encourage continued reading
        
        Return JSON with:
        {{
            "captions": [
                "caption for hero image",
                "caption for supporting image 1",
                "caption for supporting image 2"
            ],
            "caption_style": "description of caption style used"
        }}
        """
        
        try:
            response = await self.model.generate_content(prompt)
            caption_data = self._extract_json_from_response(response.text)
            
            return caption_data.get('captions', [])
            
        except Exception as e:
            logger.error(f"Error generating captions: {e}")
            return self._create_fallback_captions(story_content)
    
    async def _generate_hashtags(self, story_content: Dict, analysis: Dict) -> List[str]:
        """Generate relevant hashtags for the story"""
        
        title = story_content.get('title', '')
        content = story_content.get('content', '')
        category = analysis.get('category', 'general')
        key_topics = analysis.get('key_topics', [])
        
        prompt = f"""
        Generate relevant hashtags for this story:
        
        Title: {title}
        Category: {category}
        Key Topics: {key_topics}
        Content Summary: {content[:200]}
        
        Create 3-8 hashtags that:
        1. Are relevant to the story content
        2. Could help with discoverability
        3. Include trending keywords when appropriate
        4. Work well for anime-style content
        
        Return JSON with:
        {{
            "hashtags": ["#hashtag1", "#hashtag2", "#hashtag3"],
            "hashtag_strategy": "explanation of hashtag choices"
        }}
        """
        
        try:
            response = await self.model.generate_content(prompt)
            hashtag_data = self._extract_json_from_response(response.text)
            
            return hashtag_data.get('hashtags', [])
            
        except Exception as e:
            logger.error(f"Error generating hashtags: {e}")
            return self._create_fallback_hashtags(analysis)
    
    def _calculate_reading_time(self, content: str) -> int:
        """Calculate estimated reading time in seconds"""
        words = content.split()
        word_count = len(words)
        
        # Average reading speed: 200-250 words per minute
        # For web stories, we want faster reading: 300 words per minute
        words_per_minute = 300
        reading_time_minutes = word_count / words_per_minute
        
        # Convert to seconds and add buffer for visual elements
        reading_time_seconds = int(reading_time_minutes * 60 * 1.2)  # 20% buffer for visuals
        
        # Ensure minimum reading time for engagement
        return max(reading_time_seconds, 30)  # Minimum 30 seconds
    
    def _create_fallback_structure(self, story_type: str, base_structure: List[str]) -> Dict:
        """Create fallback story structure"""
        return {
            'story_structure': {
                'sections': [{'name': section, 'purpose': 'basic information', 'content_focus': 'general content'} 
                           for section in base_structure]
            },
            'narrative_arc': {
                'setup': 'introduce the topic',
                'development': 'provide details',
                'climax': 'highlight key point',
                'resolution': 'conclude the story'
            },
            'audience_considerations': {
                'tone': 'informative',
                'language_level': 'moderate',
                'engagement_hooks': ['interesting facts', 'visual elements']
            },
            'anime_storytelling_elements': {
                'emotional_beats': ['curiosity', 'understanding', 'interest'],
                'visual_storytelling': ['clear imagery', 'engaging scenes']
            }
        }
    
    def _create_fallback_content(self, content: Dict, story_type: str, target_audience: str) -> Dict:
        """Create fallback story content"""
        original_data = content.get('data', {})
        title = original_data.get('title', 'Interesting Story')
        
        return {
            'title': title,
            'headline': title,
            'subheadline': 'An engaging story about current events',
            'content': f"This is a story about {title}. It covers important aspects of the topic and provides valuable insights for readers interested in this subject.",
            'summary': f"A brief overview of {title}",
            'emotional_journey': ['interest', 'understanding', 'appreciation'],
            'call_to_action': 'Learn more about this topic',
            'complexity_level': 'moderate',
            'key_visual_moments': ['main subject', 'supporting elements'],
            'character_elements': ['relatable perspective'],
            'narrative_voice': 'third_person'
        }
    
    def _create_fallback_visual_descriptions(self, story_content: Dict) -> List[str]:
        """Create fallback visual descriptions"""
        title = story_content.get('title', 'Story')
        return [
            f"Illustration of {title} with anime style, featuring key elements of the story",
            f"Supporting image showing context for {title}, anime style",
            f"Additional visual element related to {title}, maintaining anime aesthetic"
        ]
    
    def _create_fallback_captions(self, story_content: Dict) -> List[str]:
        """Create fallback captions"""
        title = story_content.get('title', 'Story')
        return [
            f"Discover {title}",
            f"Learn more about this topic",
            f"The story continues"
        ]
    
    def _create_fallback_hashtags(self, analysis: Dict) -> List[str]:
        """Create fallback hashtags"""
        category = analysis.get('category', 'news')
        return [f"#{category}", "#news", "#story", "#anime"]
    
    def _create_fallback_story(self, content: Dict, story_type: str, target_audience: str) -> Dict:
        """Create complete fallback story"""
        original_data = content.get('data', {})
        title = original_data.get('title', 'Interesting Story')
        
        return {
            'title': title,
            'content': f"This is a story about {title}. It covers important aspects of the topic.",
            'summary': f"A brief overview of {title}",
            'headline': title,
            'subheadline': 'An engaging story',
            'captions': [f"About {title}", "Learn more", "Continue reading"],
            'hashtags': ["#news", "#story"],
            'call_to_action': 'Learn more about this topic',
            'story_structure': {'type': 'basic'},
            'visual_descriptions': [f"Illustration of {title}"],
            'emotional_journey': ['interest'],
            'target_audience': target_audience,
            'reading_time': 60,
            'complexity_level': 'moderate'
        }
    
    def _extract_json_from_response(self, response_text: str) -> Dict:
        """Extract JSON from AI response"""
        try:
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return json.loads(response_text)
        except Exception as e:
            logger.error(f"Error extracting JSON from response: {e}")
            return {}

# Example usage
async def example_usage():
    generator = StoryGenerator()
    
    try:
        await generator.initialize()
        
        # Example content
        content_data = {
            'type': 'news',
            'data': {
                'title': 'Revolutionary AI Breakthrough in Medical Diagnosis',
                'description': 'Scientists develop new AI system that can diagnose rare diseases with 99% accuracy',
                'content': 'In a groundbreaking development, researchers at Stanford University have created an artificial intelligence system capable of diagnosing rare medical conditions with unprecedented accuracy.',
                'publishedAt': '2024-01-15T10:00:00Z'
            },
            'analysis': {
                'category': 'technology',
                'quality_score': 0.9,
                'sentiment': 'positive',
                'key_topics': ['AI', 'medical diagnosis', 'healthcare', 'Stanford University'],
                'engagement_potential': 0.8,
                'target_audience': 'general'
            }
        }
        
        # Generate story
        story = await generator.generate_story(
            content=content_data,
            story_type='in_depth_analysis',
            narrative_angle='human_impact',
            target_audience='general'
        )
        
        print(f"Generated Story:")
        print(f"Title: {story['title']}")
        print(f"Headline: {story['headline']}")
        print(f"Reading Time: {story['reading_time']} seconds")
        print(f"Complexity: {story['complexity_level']}")
        print(f"Target Audience: {story['target_audience']}")
        print(f"Content Preview: {story['content'][:100]}...")
        print(f"Captions: {story['captions']}")
        print(f"Hashtags: {story['hashtags']}")
        print(f"Visual Descriptions: {len(story['visual_descriptions'])} descriptions")
        
    except Exception as e:
        print(f"Error in example usage: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())




















