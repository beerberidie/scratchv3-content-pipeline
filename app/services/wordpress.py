"""
WordPress API service for posting content to WordPress sites as drafts
"""
import httpx
import base64
import re
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin


class WordPressService:
    """Service for interacting with WordPress REST API"""
    
    def __init__(self):
        self.timeout = 30.0

    def _extract_title_from_content(self, content: str) -> Optional[str]:
        """Extract title from content (look for H1 or first line)"""
        if not content:
            return None

        # Look for markdown H1
        h1_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if h1_match:
            return h1_match.group(1).strip()

        # Look for HTML H1
        h1_match = re.search(r'<h1[^>]*>([^<]+)</h1>', content, re.IGNORECASE)
        if h1_match:
            return h1_match.group(1).strip()

        # Use first non-empty line as fallback
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('<'):
                # Take first 60 characters as title
                return line[:60] + "..." if len(line) > 60 else line

        return None

    def _create_slug(self, title: str) -> str:
        """Create URL-friendly slug from title"""
        if not title:
            return "untitled-post"

        # Convert to lowercase and replace spaces with hyphens
        slug = title.lower()
        # Remove special characters except hyphens and alphanumeric
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        # Replace spaces with hyphens
        slug = re.sub(r'\s+', '-', slug)
        # Remove multiple consecutive hyphens
        slug = re.sub(r'-+', '-', slug)
        # Remove leading/trailing hyphens
        slug = slug.strip('-')

        # Limit length
        if len(slug) > 50:
            slug = slug[:50].rstrip('-')

        return slug or "untitled-post"

    def _create_excerpt(self, content: str) -> str:
        """Create excerpt from content"""
        if not content:
            return ""

        # Remove markdown/HTML formatting
        text = re.sub(r'#+ ', '', content)  # Remove markdown headers
        text = re.sub(r'<[^>]+>', '', text)  # Remove HTML tags
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Remove bold markdown
        text = re.sub(r'\*([^*]+)\*', r'\1', text)  # Remove italic markdown
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)  # Remove markdown links

        # Get first paragraph or first 150 characters
        paragraphs = text.split('\n\n')
        first_paragraph = paragraphs[0].strip() if paragraphs else text.strip()

        if len(first_paragraph) > 150:
            # Find last complete sentence within 150 chars
            excerpt = first_paragraph[:150]
            last_period = excerpt.rfind('.')
            if last_period > 50:  # Only if we have a reasonable sentence
                excerpt = excerpt[:last_period + 1]
            else:
                excerpt = excerpt + "..."
        else:
            excerpt = first_paragraph

        return excerpt

    def _convert_to_html(self, content: str) -> str:
        """Convert markdown-like content to HTML with comprehensive formatting"""
        if not content:
            return ""

        html_content = content

        # Clean up any malformed markdown first
        # Remove quotes around complete markdown headers (most common issue)
        html_content = re.sub(r'^"(#{1,6}\s+[^"]+)"$', r'\1', html_content, flags=re.MULTILINE)
        html_content = re.sub(r"^'(#{1,6}\s+[^']+)'$", r'\1', html_content, flags=re.MULTILINE)

        # Remove quotes around markdown symbols that might be causing issues
        html_content = re.sub(r"'(#{1,6})'", r'\1', html_content)
        html_content = re.sub(r'"(#{1,6})"', r'\1', html_content)
        html_content = re.sub(r"'(\*{1,2})'", r'\1', html_content)
        html_content = re.sub(r'"(\*{1,2})"', r'\1', html_content)

        # Remove any stray quotes around markdown that might cause issues
        html_content = re.sub(r"'(\*\*[^*]+\*\*)'", r'\1', html_content)
        html_content = re.sub(r'"(\*\*[^*]+\*\*)"', r'\1', html_content)
        html_content = re.sub(r"'(\*[^*]+\*)'", r'\1', html_content)
        html_content = re.sub(r'"(\*[^*]+\*)"', r'\1', html_content)

        # Additional cleanup for common AI-generated markdown issues
        # Remove escaped markdown that shouldn't be escaped
        html_content = re.sub(r'\\(#{1,6})', r'\1', html_content)
        html_content = re.sub(r'\\(\*{1,2})', r'\1', html_content)

        # Fix spacing issues around headers
        html_content = re.sub(r'^(#{1,6})\s*([^\n]+)', r'\1 \2', html_content, flags=re.MULTILINE)

        # Handle quoted headers that are on their own lines
        html_content = re.sub(r'^"(#{1,6}\s+.+)"$', r'\1', html_content, flags=re.MULTILINE)
        html_content = re.sub(r"^'(#{1,6}\s+.+)'$", r'\1', html_content, flags=re.MULTILINE)

        # Handle headers with more flexible patterns (order matters - longest first)
        # More robust header patterns that handle various spacing and line endings
        html_content = re.sub(r'^####\s*(.+?)(?:\s*$)', r'<h4>\1</h4>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^###\s*(.+?)(?:\s*$)', r'<h3>\1</h3>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^##\s*(.+?)(?:\s*$)', r'<h2>\1</h2>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^#\s*(.+?)(?:\s*$)', r'<h1>\1</h1>', html_content, flags=re.MULTILINE)

        # Convert bold and italic with better patterns (order matters)
        # Handle bold first (two asterisks) - more restrictive pattern
        html_content = re.sub(r'\*\*([^*\n]+?)\*\*', r'<strong>\1</strong>', html_content)
        # Handle bold with underscores
        html_content = re.sub(r'__([^_\n]+?)__', r'<strong>\1</strong>', html_content)

        # Handle italic (single asterisk, but not if it's part of bold)
        html_content = re.sub(r'(?<!\*)\*([^*\n]+?)\*(?!\*)', r'<em>\1</em>', html_content)
        # Handle italic with underscores
        html_content = re.sub(r'(?<!_)_([^_\n]+?)_(?!_)', r'<em>\1</em>', html_content)

        # Convert links
        html_content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', html_content)

        # Handle code blocks (triple backticks)
        html_content = re.sub(r'```([^`]+?)```', r'<pre><code>\1</code></pre>', html_content, flags=re.DOTALL)

        # Handle inline code (single backticks)
        html_content = re.sub(r'`([^`]+?)`', r'<code>\1</code>', html_content)

        # Handle blockquotes
        html_content = re.sub(r'^>\s*(.+)$', r'<blockquote>\1</blockquote>', html_content, flags=re.MULTILINE)

        # Handle horizontal rules
        html_content = re.sub(r'^---+$', r'<hr>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^\*\*\*+$', r'<hr>', html_content, flags=re.MULTILINE)

        # Handle lists with better logic
        lines = html_content.split('\n')
        processed_lines = []
        in_ul = False
        in_ol = False

        for line in lines:
            stripped = line.strip()

            # Check for unordered list items
            ul_match = re.match(r'^[-*+]\s+(.+)$', stripped)
            if ul_match:
                if not in_ul:
                    if in_ol:
                        processed_lines.append('</ol>')
                        in_ol = False
                    processed_lines.append('<ul>')
                    in_ul = True
                processed_lines.append(f'<li>{ul_match.group(1)}</li>')
                continue

            # Check for ordered list items
            ol_match = re.match(r'^\d+\.\s+(.+)$', stripped)
            if ol_match:
                if not in_ol:
                    if in_ul:
                        processed_lines.append('</ul>')
                        in_ul = False
                    processed_lines.append('<ol>')
                    in_ol = True
                processed_lines.append(f'<li>{ol_match.group(1)}</li>')
                continue

            # Not a list item, close any open lists
            if in_ul:
                processed_lines.append('</ul>')
                in_ul = False
            if in_ol:
                processed_lines.append('</ol>')
                in_ol = False

            processed_lines.append(line)

        # Close any remaining open lists
        if in_ul:
            processed_lines.append('</ul>')
        if in_ol:
            processed_lines.append('</ol>')

        html_content = '\n'.join(processed_lines)

        # Convert line breaks to paragraphs
        paragraphs = html_content.split('\n\n')
        html_paragraphs = []
        for para in paragraphs:
            para = para.strip()
            if para:
                # Don't wrap if already has HTML block tags
                if not re.search(r'<(?:h[1-6]|ul|ol|li|div|p|pre|blockquote|hr)[^>]*>', para):
                    # Also don't wrap if it's just a single HTML tag
                    if not re.match(r'^<[^>]+>.*</[^>]+>$', para):
                        # Don't wrap if it contains only HTML tags
                        if not re.match(r'^<[^>]+/?>$', para):
                            para = f'<p>{para}</p>'
                html_paragraphs.append(para)

        result = '\n\n'.join(html_paragraphs)

        # Clean up any double spacing or empty paragraphs
        result = re.sub(r'<p>\s*</p>', '', result)
        result = re.sub(r'\n\n\n+', '\n\n', result)

        return result.strip()

    def test_markdown_conversion(self, content: str) -> Dict[str, str]:
        """Test markdown to HTML conversion - useful for debugging"""
        return {
            "original": content,
            "converted": self._convert_to_html(content)
        }

    async def create_draft_post_with_fallback(
        self,
        wordpress_url: str,
        username: str,
        password: str,
        title: str,
        content: str,
        excerpt: Optional[str] = None,
        categories: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        featured_image_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create draft post with multiple format attempts for better compatibility"""

        # Try the standard method first
        result = await self.create_draft_post(
            wordpress_url, username, password, title, content,
            excerpt, categories, tags, featured_image_url
        )

        # If successful, return the result
        if result.get("success"):
            return result

        # If failed, try alternative content format
        try:
            api_url = self._normalize_url(wordpress_url)
            headers = self._get_auth_header(username, password)

            article_h1 = self._extract_title_from_content(content) or title
            slug = self._create_slug(article_h1)

            if not excerpt and content:
                excerpt = self._create_excerpt(content)

            article_html = self._convert_to_html(content)

            # Try simple string format as fallback
            payload = {
                "title": article_h1,
                "status": "draft",
                "content": article_html,
                "excerpt": excerpt[:160] if excerpt else "",
                "slug": slug + "-alt",  # Different slug to avoid conflicts
                "format": "standard"
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{api_url}/posts",
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                )

                if response.status_code == 201:
                    post_data = response.json()
                    post_id = str(post_data.get("id", "")) if post_data.get("id") is not None else ""
                    return {
                        "success": True,
                        "message": "Draft post created successfully (fallback method)",
                        "post": {
                            "id": post_id,
                            "title": post_data.get("title", {}).get("rendered", ""),
                            "status": post_data.get("status"),
                            "link": post_data.get("link"),
                            "edit_link": post_data.get("link", "").replace("?preview=true", f"/wp-admin/post.php?post={post_id}&action=edit")
                        }
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Both primary and fallback methods failed. Last error: {response.text}"
                    }

        except Exception as e:
            return {
                "success": False,
                "error": f"Fallback method also failed: {str(e)}"
            }

    def _get_auth_header(self, username: str, password: str) -> Dict[str, str]:
        """Create basic auth header for WordPress API"""
        credentials = f"{username}:{password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        return {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def _normalize_url(self, wordpress_url: str) -> str:
        """Normalize WordPress URL to ensure it has the correct API endpoint"""
        # Remove trailing slash
        wordpress_url = wordpress_url.rstrip('/')
        
        # Add protocol if missing
        if not wordpress_url.startswith(('http://', 'https://')):
            wordpress_url = f"https://{wordpress_url}"
        
        # Ensure it ends with the REST API path
        if not wordpress_url.endswith('/wp-json/wp/v2'):
            wordpress_url = urljoin(wordpress_url, '/wp-json/wp/v2')
        
        return wordpress_url
    
    async def test_connection(
        self,
        wordpress_url: str,
        username: str,
        password: str
    ) -> Dict[str, Any]:
        """Test connection to WordPress site"""
        
        try:
            api_url = self._normalize_url(wordpress_url)
            headers = self._get_auth_header(username, password)
            
            async with httpx.AsyncClient() as client:
                # Test by getting user info
                response = await client.get(
                    f"{api_url}/users/me",
                    headers=headers,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    user_data = response.json()
                    return {
                        "success": True,
                        "message": "WordPress connection successful",
                        "user": {
                            "id": user_data.get("id"),
                            "name": user_data.get("name"),
                            "username": user_data.get("username"),
                            "email": user_data.get("email")
                        },
                        "site_url": wordpress_url
                    }
                elif response.status_code == 401:
                    return {
                        "success": False,
                        "error": "Authentication failed. Please check your username and password."
                    }
                elif response.status_code == 403:
                    return {
                        "success": False,
                        "error": "Access forbidden. User may not have sufficient permissions."
                    }
                else:
                    return {
                        "success": False,
                        "error": f"WordPress API error: {response.status_code} - {response.text}"
                    }
                    
        except httpx.TimeoutException:
            return {
                "success": False,
                "error": "Connection timeout. Please check the WordPress URL."
            }
        except httpx.ConnectError:
            return {
                "success": False,
                "error": "Cannot connect to WordPress site. Please check the URL."
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"WordPress connection failed: {str(e)}"
            }
    
    async def create_draft_post(
        self,
        wordpress_url: str,
        username: str,
        password: str,
        title: str,
        content: str,
        excerpt: Optional[str] = None,
        categories: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        featured_image_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a draft post in WordPress with comprehensive payload"""

        try:
            api_url = self._normalize_url(wordpress_url)
            headers = self._get_auth_header(username, password)

            # Extract article title from content if title is generic
            article_h1 = self._extract_title_from_content(content) or title

            # Create slug from title
            slug = self._create_slug(article_h1)

            # Ensure excerpt is properly formatted
            if not excerpt and content:
                excerpt = self._create_excerpt(content)

            # Convert content to HTML if it's markdown
            article_html = self._convert_to_html(content)

            # Build comprehensive payload according to WordPress REST API spec
            # WordPress REST API can accept content in different formats
            # Try the object format first, which is more explicit about content type
            payload = {
                "title": article_h1,
                "status": "draft",
                "content": {
                    "raw": article_html
                },
                "excerpt": {
                    "raw": excerpt[:160] if excerpt else ""
                },
                "slug": slug,
                "format": "standard",
                "comment_status": "open",
                "ping_status": "open"
            }

            # Add categories if provided
            if categories:
                # Note: In a real implementation, you'd need to resolve category names to IDs
                # For now, we'll include them as meta or in content
                payload["meta"] = {"categories_note": ", ".join(categories)}

            # Add tags if provided
            if tags:
                # Note: Similar to categories, tags would need to be resolved to IDs
                # For now, we'll include them as meta
                if "meta" not in payload:
                    payload["meta"] = {}
                payload["meta"]["tags_note"] = ", ".join(tags)

            # Add featured image if provided
            if featured_image_url:
                # Note: This would need to be uploaded to WordPress media library first
                # For now, we'll include it in the content
                payload["content"] = f'<img src="{featured_image_url}" alt="Featured image" class="wp-post-image" />\n\n{payload["content"]}'
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{api_url}/posts",
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                )

                # Raise exception on non-201 responses as required by guide
                if response.status_code == 201:
                    post_data = response.json()
                    post_id = str(post_data.get("id", "")) if post_data.get("id") is not None else ""
                    return {
                        "success": True,
                        "message": "Draft post created successfully",
                        "post": {
                            "id": post_id,
                            "title": post_data.get("title", {}).get("rendered", ""),
                            "status": post_data.get("status"),
                            "link": post_data.get("link"),
                            "edit_link": post_data.get("link", "").replace("?preview=true", f"/wp-admin/post.php?post={post_id}&action=edit")
                        }
                    }
                elif response.status_code == 401:
                    error_msg = "Authentication failed. Please check your credentials."
                    raise Exception(error_msg)
                elif response.status_code == 403:
                    error_msg = "Permission denied. User may not have permission to create posts."
                    raise Exception(error_msg)
                else:
                    # Parse error response
                    try:
                        error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {"message": response.text}
                        error_msg = f"WordPress API error {response.status_code}: {error_data.get('message', 'Unknown error')}"
                    except:
                        error_msg = f"WordPress API error {response.status_code}: {response.text}"

                    raise Exception(error_msg)
                    
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create WordPress post: {str(e)}"
            }
    
    async def get_site_info(
        self,
        wordpress_url: str,
        username: str,
        password: str
    ) -> Dict[str, Any]:
        """Get basic site information"""
        
        try:
            api_url = self._normalize_url(wordpress_url)
            headers = self._get_auth_header(username, password)
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    api_url.replace('/wp-json/wp/v2', '/wp-json'),
                    headers=headers,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    site_data = response.json()
                    return {
                        "success": True,
                        "site": {
                            "name": site_data.get("name", ""),
                            "description": site_data.get("description", ""),
                            "url": site_data.get("url", ""),
                            "home": site_data.get("home", "")
                        }
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to get site info: {response.status_code}"
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get site info: {str(e)}"
            }


# Global WordPress service instance
wordpress_service = WordPressService()
