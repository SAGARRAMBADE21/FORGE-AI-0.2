"""Security and sanitization utilities."""
import re
from typing import List

DEFAULT_SECRET_PATTERNS = [
    r'(?i)(api[_-]?key|secret|password|token)\s*[:=]\s*["\']?[\w\-]+["\']?',
    r'(?i)bearer\s+[\w\-\.]+',
    r'sk-[a-zA-Z0-9]{20,}',  # OpenAI keys
    r'ghp_[a-zA-Z0-9]{36}',  # GitHub tokens
    r'(?i)aws[_-]?secret[_-]?access[_-]?key',
    r'AIza[0-9A-Za-z\-_]{35}',  # Google API keys
]


def redact_secrets(text: str, patterns: Optional[List[str]] = None) -> str:
    """Redact secrets from text."""
    if patterns is None:
        patterns = DEFAULT_SECRET_PATTERNS
    
    redacted = text
    for pattern_str in patterns:
        try:
            pattern = re.compile(pattern_str)
            redacted = pattern.sub('[REDACTED]', redacted)
        except Exception as e:
            print(f"Error applying redaction pattern: {e}")
            continue
    
    return redacted


def is_sensitive_file(file_path: str) -> bool:
    """Check if file might contain sensitive data."""
    sensitive_patterns = [
        '.env',
        'secret',
        'credentials',
        'config.json',
        'auth',
        'private',
        '.pem',
        '.key'
    ]
    return any(pattern in file_path.lower() for pattern in sensitive_patterns)
