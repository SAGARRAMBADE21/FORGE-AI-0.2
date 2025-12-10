"""Chunking utility functions."""
from typing import Iterator

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False


def token_based_chunking(text: str, chunk_size: int = 1000,
                        overlap: int = 200) -> Iterator[str]:
    """Split text into chunks based on token count."""
    if TIKTOKEN_AVAILABLE:
        encoding = tiktoken.get_encoding("cl100k_base")
        tokens = encoding.encode(text)
        
        for i in range(0, len(tokens), chunk_size - overlap):
            chunk_tokens = tokens[i:i + chunk_size]
            chunk_text = encoding.decode(chunk_tokens)
            yield chunk_text
    else:
        # Fallback: character-based chunking
        for i in range(0, len(text), chunk_size - overlap):
            yield text[i:i + chunk_size]


def count_tokens(text: str) -> int:
    """Count tokens in text."""
    if TIKTOKEN_AVAILABLE:
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    else:
        # Approximate: 1 token ≈ 4 characters
        return len(text) // 4
