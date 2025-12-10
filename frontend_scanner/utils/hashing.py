"""File hashing utilities."""
import hashlib
from pathlib import Path


def compute_file_hash(file_path: Path, algorithm: str = "sha256") -> str:
    """Compute hash of file contents."""
    hash_func = getattr(hashlib, algorithm)()
    
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except Exception as e:
        print(f"Error hashing {file_path}: {e}")
        return ""


def compute_content_hash(content: str, algorithm: str = "sha256") -> str:
    """Compute hash of string content."""
    hash_func = getattr(hashlib, algorithm)()
    hash_func.update(content.encode('utf-8'))
    return hash_func.hexdigest()
