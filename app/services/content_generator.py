"""
Content generation engine that orchestrates AI, images, and WordPress services
"""
import os
import re
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

from app.services.ai import ai_service
from app.services.images import image_service
from app.services.wordpress import wordpress_service
from app.services.storage import storage_service
from app.services.rules import parse_rules, get_style_instructions
from app.services.prompt_builder import PromptBuilder, PromptSettings
from app.models.base import TaskStatus, ContentType


class ContentGenerationEngine:
    """Main engine for generating and delivering content"""
    
    def __init__(self):
        self.generation_history = []
    
    async def process_task(self, task: Dict[str, Any], user_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single task and generate content"""
        
        task_id = task["id"]
        user_id = task["user_id"]
        
        try:
            # Update task status to in_progress
            storage_service.update_task(user_id, task_id, {"status": TaskStatus.IN_PROGRESS.value})
            
            # Generate content
            content_result = await self._generate_content(task, user_settings)
            
            if not content_result["success"]:
                # Mark task as failed
                storage_service.update_task(user_id, task_id, {
                    "status": TaskStatus.FAILED.value,
                    "error_message": content_result.get("error", "Content generation failed")
                })
                return content_result
            
            # Get images if requested
            images = []
            if task.get("include_image", False):
                image_result = await self._get_images(task, user_settings, content_result["content"])
                if image_result["success"]:
                    images = image_result["images"]
            
            # Prepare final content
            final_content = {
                "content": content_result["content"],
                "images": images,
                "topic": task["topic"],
                "content_type": task.get("content_type", ContentType.BLOG.value),
                "model_used": content_result["model_used"],
                "provider": content_result["provider"],
                "tokens_used": content_result["tokens_used"],
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Save to history
            content_id = storage_service.save_generated_content(user_id, task_id, final_content)
            
            # Post to WordPress if URL specified
            wordpress_result = {"success": True, "message": "No WordPress URL specified"}
            wordpress_url = task.get("wordpress_url")
            wordpress_warning = None

            if wordpress_url:
                logger.info(f"Attempting to post to WordPress: {wordpress_url}")
                wordpress_result = await self._post_to_wordpress(task, final_content, user_settings)
                logger.info(f"WordPress posting result: {wordpress_result}")

                # If WordPress posting failed, log the error but don't fail the task
                if not wordpress_result["success"]:
                    wordpress_warning = f"WordPress posting failed: {wordpress_result.get('error', 'Unknown error')}"
                    logger.warning(f"Task {task_id} completed but WordPress posting failed: {wordpress_warning}")
            else:
                logger.info("No WordPress URL specified, skipping WordPress posting")

            # Always mark task as completed - content generation succeeded
            # WordPress posting failure is treated as a warning, not a failure
            task_update = {
                "status": TaskStatus.COMPLETED.value,
                "generated_content": content_result["content"],
                "image_urls": [img["url"] for img in images],
                "content_id": content_id,
                "wordpress_posted": wordpress_result["success"],
                "wordpress_posted_at": (
                    datetime.now(timezone.utc).isoformat()
                    if wordpress_result["success"] else None
                ),
                "wordpress_post_id": (
                    wordpress_result.get("post", {}).get("id")
                    if wordpress_result["success"] else None
                ),
                "wordpress_edit_link": (
                    wordpress_result.get("post", {}).get("edit_link")
                    if wordpress_result["success"] else None
                )
            }

            # Add WordPress error as a warning message if posting failed
            if wordpress_warning:
                task_update["wordpress_error"] = wordpress_result.get("error", "Unknown error")
                task_update["warning_message"] = wordpress_warning

            storage_service.update_task(user_id, task_id, task_update)

            # Return success with WordPress warning if applicable
            result = {
                "success": True,
                "task_id": task_id,
                "content_id": content_id,
                "content": final_content,
                "wordpress_result": wordpress_result
            }

            # Include warning in result if WordPress posting failed
            if wordpress_warning:
                result["warning"] = wordpress_warning

            return result
            
        except Exception as e:
            # Mark task as failed
            storage_service.update_task(user_id, task_id, {
                "status": TaskStatus.FAILED.value,
                "error_message": str(e)
            })
            
            return {
                "success": False,
                "task_id": task_id,
                "error": str(e)
            }
    
    async def _generate_content(self, task: Dict[str, Any], user_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content using AI service with dynamic rule parsing and PromptBuilder"""

        # Parse rules into structured flags and leftover text
        raw_rules = task.get("rules", "")
        flags, extra_rules = parse_rules(raw_rules)

        # Create PromptSettings from parsed flags
        settings = PromptSettings()

        # Apply language settings
        if flags.get("language"):
            settings.language = flags["language"]

        # Apply style settings
        style_flags = flags.get("style", [])
        if isinstance(style_flags, str):
            style_flags = [style_flags]

        settings.avoid_bullets = "no_bullets" in style_flags
        settings.avoid_emojis = "no_emojis" in style_flags
        settings.avoid_em_dashes = "no_em_dashes" in style_flags
        settings.avoid_lists = "no_lists" in style_flags

        # Apply tone settings
        if flags.get("tone"):
            settings.tone = flags["tone"]

        # Apply context settings
        context_flags = flags.get("context", [])
        if isinstance(context_flags, str):
            context_flags = [context_flags]

        settings.sa_seasons = "sa_seasons" in context_flags
        settings.sa_context = "sa_perspective" in context_flags
        settings.sa_market = "sa_market" in context_flags

        # Apply length settings
        if flags.get("length"):
            settings.length_preference = flags["length"]

        # Apply format settings
        if flags.get("format"):
            settings.format_type = flags["format"]

        # Apply SEO settings
        seo_flags = flags.get("seo", [])
        if isinstance(seo_flags, str):
            seo_flags = [seo_flags]

        settings.seo_optimized = "optimized" in seo_flags
        settings.include_keywords = "include_keywords" in seo_flags

        # Apply heading case settings
        if flags.get("heading_case"):
            settings.heading_case = flags["heading_case"]

        # Set AI provider from user settings
        settings.ai_provider = user_settings.get("ai_provider", "lmstudio")

        # Add any additional style instructions
        style_instructions = get_style_instructions(flags)
        if style_instructions:
            settings.extra_instructions.extend(style_instructions)

        # Add chat-derived style instructions
        if chat_style_analysis:
            chat_instructions = self.build_chat_style_instructions(chat_style_analysis)
            if chat_instructions:
                settings.extra_instructions.extend(chat_instructions)

        # Create PromptBuilder with settings
        content_type = ContentType(task.get("content_type", ContentType.BLOG.value))
        prompt_builder = PromptBuilder(settings)

        # Load referenced chat content and analyze for tone/style
        referenced_content = ""
        chat_style_analysis = {}
        if task.get("referenced_chats"):
            referenced_content = self.load_chats(task["user_id"], task["referenced_chats"])
            chat_style_analysis = self.analyze_chat_style(referenced_content)

        # Build messages using PromptBuilder
        messages = prompt_builder.build_messages(
            topic=task["topic"],
            content_type=content_type,
            article_content=task.get("article_content", ""),
            referenced_content=referenced_content,
            extra_rules=extra_rules
        )

        # Get AI provider and model from user settings with proper defaults
        from app.config import settings
        ai_provider = user_settings.get("ai_provider", settings.default_ai_provider)

        if ai_provider == "openai":
            model = user_settings.get("openai_model", settings.default_openai_model)
        elif ai_provider == "lmstudio":
            model = user_settings.get("lmstudio_model", settings.default_lmstudio_model)
        else:  # openrouter
            model = user_settings.get("openrouter_model", settings.default_openrouter_model)

        # Add user_id to user_settings for API key lookup
        # We need to get the user's email for encrypted key lookup
        from app.services.auth import auth_service
        user_data = auth_service.get_user(task["user_id"])
        user_email = user_data.get("email") if user_data else task["user_id"]

        enhanced_user_settings = user_settings.copy()
        enhanced_user_settings["user_id"] = user_email  # Use email for encrypted key lookup

        # Generate content using the new message format
        result = await ai_service.generate_content_with_messages(
            messages=messages,
            provider=ai_provider,
            model=model,
            user_settings=enhanced_user_settings,
            max_tokens=2000,
            temperature=0.7
        )

        # Apply QA filter immediately after AI response
        if result.get("success") and result.get("content"):
            filtered_content = self._qa_filter(result["content"])
            result["content"] = filtered_content

        return result
    
    def _build_content_prompt(self, task: Dict[str, Any]) -> str:
        """Build a comprehensive prompt for content generation"""
        
        topic = task["topic"]
        rules = task.get("rules", "")
        article_content = task.get("article_content", "")
        content_type = task.get("content_type", ContentType.BLOG.value)
        
        # Load referenced chat files
        referenced_content = ""
        if task.get("referenced_chats"):
            referenced_content = self._load_referenced_chats(task["user_id"], task["referenced_chats"])
        
        # Build prompt based on content type
        if content_type == ContentType.BLOG.value:
            prompt = f"""Create a comprehensive blog post about: {topic}

{f"Additional guidelines: {rules}" if rules else ""}

{f"Reference material to incorporate: {article_content}" if article_content else ""}

{f"Referenced conversations/context: {referenced_content}" if referenced_content else ""}

Please create an engaging, well-structured blog post that:
1. Has a compelling headline
2. Includes an engaging introduction
3. Has well-organized sections with subheadings
4. Provides valuable insights and information
5. Ends with a strong conclusion
6. Uses markdown formatting for better readability

Make the content informative, engaging, and suitable for publication."""

        elif content_type == ContentType.ARTICLE.value:
            prompt = f"""Write a professional article about: {topic}

{f"Writing guidelines: {rules}" if rules else ""}

{f"Source material: {article_content}" if article_content else ""}

{f"Additional context: {referenced_content}" if referenced_content else ""}

Create a well-researched, authoritative article that:
1. Has a clear, informative title
2. Provides comprehensive coverage of the topic
3. Uses proper structure with headings and subheadings
4. Includes relevant examples and insights
5. Maintains a professional tone throughout
6. Is formatted with markdown for clarity"""

        elif content_type == ContentType.NEWS.value:
            prompt = f"""Write a news article about: {topic}

{f"Editorial guidelines: {rules}" if rules else ""}

{f"Source information: {article_content}" if article_content else ""}

{f"Background context: {referenced_content}" if referenced_content else ""}

Create a news article that:
1. Has a compelling headline
2. Follows the inverted pyramid structure
3. Includes who, what, when, where, why, and how
4. Uses clear, concise language
5. Maintains journalistic objectivity
6. Is formatted appropriately for news publication"""

        elif content_type == ContentType.SOCIAL_POST.value:
            prompt = f"""Create engaging social media content about: {topic}

{f"Content guidelines: {rules}" if rules else ""}

{f"Key points to include: {article_content}" if article_content else ""}

{f"Context from conversations: {referenced_content}" if referenced_content else ""}

Generate social media content that:
1. Is attention-grabbing and shareable
2. Uses an engaging, conversational tone
3. Includes relevant hashtags
4. Has a clear call-to-action
5. Is optimized for social media engagement
6. Fits platform character limits when applicable"""

        else:
            # Default to blog format
            prompt = f"""Create content about: {topic}

{f"Guidelines: {rules}" if rules else ""}

{f"Reference material: {article_content}" if article_content else ""}

{f"Additional context: {referenced_content}" if referenced_content else ""}

Please create engaging, well-structured content that is informative and suitable for publication."""

        return prompt
    
    def _get_system_prompt(self, task: Dict[str, Any]) -> str:
        """Get system prompt based on content type"""
        
        content_type = task.get("content_type", ContentType.BLOG.value)
        
        if content_type == ContentType.BLOG.value:
            return """You are a professional blog writer with expertise in creating engaging, SEO-friendly content. 
            Write in a conversational yet informative tone that connects with readers while providing valuable insights."""
        
        elif content_type == ContentType.ARTICLE.value:
            return """You are an expert content writer specializing in authoritative articles. 
            Write with expertise and credibility, providing comprehensive coverage while maintaining clarity and readability."""
        
        elif content_type == ContentType.NEWS.value:
            return """You are a professional journalist with experience in news writing. 
            Write objectively, factually, and clearly, following journalistic standards and ethics."""
        
        elif content_type == ContentType.SOCIAL_POST.value:
            return """You are a social media content creator who understands engagement and viral content. 
            Write in a way that encourages interaction, sharing, and community building."""
        
        else:
            return """You are a professional content writer. Create high-quality, engaging content that provides value to readers."""
    
    def _load_referenced_chats(self, user_id: str, chat_filenames: List[str]) -> str:
        """Load content from referenced chat files with token-safe concatenation"""
        # Use new helper methods for improved chat loading
        return self.load_chats(user_id, chat_filenames)

    def load_chats(self, user_id: str, chat_refs: List[str]) -> str:
        """Load and process multiple chat files with token-safe concatenation"""

        from app.config import settings

        if not chat_refs:
            return ""

        user_chat_dir = os.path.join(settings.data_dir, "chats", user_id)
        processed_chats = []
        total_tokens = 0
        max_tokens = 4000  # Reserve space for main prompt

        for filename in chat_refs:
            file_path = os.path.join(user_chat_dir, filename)
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Summarize chat if it's too long
                    summary = self.summarise_chat(content, filename)

                    # Estimate tokens (rough approximation: 1 token ≈ 4 characters)
                    estimated_tokens = len(summary) // 4

                    if total_tokens + estimated_tokens > max_tokens:
                        # If adding this chat would exceed limit, truncate or skip
                        remaining_tokens = max_tokens - total_tokens
                        if remaining_tokens > 100:  # Only add if we have meaningful space
                            truncated_summary = summary[:remaining_tokens * 4] + "... [truncated]"
                            processed_chats.append(f"\n\n--- From {filename} ---\n{truncated_summary}")
                        break

                    processed_chats.append(f"\n\n--- From {filename} ---\n{summary}")
                    total_tokens += estimated_tokens

                except Exception as e:
                    error_msg = f"\n\n--- Error reading {filename}: {str(e)} ---"
                    if total_tokens + len(error_msg) // 4 <= max_tokens:
                        processed_chats.append(error_msg)

        return "".join(processed_chats)

    def summarise_chat(self, chat_content: str, filename: str) -> str:
        """Summarize chat content to extract key insights and context"""

        if not chat_content or len(chat_content.strip()) == 0:
            return f"[Empty chat file: {filename}]"

        # If content is short enough, return as-is
        if len(chat_content) <= 1000:
            return chat_content

        # Extract key information from chat
        lines = chat_content.split('\n')

        # Look for key patterns and extract important information
        key_points = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detect topic changes or important statements
            important_keywords = ['user:', 'assistant:', 'topic:', 'question:', 'problem:', 'solution:']
            if any(keyword in line.lower() for keyword in important_keywords):
                if len(line) <= 200:  # Keep short, important lines
                    key_points.append(line)
                else:
                    # Truncate long lines but keep the beginning
                    key_points.append(line[:200] + "...")

            # Extract key insights (lines with certain keywords)
            else:
                insight_keywords = ['important', 'key', 'main', 'summary', 'conclusion', 'result']
                if any(keyword in line.lower() for keyword in insight_keywords):
                    if len(line) <= 150:
                        key_points.append(line)

        # If we didn't extract enough, take first and last parts
        if len(key_points) < 3:
            # Take first 500 chars and last 300 chars
            first_part = chat_content[:500]
            last_part = chat_content[-300:] if len(chat_content) > 800 else ""

            summary = first_part
            if last_part and last_part != first_part[-300:]:
                summary += "\n\n... [middle content omitted] ...\n\n" + last_part

            return summary

        # Combine key points with reasonable length limit
        summary = "\n".join(key_points[:10])  # Limit to 10 key points

        # If still too long, truncate
        if len(summary) > 2000:
            summary = summary[:2000] + "\n... [additional content omitted]"

        return summary

    def analyze_chat_style(self, chat_content: str) -> Dict[str, Any]:
        """Analyze chat content to extract tone and style patterns"""
        if not chat_content:
            return {}

        analysis = {
            'tone_indicators': [],
            'style_patterns': [],
            'formality_level': 'neutral',
            'writing_style': []
        }

        content_lower = chat_content.lower()

        # Analyze tone indicators
        casual_indicators = ['hey', 'hi there', 'cool', 'awesome', 'great!', 'thanks!', 'btw', 'fyi']
        formal_indicators = ['however', 'furthermore', 'therefore', 'consequently', 'nevertheless']
        friendly_indicators = ['please', 'thank you', 'appreciate', 'wonderful', 'excellent']

        casual_count = sum(1 for indicator in casual_indicators if indicator in content_lower)
        formal_count = sum(1 for indicator in formal_indicators if indicator in content_lower)
        friendly_count = sum(1 for indicator in friendly_indicators if indicator in content_lower)

        # Determine formality level
        if formal_count > casual_count:
            analysis['formality_level'] = 'formal'
            analysis['tone_indicators'].append('formal language patterns detected')
        elif casual_count > formal_count:
            analysis['formality_level'] = 'casual'
            analysis['tone_indicators'].append('casual language patterns detected')

        if friendly_count > 2:
            analysis['tone_indicators'].append('friendly and polite tone')

        # Analyze style patterns
        if '!' in chat_content:
            exclamation_count = chat_content.count('!')
            if exclamation_count > 3:
                analysis['style_patterns'].append('enthusiastic tone with exclamations')

        if '?' in chat_content:
            question_count = chat_content.count('?')
            if question_count > 2:
                analysis['style_patterns'].append('inquisitive and engaging style')

        # Check for bullet points or lists in chat
        if '•' in chat_content or '- ' in chat_content or any(line.strip().startswith(('1.', '2.', '3.')) for line in chat_content.split('\n')):
            analysis['style_patterns'].append('structured list format preferred')

        # Check for technical language
        technical_terms = ['api', 'database', 'algorithm', 'implementation', 'configuration', 'optimization']
        if any(term in content_lower for term in technical_terms):
            analysis['writing_style'].append('technical writing style')

        # Check for storytelling elements
        story_indicators = ['once', 'then', 'finally', 'first', 'next', 'example', 'for instance']
        if sum(1 for indicator in story_indicators if indicator in content_lower) > 3:
            analysis['writing_style'].append('narrative and example-driven style')

        return analysis

    def build_chat_style_instructions(self, style_analysis: Dict[str, Any]) -> List[str]:
        """Build style instructions based on chat analysis"""
        instructions = []

        if not style_analysis:
            return instructions

        # Add formality instructions
        formality = style_analysis.get('formality_level', 'neutral')
        if formality == 'formal':
            instructions.append("Maintain a formal, professional tone similar to the referenced conversations")
        elif formality == 'casual':
            instructions.append("Use a casual, approachable tone that matches the conversational style in the referenced chats")

        # Add tone-specific instructions
        tone_indicators = style_analysis.get('tone_indicators', [])
        if 'friendly and polite tone' in tone_indicators:
            instructions.append("Maintain a friendly and polite tone throughout")
        if 'enthusiastic tone with exclamations' in style_analysis.get('style_patterns', []):
            instructions.append("Use an enthusiastic tone but avoid excessive exclamation marks")

        # Add style pattern instructions
        style_patterns = style_analysis.get('style_patterns', [])
        if 'inquisitive and engaging style' in style_patterns:
            instructions.append("Include engaging questions to maintain reader interest")
        if 'structured list format preferred' in style_patterns:
            instructions.append("Use structured formatting with clear organization")

        # Add writing style instructions
        writing_style = style_analysis.get('writing_style', [])
        if 'technical writing style' in writing_style:
            instructions.append("Incorporate technical accuracy and precise terminology where appropriate")
        if 'narrative and example-driven style' in writing_style:
            instructions.append("Include concrete examples and use narrative elements to illustrate points")

        return instructions

    def _extract_keywords_from_content(self, content: str, max_keywords: int = 10) -> List[str]:
        """Extract meaningful keywords from generated content for image search"""
        if not content:
            return []

        # Remove markdown formatting and HTML tags
        clean_content = re.sub(r'#+ ', '', content)  # Remove markdown headers
        clean_content = re.sub(r'<[^>]+>', '', clean_content)  # Remove HTML tags
        clean_content = re.sub(r'\*\*([^*]+)\*\*', r'\1', clean_content)  # Remove bold markdown
        clean_content = re.sub(r'\*([^*]+)\*', r'\1', clean_content)  # Remove italic markdown
        clean_content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', clean_content)  # Remove markdown links

        # Split into words and filter
        words = re.findall(r'\b[a-zA-Z]{3,}\b', clean_content.lower())

        # Common stop words to exclude
        stop_words = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'who', 'boy', 'did', 'she', 'use', 'way', 'will', 'with', 'have', 'this', 'that', 'they', 'from', 'been', 'said', 'each', 'which', 'their', 'time', 'would', 'there', 'what', 'about', 'when', 'where', 'more', 'some', 'very', 'into', 'just', 'like', 'only', 'other', 'such', 'than', 'then', 'them', 'well', 'were'
        }

        # Filter out stop words and count frequency
        word_freq = {}
        for word in words:
            if word not in stop_words and len(word) > 3:
                word_freq[word] = word_freq.get(word, 0) + 1

        # Sort by frequency and return top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, _ in sorted_words[:max_keywords]]

    async def _get_images(self, task: Dict[str, Any], user_settings: Dict[str, Any], generated_content: str = None) -> Dict[str, Any]:
        """Get relevant images for the content using keywords from generated content"""

        try:
            # Extract keywords from generated content if available, otherwise use topic
            if generated_content:
                keywords = self._extract_keywords_from_content(generated_content)
                # Combine topic with top keywords for better search
                search_terms = [task["topic"]] + keywords[:3]
                search_query = " ".join(search_terms)
            else:
                search_query = task["topic"]

            # Search for images
            result = await image_service.search_images(
                query=search_query,
                per_page=8,  # Get more to have better selection
                orientation="landscape",
                size="large",
                user_settings=user_settings
            )

            if result["success"] and result["photos"]:
                # Format images with attribution
                images = []
                for photo in result["photos"][:5]:  # Take top 5 images as requested
                    images.append({
                        "id": photo["id"],
                        "url": photo["src"]["large"],
                        "thumbnail": photo["src"]["medium"],
                        "photographer": photo["photographer"],
                        "photographer_url": photo["photographer_url"],
                        "attribution": image_service.get_attribution_text(photo),
                        "alt": photo.get("alt", search_query),
                        "search_keywords": keywords if generated_content else [task["topic"]]
                    })

                return {"success": True, "images": images, "search_query": search_query}
            else:
                return {"success": False, "images": [], "error": result.get("error", "No images found")}

        except Exception as e:
            return {"success": False, "images": [], "error": str(e)}
    
    async def _post_to_wordpress(self, task: Dict[str, Any], content: Dict[str, Any], user_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Post generated content to WordPress as draft"""

        try:
            # Get WordPress credentials using the proper method that handles both new and legacy systems
            from app.api.wp import get_decrypted_wp_auth
            from app.services.auth import auth_service

            # Get user email for credential lookup
            user_data = auth_service.get_user(task["user_id"])
            user_email = user_data.get("email") if user_data else task["user_id"]

            # Try to get credentials from the new encrypted system first
            wp_credentials = get_decrypted_wp_auth(user_email)

            if wp_credentials:
                username = wp_credentials["username"]
                password = wp_credentials["password"]
                logger.info(f"Using encrypted WordPress credentials for user {user_email}")
            else:
                # Fallback to legacy user_settings method
                username = user_settings.get("wordpress_app_username")
                password = user_settings.get("wordpress_app_password")
                logger.info(f"Using legacy WordPress credentials for user {user_email}")

            if not username or not password:
                return {
                    "success": False,
                    "error": "WordPress credentials not configured"
                }

            # Prepare content for WordPress
            title = task["topic"]
            # Clean content by removing <think></think> tags before posting to WordPress
            wordpress_content = self._clean_think_tags(content["content"])

            # Add images to content if available
            if content.get("images"):
                for image in content["images"]:
                    if image.get("url"):
                        alt_text = image.get("description", "Generated image")
                        wordpress_content += f'\n\n<img src="{image["url"]}" alt="{alt_text}" />'

            # Create excerpt from first paragraph
            excerpt = None
            if wordpress_content:
                # Extract first paragraph as excerpt
                paragraphs = wordpress_content.split('\n\n')
                if paragraphs:
                    excerpt = paragraphs[0][:150] + "..." if len(paragraphs[0]) > 150 else paragraphs[0]

            # Post to WordPress
            result = await wordpress_service.create_draft_post(
                wordpress_url=task["wordpress_url"],
                username=username,
                password=password,
                title=title,
                content=wordpress_content,
                excerpt=excerpt
            )

            return result

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _clean_think_tags(self, text: str) -> str:
        """
        Remove <think></think> tags and their content from generated text.
        This ensures clean output for downloads and WordPress posting.
        """
        if not text:
            return text

        # Remove <think></think> tags and everything between them
        # Use re.DOTALL flag to match newlines within think tags
        cleaned_text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL | re.IGNORECASE)

        # Clean up any extra whitespace left behind
        cleaned_text = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned_text)  # Remove triple+ line breaks
        cleaned_text = cleaned_text.strip()

        return cleaned_text

    def _qa_filter(self, text: str) -> str:
        """
        Apply quality assurance filtering to remove unwanted elements
        that may have slipped through the AI generation process.
        """
        if not text:
            return text

        # First remove think tags
        filtered_text = self._clean_think_tags(text)

        # Remove bullet points and list markers
        # Remove various bullet point styles
        filtered_text = re.sub(r'^[\s]*[•·▪▫‣⁃]\s*', '', filtered_text, flags=re.MULTILINE)
        filtered_text = re.sub(r'^[\s]*[-*+]\s*', '', filtered_text, flags=re.MULTILINE)
        filtered_text = re.sub(r'^[\s]*\d+\.\s*', '', filtered_text, flags=re.MULTILINE)
        filtered_text = re.sub(r'^[\s]*[a-zA-Z]\.\s*', '', filtered_text, flags=re.MULTILINE)
        filtered_text = re.sub(r'^[\s]*[ivxlcdm]+\.\s*', '', filtered_text, flags=re.MULTILINE | re.IGNORECASE)

        # Remove emojis and emoticons
        # Unicode emoji ranges
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U00002702-\U000027B0"  # dingbats
            "\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE
        )
        filtered_text = emoji_pattern.sub('', filtered_text)

        # Remove common emoticons
        emoticon_patterns = [
            r':\)', r':\(', r':D', r':P', r':p', r';\)', r':\|', r':/', r':\\',
            r':-\)', r':-\(', r':-D', r':-P', r':-p', r';\-\)', r':-\|', r':-/', r':-\\',
            r'=\)', r'=\(', r'=D', r'=P', r'=p', r';\)', r'=\|', r'=/', r'=\\',
            r'<3', r'</3', r'<\\3', r'♥', r'♡'
        ]
        for pattern in emoticon_patterns:
            filtered_text = re.sub(pattern, '', filtered_text)

        # Remove em-dashes and replace with regular dashes or spaces
        filtered_text = re.sub(r'—', ' - ', filtered_text)
        filtered_text = re.sub(r'–', ' - ', filtered_text)

        # Convert US spellings to UK spellings (basic implementation)
        us_to_uk_spellings = {
            r'\bcolor\b': 'colour',
            r'\bcolors\b': 'colours',
            r'\bcolored\b': 'coloured',
            r'\bcoloring\b': 'colouring',
            r'\bfavor\b': 'favour',
            r'\bfavors\b': 'favours',
            r'\bfavored\b': 'favoured',
            r'\bfavoring\b': 'favouring',
            r'\bhonor\b': 'honour',
            r'\bhonors\b': 'honours',
            r'\bhonored\b': 'honoured',
            r'\bhonoring\b': 'honouring',
            r'\blabor\b': 'labour',
            r'\blabors\b': 'labours',
            r'\blabored\b': 'laboured',
            r'\blaboring\b': 'labouring',
            r'\bneighbor\b': 'neighbour',
            r'\bneighbors\b': 'neighbours',
            r'\bcenter\b': 'centre',
            r'\bcenters\b': 'centres',
            r'\bcentered\b': 'centred',
            r'\bcentering\b': 'centring',
            r'\btheater\b': 'theatre',
            r'\btheaters\b': 'theatres',
            r'\borganize\b': 'organise',
            r'\borganizes\b': 'organises',
            r'\borganized\b': 'organised',
            r'\borganizing\b': 'organising',
            r'\borganization\b': 'organisation',
            r'\borganizations\b': 'organisations',
            r'\brealize\b': 'realise',
            r'\brealizes\b': 'realises',
            r'\brealized\b': 'realised',
            r'\brealizing\b': 'realising',
            r'\brealization\b': 'realisation',
            r'\brealizations\b': 'realisations',
            r'\brecognize\b': 'recognise',
            r'\brecognizes\b': 'recognises',
            r'\brecognized\b': 'recognised',
            r'\brecognizing\b': 'recognising',
            r'\banalyze\b': 'analyse',
            r'\banalyzes\b': 'analyses',
            r'\banalyzed\b': 'analysed',
            r'\banalyzing\b': 'analysing',
            r'\bdefense\b': 'defence',
            r'\bdefenses\b': 'defences',
            r'\blicense\b': 'licence',
            r'\blicenses\b': 'licences',
        }

        # Apply UK spelling corrections
        for us_pattern, uk_replacement in us_to_uk_spellings.items():
            filtered_text = re.sub(us_pattern, uk_replacement, filtered_text, flags=re.IGNORECASE)

        # Clean up extra whitespace
        filtered_text = re.sub(r'\n\s*\n\s*\n', '\n\n', filtered_text)  # Remove triple+ line breaks
        filtered_text = re.sub(r'[ \t]+', ' ', filtered_text)  # Remove extra spaces/tabs
        filtered_text = re.sub(r'^\s+', '', filtered_text, flags=re.MULTILINE)  # Remove leading whitespace
        filtered_text = filtered_text.strip()

        return filtered_text


# Global content generation engine instance
content_engine = ContentGenerationEngine()
