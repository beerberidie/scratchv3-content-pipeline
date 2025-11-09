"""
Dynamic rule parsing service for content generation
"""
import re
from typing import Dict, Tuple, Any, List


def parse_rules(raw_rules: str) -> Tuple[Dict[str, Any], str]:
    """
    Parse free-form rules text into structured flags and leftover text.
    
    Args:
        raw_rules: Free-form rules text from user input
        
    Returns:
        Tuple of (flags_dict, leftover_text)
        - flags_dict: Structured flags that can be used programmatically
        - leftover_text: Remaining text that couldn't be parsed into flags
    """
    if not raw_rules or not raw_rules.strip():
        return {}, ""
    
    flags = {}
    processed_parts = []
    remaining_text = raw_rules
    
    # Define rule patterns and their corresponding flags
    rule_patterns = [
        # Language and locale patterns
        (r'\b(UK|British|GB)\s+(English|ENG)\b', 'language', 'uk_english'),
        (r'\b(US|American|USA)\s+(English|ENG)\b', 'language', 'us_english'),
        (r'\b(AU|Australian|AUS)\s+(English|ENG)\b', 'language', 'au_english'),
        (r'\b(CA|Canadian|CAN)\s+(English|ENG)\b', 'language', 'ca_english'),
        
        # South African context patterns
        (r'\b(SA|South\s+African?)\s+(seasons?|weather|climate)\b', 'context', 'sa_seasons'),
        (r'\b(SA|South\s+African?)\s+(context|perspective|viewpoint)\b', 'context', 'sa_perspective'),
        (r'\b(SA|South\s+African?)\s+(market|economy|business)\b', 'context', 'sa_market'),
        
        # Style patterns
        (r'\bavoid\s+bullet\s+points?\b', 'style', 'no_bullets'),
        (r'\bno\s+bullet\s+points?\b', 'style', 'no_bullets'),
        (r'\bavoid\s+lists?\b', 'style', 'no_lists'),
        (r'\bno\s+lists?\b', 'style', 'no_lists'),
        (r'\bavoid\s+emojis?\b', 'style', 'no_emojis'),
        (r'\bno\s+emojis?\b', 'style', 'no_emojis'),
        (r'\bavoid\s+em[\-\s]?dashes?\b', 'style', 'no_em_dashes'),
        (r'\bno\s+em[\-\s]?dashes?\b', 'style', 'no_em_dashes'),
        
        # Tone patterns
        (r'\bprofessional\s+tone\b', 'tone', 'professional'),
        (r'\bcasual\s+tone\b', 'tone', 'casual'),
        (r'\bformal\s+tone\b', 'tone', 'formal'),
        (r'\bconversational\s+tone\b', 'tone', 'conversational'),
        (r'\bfriendly\s+tone\b', 'tone', 'friendly'),
        
        # Length patterns
        (r'\bshort\s+(article|post|content)\b', 'length', 'short'),
        (r'\blong\s+(article|post|content)\b', 'length', 'long'),
        (r'\bmedium\s+(article|post|content)\b', 'length', 'medium'),
        (r'\bconcise\b', 'length', 'concise'),
        (r'\bdetailed\b', 'length', 'detailed'),
        
        # Format patterns
        (r'\bmarkdown\s+format(ting)?\b', 'format', 'markdown'),
        (r'\bhtml\s+format(ting)?\b', 'format', 'html'),
        (r'\bplain\s+text\b', 'format', 'plain_text'),

        # Heading case patterns
        (r'\bsentence\s+case\b', 'heading_case', 'sentence'),
        (r'\btitle\s+case\b', 'heading_case', 'title'),
        (r'\blowercase\s+headings?\b', 'heading_case', 'lower'),
        (r'\bsentence\s+case\s+headings?\b', 'heading_case', 'sentence'),

        # SEO patterns
        (r'\bSEO\s+optimized?\b', 'seo', 'optimized'),
        (r'\binclude\s+keywords?\b', 'seo', 'include_keywords'),
        (r'\bmeta\s+description\b', 'seo', 'meta_description'),
    ]
    
    # Process each pattern
    for pattern, flag_category, flag_value in rule_patterns:
        matches = re.finditer(pattern, remaining_text, re.IGNORECASE)
        for match in matches:
            # Store the flag
            if flag_category not in flags:
                flags[flag_category] = []
            if flag_value not in flags[flag_category]:
                flags[flag_category].append(flag_value)
            
            # Mark this text as processed
            processed_parts.append((match.start(), match.end(), match.group()))
    
    # Remove processed parts from remaining text
    if processed_parts:
        # Sort by start position in reverse order to maintain indices
        processed_parts.sort(key=lambda x: x[0], reverse=True)
        
        for start, end, matched_text in processed_parts:
            remaining_text = remaining_text[:start] + remaining_text[end:]
    
    # Clean up remaining text
    leftover_text = re.sub(r'\s+', ' ', remaining_text).strip()
    leftover_text = re.sub(r'[,;]\s*$', '', leftover_text)  # Remove trailing punctuation
    
    # Convert single-item lists to strings for easier handling
    for category in flags:
        if len(flags[category]) == 1:
            flags[category] = flags[category][0]
    
    return flags, leftover_text


def get_style_instructions(flags: Dict[str, Any]) -> List[str]:
    """
    Convert parsed flags into specific style instructions for the AI.
    
    Args:
        flags: Parsed flags dictionary from parse_rules()
        
    Returns:
        List of specific instructions for the AI
    """
    instructions = []
    
    # Language instructions
    language = flags.get('language')
    if language == 'uk_english':
        instructions.append("Use British English spelling and terminology (colour, realise, centre, etc.)")
    elif language == 'us_english':
        instructions.append("Use American English spelling and terminology (color, realize, center, etc.)")
    elif language == 'au_english':
        instructions.append("Use Australian English spelling and terminology")
    elif language == 'ca_english':
        instructions.append("Use Canadian English spelling and terminology")
    
    # Context instructions
    context = flags.get('context')
    if context:
        if 'sa_seasons' in str(context):
            instructions.append("Consider South African seasons (summer: Dec-Feb, autumn: Mar-May, winter: Jun-Aug, spring: Sep-Nov)")
        if 'sa_perspective' in str(context):
            instructions.append("Write from a South African perspective, considering local context and culture")
        if 'sa_market' in str(context):
            instructions.append("Focus on South African market conditions and business environment")
    
    # Style instructions
    style = flags.get('style')
    if style:
        if 'no_bullets' in str(style):
            instructions.append("Avoid using bullet points or numbered lists")
        if 'no_lists' in str(style):
            instructions.append("Avoid using any form of lists")
        if 'no_emojis' in str(style):
            instructions.append("Do not use any emojis or emoticons")
        if 'no_em_dashes' in str(style):
            instructions.append("Avoid using em-dashes (—) in the text")
    
    # Tone instructions
    tone = flags.get('tone')
    if tone:
        instructions.append(f"Use a {tone} tone throughout the content")
    
    # Length instructions
    length = flags.get('length')
    if length == 'short':
        instructions.append("Keep the content concise and brief")
    elif length == 'long':
        instructions.append("Create comprehensive, detailed content")
    elif length == 'medium':
        instructions.append("Aim for moderate length content")
    elif length == 'concise':
        instructions.append("Be concise and to the point")
    elif length == 'detailed':
        instructions.append("Provide detailed explanations and examples")
    
    # Format instructions
    format_type = flags.get('format')
    if format_type == 'markdown':
        instructions.append("Format the content using proper Markdown syntax")
    elif format_type == 'html':
        instructions.append("Format the content using HTML tags")
    elif format_type == 'plain_text':
        instructions.append("Use plain text formatting without special markup")
    
    # SEO instructions
    seo = flags.get('seo')
    if seo:
        if 'optimized' in str(seo):
            instructions.append("Optimize content for search engines with relevant keywords")
        if 'include_keywords' in str(seo):
            instructions.append("Naturally incorporate relevant keywords throughout the content")
        if 'meta_description' in str(seo):
            instructions.append("Include a compelling meta description")
    
    return instructions


def format_rule_examples() -> str:
    """
    Return formatted examples of rule patterns that users can use.
    
    Returns:
        String with example rule patterns
    """
    examples = [
        "Language: 'UK ENG', 'US English', 'Australian English'",
        "Style: 'avoid bullet points', 'no emojis', 'professional tone'",
        "Context: 'SA seasons', 'South African perspective'",
        "Length: 'short article', 'detailed content', 'concise'",
        "Format: 'markdown formatting', 'HTML format'",
        "SEO: 'SEO optimized', 'include keywords'"
    ]
    return "\n".join(f"• {example}" for example in examples)
