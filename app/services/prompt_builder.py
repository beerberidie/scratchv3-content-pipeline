"""
Advanced prompt building system for content generation
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

from app.models.base import ContentType


class PromptStyle(Enum):
    """Enumeration of prompt styles"""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    FORMAL = "formal"
    CONVERSATIONAL = "conversational"
    CREATIVE = "creative"


@dataclass
class PromptSettings:
    """Settings for prompt generation"""

    # Language and locale
    language: str = "us_english"  # uk_english, us_english, au_english, ca_english

    # Content style
    tone: str = "professional"
    avoid_bullets: bool = False
    avoid_emojis: bool = False
    avoid_em_dashes: bool = False
    avoid_lists: bool = False

    # Formatting rules
    heading_case: str = "sentence"  # sentence, title, lower
    enforce_formatting: bool = True

    # Context
    sa_context: bool = False
    sa_seasons: bool = False
    sa_market: bool = False

    # Length and format
    length_preference: str = "medium"  # short, medium, long, concise, detailed
    format_type: str = "markdown"  # markdown, html, plain_text

    # SEO
    seo_optimized: bool = False
    include_keywords: bool = False

    # Provider-specific adjustments
    ai_provider: str = "lmstudio"  # lmstudio, openai, openrouter

    # Additional instructions
    extra_instructions: List[str] = None
    
    def __post_init__(self):
        if self.extra_instructions is None:
            self.extra_instructions = []


class PromptBuilder:
    """Advanced prompt builder for content generation"""
    
    def __init__(self, settings: PromptSettings):
        self.settings = settings
    
    def build_system_prompt(self, content_type: ContentType) -> str:
        """Build the system prompt based on settings and content type"""
        
        base_prompts = {
            ContentType.BLOG: "You are a professional blog writer who creates engaging, informative blog posts.",
            ContentType.ARTICLE: "You are a professional journalist and article writer who creates well-researched, informative articles.",
            ContentType.NEWS: "You are a professional news writer who creates factual, objective news articles.",
            ContentType.SOCIAL_POST: "You are a social media content creator who writes engaging, shareable posts."
        }
        
        system_prompt = base_prompts.get(content_type, base_prompts[ContentType.BLOG])
        
        # Add language specifications
        if self.settings.language == "uk_english":
            system_prompt += " You write in British English with proper UK spelling and terminology."
        elif self.settings.language == "au_english":
            system_prompt += " You write in Australian English with proper Australian spelling and terminology."
        elif self.settings.language == "ca_english":
            system_prompt += " You write in Canadian English with proper Canadian spelling and terminology."
        else:
            system_prompt += " You write in American English with proper US spelling and terminology."
        
        # Add style constraints
        constraints = []
        if self.settings.avoid_bullets:
            constraints.append("never use bullet points or numbered lists")
        if self.settings.avoid_emojis:
            constraints.append("never use emojis or emoticons")
        if self.settings.avoid_em_dashes:
            constraints.append("avoid using em-dashes (—)")
        if self.settings.avoid_lists:
            constraints.append("avoid using any form of lists")

        # Add formatting constraints
        if self.settings.enforce_formatting:
            if self.settings.heading_case == "sentence":
                constraints.append("use sentence case for all headings and subheadings (capitalize only the first word and proper nouns)")
            elif self.settings.heading_case == "title":
                constraints.append("use title case for all headings and subheadings")
            elif self.settings.heading_case == "lower":
                constraints.append("use lowercase for all headings and subheadings")

        if constraints:
            system_prompt += f" Important formatting rules: {', '.join(constraints)}."
        
        # Add context awareness
        if self.settings.sa_context:
            system_prompt += " You have deep knowledge of South African culture, context, and perspectives."
        
        if self.settings.sa_seasons:
            system_prompt += " Remember that South Africa is in the Southern Hemisphere with opposite seasons (summer: Dec-Feb, winter: Jun-Aug)."
        
        # Add tone specification
        system_prompt += f" Your writing tone should be {self.settings.tone}."

        # Add provider-specific adjustments
        if self.settings.ai_provider in ["openai", "openrouter"]:
            system_prompt += " Pay special attention to maintaining consistent tone and following all formatting rules precisely. When using referenced content, maintain the same style and voice throughout."

        return system_prompt
    
    def build_user_prompt(self, topic: str, content_type: ContentType, 
                         article_content: str = "", referenced_content: str = "", 
                         extra_rules: str = "") -> str:
        """Build the user prompt with all context and requirements"""
        
        # Start with content type specific prompt
        if content_type == ContentType.BLOG:
            prompt = f"Create a comprehensive blog post about: {topic}\n\n"
        elif content_type == ContentType.ARTICLE:
            prompt = f"Write a professional article about: {topic}\n\n"
        elif content_type == ContentType.NEWS:
            prompt = f"Write a news article about: {topic}\n\n"
        elif content_type == ContentType.SOCIAL_POST:
            prompt = f"Create engaging social media content about: {topic}\n\n"
        else:
            prompt = f"Create content about: {topic}\n\n"
        
        # Add reference material if provided
        if article_content:
            prompt += f"Reference material to incorporate:\n{article_content}\n\n"
        
        # Add chat context if provided
        if referenced_content:
            prompt += f"Additional context from conversations:\n{referenced_content}\n\n"
        
        # Add content requirements based on type
        prompt += self._get_content_requirements(content_type)
        
        # Add style and format instructions
        style_instructions = self._build_style_instructions()
        if style_instructions:
            prompt += f"\n\nStyle requirements:\n{style_instructions}"
        
        # Add extra rules if provided
        if extra_rules:
            prompt += f"\n\nAdditional guidelines:\n{extra_rules}"

        # Add provider-specific emphasis
        if self.settings.ai_provider in ["openai", "openrouter"]:
            prompt += "\n\nIMPORTANT: Follow ALL formatting rules precisely, especially heading case requirements. Maintain consistent tone throughout and pay special attention to the style guidelines provided."

        return prompt
    
    def _get_content_requirements(self, content_type: ContentType) -> str:
        """Get content-specific requirements"""
        
        if content_type == ContentType.BLOG:
            requirements = [
                "1. Create a compelling headline",
                "2. Write an engaging introduction",
                "3. Organize content with clear sections and subheadings",
                "4. Provide valuable insights and actionable information",
                "5. End with a strong conclusion",
                "6. Use proper formatting for readability"
            ]
        elif content_type == ContentType.ARTICLE:
            requirements = [
                "1. Create a professional headline",
                "2. Write a strong lead paragraph",
                "3. Present information in a logical structure",
                "4. Support points with evidence and examples",
                "5. Maintain objectivity and credibility",
                "6. Include a compelling conclusion"
            ]
        elif content_type == ContentType.NEWS:
            requirements = [
                "1. Write a compelling headline",
                "2. Follow the inverted pyramid structure",
                "3. Include who, what, when, where, why, and how",
                "4. Use clear, concise language",
                "5. Maintain journalistic objectivity",
                "6. Format appropriately for news publication"
            ]
        elif content_type == ContentType.SOCIAL_POST:
            requirements = [
                "1. Create attention-grabbing content",
                "2. Use an engaging, conversational tone",
                "3. Include relevant hashtags",
                "4. Add a clear call-to-action",
                "5. Optimize for social media engagement",
                "6. Consider platform character limits"
            ]
        else:
            requirements = [
                "1. Create engaging, well-structured content",
                "2. Provide valuable information",
                "3. Use clear, readable formatting",
                "4. Maintain consistent tone throughout"
            ]
        
        # Filter out list-related requirements if lists are avoided
        if self.settings.avoid_bullets or self.settings.avoid_lists:
            # Convert numbered requirements to paragraph form
            requirements_text = "Please ensure the content: "
            requirements_text += "; ".join([req.split(". ", 1)[1] for req in requirements])
            requirements_text += "."
            return requirements_text
        
        return "Please create content that:\n" + "\n".join(requirements)
    
    def _build_style_instructions(self) -> str:
        """Build style-specific instructions"""
        
        instructions = []
        
        # Length instructions
        if self.settings.length_preference == "short":
            instructions.append("Keep content concise and brief")
        elif self.settings.length_preference == "long":
            instructions.append("Create comprehensive, detailed content")
        elif self.settings.length_preference == "detailed":
            instructions.append("Provide detailed explanations and examples")
        elif self.settings.length_preference == "concise":
            instructions.append("Be concise and to the point")
        
        # Format instructions
        if self.settings.format_type == "markdown":
            instructions.append("Use proper Markdown formatting with clear heading hierarchy")
            if self.settings.heading_case == "sentence":
                instructions.append("Format all headings in sentence case (e.g., 'This is a heading' not 'This Is A Heading')")
        elif self.settings.format_type == "html":
            instructions.append("Format using HTML tags with proper heading structure")
            if self.settings.heading_case == "sentence":
                instructions.append("Use sentence case for all HTML headings")
        elif self.settings.format_type == "plain_text":
            instructions.append("Use plain text without special markup")
            if self.settings.heading_case == "sentence":
                instructions.append("Use sentence case for section headings")
        
        # SEO instructions
        if self.settings.seo_optimized:
            instructions.append("Optimize for search engines with relevant keywords")
        if self.settings.include_keywords:
            instructions.append("Naturally incorporate relevant keywords")
        
        # South African context
        if self.settings.sa_market:
            instructions.append("Focus on South African market conditions and business environment")
        
        # Add extra instructions
        instructions.extend(self.settings.extra_instructions)
        
        if not instructions:
            return ""
        
        # Format as paragraph if lists are avoided
        if self.settings.avoid_bullets or self.settings.avoid_lists:
            return "; ".join(instructions) + "."
        
        return "\n".join(f"• {instruction}" for instruction in instructions)
    
    def build_messages(self, topic: str, content_type: ContentType, 
                      article_content: str = "", referenced_content: str = "", 
                      extra_rules: str = "") -> List[Dict[str, str]]:
        """Build complete message array for AI API"""
        
        system_prompt = self.build_system_prompt(content_type)
        user_prompt = self.build_user_prompt(
            topic, content_type, article_content, referenced_content, extra_rules
        )
        
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
