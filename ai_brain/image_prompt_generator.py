



















import google.generativeai as genai
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from config import Config

logger = logging.getLogger(__name__)

@dataclass
class ImagePrompt:
    """Structured image prompt with metadata"""
    prompt: str
    style: str
    aspect_ratio: str
    quality: str
    mood: str
    color_palette: List[str]
    composition_notes: str
    technical_requirements: Dict[str, Any]
    target_emotion: str
    cultural_context: str
    narrative_purpose: str

class ImagePromptGenerator:
    """
    Advanced image prompt generator for creating anime-style visuals
    that perfectly complement news stories and trending topics
    """
    
    def __init__(self):
        self.model = None
        self.is_initialized = False
        
        # Image generation configuration
        self.config = {
            'default_style': 'anime forge style',
            'available_styles': [
                'anime forge style',
                'digital art',
                'illustration',
                'manga style',
                'anime style',
                'concept art',
                'storybook illustration',
                'cinematic anime',
                'modern anime',
                'classic anime'
            ],
            'aspect_ratios': ['16:9', '9:16', '1:1', '4:3', '3:4'],
            'quality_levels': ['high', 'medium', 'low'],
            'moods': ['dramatic', 'hopeful', 'serious', 'lighthearted', 'mysterious', 'action-packed', 'emotional', 'inspiring'],
            'color_palettes': {
                'technology': ['blue', 'silver', 'white', 'neon'],
                'business': ['blue', 'gray', 'gold', 'white'],
                'politics': ['red', 'blue', 'white', 'gold'],
                'sports': ['bright colors', 'team colors', 'dynamic'],
                'entertainment': ['vibrant', 'colorful', 'eye-catching'],
                'science': ['blue', 'green', 'purple', 'white'],
                'world': ['earth tones', 'cultural colors', 'diverse'],
                'health': ['green', 'blue', 'white', 'clean'],
                'environment': ['green', 'blue', 'brown', 'natural']
            },
            'default_aspect_ratio': '16:9',
            'default_quality': 'high',
            'max_prompt_length': 1000,
            'min_prompt_length': 50
        }
        
        # Anime-specific style elements
        self.anime_style_elements = {
            'character_features': ['large expressive eyes', 'detailed hair', 'dynamic poses', 'emotional expressions'],
            'background_elements': ['detailed backgrounds', 'atmospheric lighting', 'environmental storytelling'],
            'artistic_techniques': ['cell shading', 'soft gradients', 'highlight effects', 'motion lines'],
            'emotional_styling': ['sparkling eyes', 'dramatic lighting', 'symbolic imagery', 'expressive gestures']
        }
    
    async def initialize(self):
        """Initialize the image prompt generator with Gemini API"""
        try:
            genai.configure(api_key=Config.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
            self.is_initialized = True
            logger.info("Image prompt generator initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize image prompt generator: {e}")
            raise
    
    async def generate_prompts(self, story_data: Dict, style: str = None, num_images: int = 3) -> List[ImagePrompt]:
        """
        Generate image prompts for a story
        
        Args:
            story_data: Story data including title, content, analysis
            style: Image style to use
            num_images: Number of image prompts to generate
            
        Returns:
            List of image prompts
        """
        if not self.is_initialized:
            await self.initialize()
        
        try:
            style = style or self.config['default_style']
            
            # Generate different types of prompts for the story
            prompts = []
            
            # Main story image (hero image)
            hero_prompt = await self._generate_hero_prompt(story_data, style)
            prompts.append(hero_prompt)
            
            # Supporting images
            for i in range(1, num_images):
                supporting_prompt = await self._generate_supporting_prompt(story_data, style, i)
                prompts.append(supporting_prompt)
            
            logger.info(f"Generated {len(prompts)} image prompts for story: {story_data.get('title', 'Unknown')}")
            return prompts
            
        except Exception as e:
            logger.error(f"Error generating image prompts: {e}")
            return [self._create_fallback_prompt(story_data, style)]
    
    async def _generate_hero_prompt(self, story_data: Dict, style: str) -> ImagePrompt:
        """Generate the main hero image prompt"""
        
        # Extract story elements
        title = story_data.get('title', '')
        content = story_data.get('content', '')
        category = story_data.get('category', 'general')
        analysis = story_data.get('analysis', {})
        
        # Create detailed prompt for hero image
        prompt = f"""
        Create a detailed image prompt for the main hero image of this story:
        
        Title: {title}
        Category: {category}
        Content Summary: {content[:500]}
        
        Style: {style}
        Category-specific elements: {self._get_category_elements(category)}
        
        The image should:
        1. Capture the essence of the story
        2. Be visually striking and attention-grabbing
        3. Work well as a thumbnail/hero image
        4. Convey the emotional tone of the story
        5. Include relevant visual metaphors or symbols
        
        Return JSON with:
        {{
            "prompt": "detailed image generation prompt",
            "mood": "emotional mood of the image",
            "color_palette": ["specific colors to use"],
            "composition_notes": "composition and framing notes",
            "technical_requirements": {{
                "lighting": "lighting description",
                "perspective": "camera angle/perspective",
                "depth_of_field": "depth of field settings",
                "style_elements": ["specific style elements"]
            }},
            "target_emotion": "primary emotion to evoke",
            "cultural_context": "cultural considerations",
            "narrative_purpose": "how this image serves the story"
        }}
        """
        
        try:
            response = await self.model.generate_content(prompt)
            prompt_data = self._extract_json_from_response(response.text)
            
            return ImagePrompt(
                prompt=prompt_data.get('prompt', self._create_fallback_hero_prompt(story_data, style)),
                style=style,
                aspect_ratio=self.config['default_aspect_ratio'],
                quality=self.config['default_quality'],
                mood=prompt_data.get('mood', 'dramatic'),
                color_palette=prompt_data.get('color_palette', self.config['color_palettes'].get(category, ['blue', 'white'])),
                composition_notes=prompt_data.get('composition_notes', 'Center composition with strong focal point'),
                technical_requirements=prompt_data.get('technical_requirements', {}),
                target_emotion=prompt_data.get('target_emotion', 'curiosity'),
                cultural_context=prompt_data.get('cultural_context', 'universal appeal'),
                narrative_purpose=prompt_data.get('narrative_purpose', 'establish story theme')
            )
            
        except Exception as e:
            logger.error(f"Error generating hero prompt: {e}")
            return self._create_fallback_hero_prompt_obj(story_data, style)
    
    async def _generate_supporting_prompt(self, story_data: Dict, style: str, image_index: int) -> ImagePrompt:
        """Generate supporting image prompts"""
        
        title = story_data.get('title', '')
        content = story_data.get('content', '')
        category = story_data.get('category', 'general')
        
        # Determine the focus of this supporting image
        focus_types = ['detail', 'context', 'emotion', 'action', 'consequence']
        focus = focus_types[image_index % len(focus_types)]
        
        prompt = f"""
        Create a supporting image prompt for this story (focus: {focus}):
        
        Title: {title}
        Category: {category}
        Content: {content[:300]}
        
        Style: {style}
        Image Focus: {focus}
        
        This supporting image should:
        1. Complement the hero image
        2. Focus on: {focus}
        3. Provide additional visual context
        4. Maintain visual consistency with the hero image
        
        Return JSON with:
        {{
            "prompt": "detailed supporting image prompt",
            "mood": "emotional mood",
            "color_palette": ["colors to use"],
            "composition_notes": "composition notes",
            "technical_requirements": {{
                "lighting": "lighting description",
                "perspective": "camera perspective",
                "style_consistency": "how to maintain style consistency"
            }},
            "target_emotion": "emotion to evoke",
            "narrative_purpose": "how this supports the story"
        }}
        """
        
        try:
            response = await self.model.generate_content(prompt)
            prompt_data = self._extract_json_from_response(response.text)
            
            return ImagePrompt(
                prompt=prompt_data.get('prompt', self._create_fallback_supporting_prompt(story_data, style, focus)),
                style=style,
                aspect_ratio=self.config['default_aspect_ratio'],
                quality=self.config['default_quality'],
                mood=prompt_data.get('mood', 'supportive'),
                color_palette=prompt_data.get('color_palette', self.config['color_palettes'].get(category, ['blue', 'white'])),
                composition_notes=prompt_data.get('composition_notes', 'Supporting composition'),
                technical_requirements=prompt_data.get('technical_requirements', {}),
                target_emotion=prompt_data.get('target_emotion', 'understanding'),
                cultural_context=prompt_data.get('cultural_context', 'consistent with hero image'),
                narrative_purpose=prompt_data.get('narrative_purpose', f'provide {focus} context')
            )
            
        except Exception as e:
            logger.error(f"Error generating supporting prompt: {e}")
            return self._create_fallback_supporting_prompt_obj(story_data, style, focus)
    
    def _get_category_elements(self, category: str) -> List[str]:
        """Get category-specific visual elements"""
        category_elements = {
            'technology': ['futuristic interfaces', 'digital displays', 'circuit patterns', 'holographic elements', 'robotic components'],
            'business': ['modern offices', 'financial charts', 'corporate settings', 'professional attire', 'meeting rooms'],
            'politics': ['government buildings', 'flags', 'podiums', 'crowds', 'symbols of power', 'document signing'],
            'sports': ['dynamic action poses', 'sports equipment', 'stadiums', 'crowds cheering', 'victory moments', 'training scenes'],
            'entertainment': ['spotlights', 'red carpets', 'cameras', 'microphones', 'performance stages', 'celebration scenes'],
            'science': ['laboratories', 'microscopes', 'chemical equipment', 'space elements', 'research settings', 'discovery moments'],
            'world': ['globes', 'maps', 'international landmarks', 'cultural symbols', 'diverse crowds', 'global connections'],
            'health': ['medical equipment', 'hospitals', 'healthy lifestyle imagery', 'medical professionals', 'wellness symbols'],
            'environment': ['natural landscapes', 'green imagery', 'renewable energy', 'wildlife', 'conservation symbols', 'earth elements']
        }
        
        return category_elements.get(category, ['neutral backgrounds', 'simple compositions', 'universal symbols'])
    
    def _create_fallback_hero_prompt(self, story_data: Dict, style: str) -> str:
        """Create fallback hero prompt when AI generation fails"""
        title = story_data.get('title', 'News Story')
        category = story_data.get('category', 'general')
        
        base_prompt = f"{style}, hero image for news story about {title}"
        
        # Add category-specific elements
        if category == 'technology':
            base_prompt += ", futuristic setting, digital elements, modern technology"
        elif category == 'business':
            base_prompt += ", professional setting, corporate environment, business elements"
        elif category == 'politics':
            base_prompt += ", official setting, government elements, serious tone"
        elif category == 'sports':
            base_prompt += ", dynamic action, athletic elements, energetic composition"
        elif category == 'entertainment':
            base_prompt += ", vibrant colors, entertainment setting, engaging atmosphere"
        elif category == 'science':
            base_prompt += ", scientific setting, research elements, discovery theme"
        elif category == 'world':
            base_prompt += ", global elements, international setting, diverse imagery"
        elif category == 'health':
            base_prompt += ", medical setting, health imagery, wellness theme"
        elif category == 'environment':
            base_prompt += ", natural setting, environmental elements, earth-friendly theme"
        
        base_prompt += ", high quality, detailed, visually striking, attention-grabbing"
        
        return base_prompt
    
    def _create_fallback_hero_prompt_obj(self, story_data: Dict, style: str) -> ImagePrompt:
        """Create fallback hero prompt object"""
        return ImagePrompt(
            prompt=self._create_fallback_hero_prompt(story_data, style),
            style=style,
            aspect_ratio=self.config['default_aspect_ratio'],
            quality=self.config['default_quality'],
            mood='dramatic',
            color_palette=['blue', 'white'],
            composition_notes='Center composition with strong focal point',
            technical_requirements={},
            target_emotion='curiosity',
            cultural_context='universal appeal',
            narrative_purpose='establish story theme'
        )
    
    def _create_fallback_supporting_prompt(self, story_data: Dict, style: str, focus: str) -> str:
        """Create fallback supporting prompt"""
        title = story_data.get('title', 'News Story')
        return f"{style}, supporting image for {title}, focus on {focus}, complementary to main image, detailed, high quality"
    
    def _create_fallback_supporting_prompt_obj(self, story_data: Dict, style: str, focus: str) -> ImagePrompt:
        """Create fallback supporting prompt object"""
        return ImagePrompt(
            prompt=self._create_fallback_supporting_prompt(story_data, style, focus),
            style=style,
            aspect_ratio=self.config['default_aspect_ratio'],
            quality=self.config['default_quality'],
            mood='supportive',
            color_palette=['blue', 'white'],
            composition_notes='Supporting composition',
            technical_requirements={},
            target_emotion='understanding',
            cultural_context='consistent with hero image',
            narrative_purpose=f'provide {focus} context'
        )
    
    def _create_fallback_prompt(self, story_data: Dict, style: str) -> ImagePrompt:
        """Create fallback prompt when all generation fails"""
        return ImagePrompt(
            prompt=f"{style}, news story illustration, {story_data.get('title', 'story')}, high quality, detailed",
            style=style,
            aspect_ratio=self.config['default_aspect_ratio'],
            quality=self.config['default_quality'],
            mood='neutral',
            color_palette=['blue', 'white'],
            composition_notes='Simple composition',
            technical_requirements={},
            target_emotion='neutral',
            cultural_context='general',
            narrative_purpose='illustrate story'
        )
    
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
    
    def get_style_guide(self) -> Dict:
        """Get comprehensive style guide for image generation"""
        return {
            'available_styles': self.config['available_styles'],
            'anime_elements': self.anime_style_elements,
            'color_palettes': self.config['color_palettes'],
            'moods': self.config['moods'],
            'aspect_ratios': self.config['aspect_ratios'],
            'quality_levels': self.config['quality_levels'],
            'technical_considerations': {
                'lighting': 'Consider dramatic lighting for emotional impact',
                'composition': 'Use rule of thirds and leading lines',
                'color_theory': 'Use complementary colors for visual harmony',
                'cultural_sensitivity': 'Be mindful of cultural symbols and representations'
            }
        }
    
    def optimize_prompt_for_gemini_image(self, prompt: ImagePrompt) -> str:
        """Optimize prompt specifically for Gemini 2.5 Flash Image model"""
        
        # Start with style specification
        optimized_prompt = f"{prompt.style}, "
        
        # Add main prompt
        optimized_prompt += f"{prompt.prompt}, "
        
        # Add technical specifications
        optimized_prompt += f"{prompt.quality} quality, "
        optimized_prompt += f"{prompt.aspect_ratio} aspect ratio, "
        optimized_prompt += f"{prompt.mood} mood, "
        
        # Add color palette
        if prompt.color_palette:
            optimized_prompt += f"colors: {', '.join(prompt.color_palette)}, "
        
        # Add composition notes
        if prompt.composition_notes:
            optimized_prompt += f"composition: {prompt.composition_notes}, "
        
        # Add anime-specific elements if applicable
        if 'anime' in prompt.style.lower():
            optimized_prompt += "detailed anime style, expressive characters, dynamic composition, "
        
        # Add target emotion
        optimized_prompt += f"evokes {prompt.target_emotion}, "
        
        # Ensure prompt length is appropriate
        if len(optimized_prompt) > self.config['max_prompt_length']:
            optimized_prompt = optimized_prompt[:self.config['max_prompt_length']]
        
        return optimized_prompt.strip()

# Example usage
async def example_usage():
    generator = ImagePromptGenerator()
    
    try:
        await generator.initialize()
        
        # Example story data
        story_data = {
            'title': 'Revolutionary AI Breakthrough in Medical Diagnosis',
            'content': 'Scientists at Stanford University have developed an AI system that can diagnose rare diseases with 99% accuracy. This breakthrough could revolutionize healthcare by enabling earlier detection of life-threatening conditions.',
            'category': 'technology',
            'analysis': {
                'sentiment': 'positive',
                'key_topics': ['AI', 'medical diagnosis', 'healthcare', 'Stanford University'],
                'target_audience': 'general',
                'emotional_appeal': 0.8
            }
        }
        
        # Generate prompts
        prompts = await generator.generate_prompts(story_data, style='anime forge style', num_images=3)
        
        print(f"Generated {len(prompts)} image prompts:")
        for i, prompt in enumerate(prompts):
            print(f"\nPrompt {i+1}:")
            print(f"Style: {prompt.style}")
            print(f"Mood: {prompt.mood}")
            print(f"Target Emotion: {prompt.target_emotion}")
            print(f"Prompt: {prompt.prompt[:100]}...")
            print(f"Color Palette: {prompt.color_palette}")
        
        # Get style guide
        style_guide = generator.get_style_guide()
        print(f"\nAvailable styles: {style_guide['available_styles']}")
        
        # Optimize prompt for Gemini
        if prompts:
            optimized = generator.optimize_prompt_for_gemini_image(prompts[0])
            print(f"\nOptimized prompt for Gemini: {optimized[:150]}...")
        
    except Exception as e:
        print(f"Error in example usage: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())



















