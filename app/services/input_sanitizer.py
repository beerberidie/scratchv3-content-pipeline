"""
Input sanitization service to prevent injection attacks
"""
import re
import html
import logging
from typing import str, Optional

logger = logging.getLogger(__name__)


class InputSanitizer:
    """Service for sanitizing user inputs to prevent injection attacks"""
    
    # Patterns that might indicate prompt injection attempts
    SUSPICIOUS_PATTERNS = [
        r'ignore\s+previous\s+instructions',
        r'forget\s+everything',
        r'system\s*:',
        r'assistant\s*:',
        r'human\s*:',
        r'user\s*:',
        r'<\s*script\s*>',
        r'javascript\s*:',
        r'data\s*:',
        r'vbscript\s*:',
        r'on\w+\s*=',
        r'eval\s*\(',
        r'exec\s*\(',
        r'function\s*\(',
        r'<\s*iframe',
        r'<\s*object',
        r'<\s*embed',
        r'<\s*link',
        r'<\s*meta',
        r'<\s*style',
    ]
    
    # Maximum lengths for different input types
    MAX_LENGTHS = {
        'topic': 500,
        'rules': 2000,
        'article_content': 10000,
        'username': 50,
        'email': 100,
        'password': 128,
        'url': 500,
        'filename': 255,
        'general': 1000
    }
    
    def __init__(self):
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.SUSPICIOUS_PATTERNS]
    
    def sanitize_text(self, text: str, input_type: str = 'general', allow_html: bool = False) -> str:
        """
        Sanitize text input to prevent injection attacks
        
        Args:
            text: The input text to sanitize
            input_type: Type of input for length validation
            allow_html: Whether to allow HTML tags (default: False)
        
        Returns:
            Sanitized text
        """
        if not text:
            return ""
        
        # Convert to string if not already
        text = str(text)
        
        # Check length limits
        max_length = self.MAX_LENGTHS.get(input_type, self.MAX_LENGTHS['general'])
        if len(text) > max_length:
            logger.warning(f"Input too long for type {input_type}: {len(text)} > {max_length}")
            text = text[:max_length]
        
        # HTML escape if HTML not allowed
        if not allow_html:
            text = html.escape(text)
        
        # Remove null bytes and control characters
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def check_for_injection(self, text: str) -> tuple[bool, Optional[str]]:
        """
        Check if text contains potential injection patterns
        
        Args:
            text: Text to check
        
        Returns:
            Tuple of (is_suspicious, reason)
        """
        if not text:
            return False, None
        
        text_lower = text.lower()
        
        # Check for suspicious patterns
        for i, pattern in enumerate(self.compiled_patterns):
            if pattern.search(text_lower):
                reason = f"Suspicious pattern detected: {self.SUSPICIOUS_PATTERNS[i]}"
                logger.warning(f"Potential injection attempt: {reason}")
                return True, reason
        
        # Check for excessive special characters (might indicate obfuscation)
        special_char_ratio = len(re.findall(r'[^\w\s]', text)) / len(text) if text else 0
        if special_char_ratio > 0.3:
            reason = f"High special character ratio: {special_char_ratio:.2f}"
            logger.warning(f"Suspicious input: {reason}")
            return True, reason
        
        # Check for repeated patterns (might indicate injection)
        if len(set(text.split())) < len(text.split()) * 0.3 and len(text.split()) > 10:
            reason = "High repetition detected"
            logger.warning(f"Suspicious input: {reason}")
            return True, reason
        
        return False, None
    
    def sanitize_prompt_input(self, text: str) -> str:
        """
        Specifically sanitize text that will be used in AI prompts
        
        Args:
            text: Text to sanitize for prompt use
        
        Returns:
            Sanitized text safe for AI prompts
        """
        if not text:
            return ""
        
        # Basic sanitization
        text = self.sanitize_text(text, 'general', allow_html=False)
        
        # Check for injection attempts
        is_suspicious, reason = self.check_for_injection(text)
        if is_suspicious:
            logger.warning(f"Blocking suspicious prompt input: {reason}")
            # Return a safe version or raise an exception
            # For now, we'll clean it more aggressively
            text = re.sub(r'[^\w\s\-.,!?]', '', text)
            text = text[:500]  # Limit length further
        
        # Remove potential prompt injection markers
        text = re.sub(r'\b(system|assistant|human|user)\s*:', '', text, flags=re.IGNORECASE)
        text = re.sub(r'ignore\s+previous', 'previous', text, flags=re.IGNORECASE)
        text = re.sub(r'forget\s+everything', 'everything', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename to prevent directory traversal
        
        Args:
            filename: Original filename
        
        Returns:
            Safe filename
        """
        if not filename:
            return "unnamed_file"
        
        # Remove path separators and dangerous characters
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        filename = re.sub(r'\.\.', '', filename)  # Remove directory traversal
        filename = filename.strip('. ')  # Remove leading/trailing dots and spaces
        
        # Limit length
        if len(filename) > 255:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:250] + ('.' + ext if ext else '')
        
        return filename or "unnamed_file"
    
    def sanitize_url(self, url: str) -> str:
        """
        Sanitize URL input
        
        Args:
            url: URL to sanitize
        
        Returns:
            Sanitized URL
        """
        if not url:
            return ""
        
        # Basic sanitization
        url = url.strip()
        
        # Check for dangerous protocols
        dangerous_protocols = ['javascript:', 'data:', 'vbscript:', 'file:']
        for protocol in dangerous_protocols:
            if url.lower().startswith(protocol):
                logger.warning(f"Dangerous protocol detected in URL: {protocol}")
                return ""
        
        # Ensure it starts with http:// or https://
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        return url


# Global sanitizer instance
input_sanitizer = InputSanitizer()
