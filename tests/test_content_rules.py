"""
Tests for content rules parsing and QA filtering functionality
"""
import pytest
from app.services.rules import parse_rules, get_style_instructions, format_rule_examples
from app.services.prompt_builder import PromptBuilder, PromptSettings
from app.services.content_generator import ContentGenerationEngine
from app.models.base import ContentType


class TestRuleParsing:
    """Test dynamic rule parsing functionality"""
    
    def test_parse_language_rules(self):
        """Test parsing of language-specific rules"""
        rules = "UK English, avoid bullet points, professional tone"
        flags, leftover = parse_rules(rules)
        
        assert flags['language'] == 'uk_english'
        assert 'no_bullets' in flags['style']
        assert flags['tone'] == 'professional'
        assert leftover == ""
    
    def test_parse_south_african_context(self):
        """Test parsing of South African context rules"""
        rules = "SA seasons, South African perspective, no emojis"
        flags, leftover = parse_rules(rules)
        
        assert 'sa_seasons' in flags['context']
        assert 'sa_perspective' in flags['context']
        assert 'no_emojis' in flags['style']
    
    def test_parse_mixed_rules_with_leftover(self):
        """Test parsing mixed rules with unrecognized content"""
        rules = "UK ENG, custom instruction here, avoid em-dashes, another custom note"
        flags, leftover = parse_rules(rules)
        
        assert flags['language'] == 'uk_english'
        assert 'no_em_dashes' in flags['style']
        assert "custom instruction here" in leftover
        assert "another custom note" in leftover
    
    def test_parse_empty_rules(self):
        """Test parsing empty or None rules"""
        flags, leftover = parse_rules("")
        assert flags == {}
        assert leftover == ""
        
        flags, leftover = parse_rules(None)
        assert flags == {}
        assert leftover == ""
    
    def test_get_style_instructions(self):
        """Test conversion of flags to style instructions"""
        flags = {
            'language': 'uk_english',
            'style': ['no_bullets', 'no_emojis'],
            'tone': 'professional',
            'context': 'sa_seasons'
        }
        
        instructions = get_style_instructions(flags)
        
        assert any("British English" in inst for inst in instructions)
        assert any("bullet points" in inst for inst in instructions)
        assert any("emojis" in inst for inst in instructions)
        assert any("professional tone" in inst for inst in instructions)
        assert any("South African seasons" in inst for inst in instructions)
    
    def test_format_rule_examples(self):
        """Test rule examples formatting"""
        examples = format_rule_examples()
        
        assert "UK ENG" in examples
        assert "avoid bullet points" in examples
        assert "SA seasons" in examples
        assert "professional tone" in examples


class TestPromptBuilder:
    """Test PromptBuilder functionality"""
    
    def test_prompt_settings_creation(self):
        """Test PromptSettings creation and defaults"""
        settings = PromptSettings()
        
        assert settings.language == "us_english"
        assert settings.tone == "professional"
        assert not settings.avoid_bullets
        assert not settings.avoid_emojis
        assert settings.format_type == "markdown"
    
    def test_prompt_builder_system_prompt(self):
        """Test system prompt generation"""
        settings = PromptSettings(
            language="uk_english",
            avoid_bullets=True,
            avoid_emojis=True,
            tone="casual"
        )
        
        builder = PromptBuilder(settings)
        system_prompt = builder.build_system_prompt(ContentType.BLOG)
        
        assert "British English" in system_prompt
        assert "bullet points" in system_prompt
        assert "emojis" in system_prompt
        assert "casual" in system_prompt
    
    def test_prompt_builder_user_prompt(self):
        """Test user prompt generation"""
        settings = PromptSettings(avoid_lists=True)
        builder = PromptBuilder(settings)
        
        user_prompt = builder.build_user_prompt(
            topic="AI Content Strategy",
            content_type=ContentType.ARTICLE,
            referenced_content="Chat context about AI",
            extra_rules="Custom rule here"
        )
        
        assert "AI Content Strategy" in user_prompt
        assert "Chat context about AI" in user_prompt
        assert "Custom rule here" in user_prompt
    
    def test_prompt_builder_messages(self):
        """Test complete message building"""
        settings = PromptSettings(language="uk_english")
        builder = PromptBuilder(settings)
        
        messages = builder.build_messages(
            topic="Test Topic",
            content_type=ContentType.BLOG
        )
        
        assert len(messages) == 2
        assert messages[0]['role'] == 'system'
        assert messages[1]['role'] == 'user'
        assert "British English" in messages[0]['content']
        assert "Test Topic" in messages[1]['content']


class TestQAFilter:
    """Test QA filtering functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.content_engine = ContentGenerationEngine()
    
    def test_remove_bullet_points(self):
        """Test removal of various bullet point styles"""
        content_with_bullets = """
Here is some content:
• First bullet point
- Second bullet point
* Third bullet point
1. Numbered point
a. Lettered point
"""
        
        filtered = self.content_engine._qa_filter(content_with_bullets)
        
        assert "•" not in filtered
        assert "First bullet point" in filtered  # Content preserved
        assert "- Second bullet point" not in filtered  # Bullet removed
        assert "* Third bullet point" not in filtered  # Bullet removed
        assert "1. Numbered point" not in filtered  # Number removed
    
    def test_remove_emojis(self):
        """Test removal of emojis and emoticons"""
        content_with_emojis = """
Great content! 😊 This is amazing 🎉
Also check this out :) and this :D
Some hearts ♥ and <3 too
"""
        
        filtered = self.content_engine._qa_filter(content_with_emojis)
        
        assert "😊" not in filtered
        assert "🎉" not in filtered
        assert ":)" not in filtered
        assert ":D" not in filtered
        assert "♥" not in filtered
        assert "<3" not in filtered
        assert "Great content!" in filtered  # Text preserved
    
    def test_remove_em_dashes(self):
        """Test removal and replacement of em-dashes"""
        content_with_dashes = """
This is content—with em-dashes—throughout the text.
Also en-dashes–like this–should be handled.
"""
        
        filtered = self.content_engine._qa_filter(content_with_dashes)
        
        assert "—" not in filtered
        assert "–" not in filtered
        assert " - " in filtered  # Replaced with regular dash
    
    def test_us_to_uk_spelling_conversion(self):
        """Test conversion of US spellings to UK spellings"""
        us_content = """
The color of the organization was analyzed by the center.
We need to realize the favor and honor the labor.
The theater and defense were organized properly.
"""
        
        filtered = self.content_engine._qa_filter(us_content)
        
        # Check UK spellings are used
        assert "colour" in filtered
        assert "organisation" in filtered
        assert "analysed" in filtered
        assert "centre" in filtered
        assert "realise" in filtered
        assert "favour" in filtered
        assert "honour" in filtered
        assert "labour" in filtered
        assert "theatre" in filtered
        assert "defence" in filtered
        assert "organised" in filtered
        
        # Check US spellings are removed
        assert "color" not in filtered
        assert "organization" not in filtered
        assert "analyzed" not in filtered
        assert "center" not in filtered
    
    def test_whitespace_cleanup(self):
        """Test cleanup of extra whitespace"""
        messy_content = """
This   has    extra     spaces.


And   too   many   line   breaks.



Also  tabs	and	mixed	whitespace.
"""
        
        filtered = self.content_engine._qa_filter(messy_content)
        
        # Should have single spaces
        assert "  " not in filtered  # No double spaces
        assert "\t" not in filtered  # No tabs
        
        # Should have at most double line breaks
        assert "\n\n\n" not in filtered
    
    def test_empty_content_handling(self):
        """Test handling of empty or None content"""
        assert self.content_engine._qa_filter("") == ""
        assert self.content_engine._qa_filter(None) == None
    
    def test_comprehensive_filtering(self):
        """Test comprehensive filtering with multiple issues"""
        problematic_content = """
# AI Content Strategy 😊

Here are the key points:
• Use AI for content creation
- Maintain quality control 🎉
* Ensure brand consistency

The color of your organization should be analyzed—this is important.
We need to realize the favor of automation :)

1. First step
2. Second step  
3. Third step

This content has   extra   spaces   and


too many line breaks.
"""
        
        filtered = self.content_engine._qa_filter(problematic_content)
        
        # Check all issues are addressed
        assert "😊" not in filtered  # Emojis removed
        assert "🎉" not in filtered
        assert ":)" not in filtered
        assert "•" not in filtered  # Bullets removed
        assert "-" not in "- Maintain" or "- Maintain" not in filtered
        assert "*" not in "* Ensure" or "* Ensure" not in filtered
        assert "1." not in filtered  # Numbers removed
        assert "—" not in filtered  # Em-dashes replaced
        assert "colour" in filtered  # US->UK spelling
        assert "organisation" in filtered
        assert "analysed" in filtered
        assert "realise" in filtered
        assert "favour" in filtered
        assert "   " not in filtered  # Extra spaces removed
        assert "\n\n\n" not in filtered  # Extra line breaks removed
        
        # Check content is preserved
        assert "AI Content Strategy" in filtered
        assert "quality control" in filtered
        assert "brand consistency" in filtered
