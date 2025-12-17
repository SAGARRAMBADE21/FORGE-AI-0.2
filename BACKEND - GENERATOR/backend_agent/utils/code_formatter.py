"""
Code Formatter
Formats generated code using Black, Prettier, etc.
"""

import subprocess
from pathlib import Path
from typing import Optional


def format_code(code: str, filepath: str, style: str = "black") -> str:
    """Format code based on language and style."""
    
    file_ext = Path(filepath).suffix
    
    if file_ext in [".py"]:
        return format_python(code, style)
    elif file_ext in [".js", ".ts", ".jsx", ".tsx"]:
        return format_javascript(code, style)
    elif file_ext in [".json"]:
        return format_json(code)
    else:
        return code


def format_python(code: str, style: str = "black") -> str:
    """Format Python code with Black."""
    try:
        import black
        
        mode = black.Mode(
            line_length=100,
            string_normalization=True,
        )
        
        formatted = black.format_str(code, mode=mode)
        return formatted
    except ImportError:
        print("Warning: Black not installed, skipping formatting")
        return code
    except Exception as e:
        print(f"Warning: Formatting error: {e}")
        return code


def format_javascript(code: str, style: str = "prettier") -> str:
    """Format JavaScript/TypeScript code with Prettier."""
    try:
        # Try using prettier via subprocess
        result = subprocess.run(
            ["npx", "prettier", "--stdin-filepath", "file.js"],
            input=code.encode(),
            capture_output=True,
            timeout=5
        )
        
        if result.returncode == 0:
            return result.stdout.decode()
        else:
            return code
    except (subprocess.SubprocessError, FileNotFoundError):
        # Prettier not available, return as-is
        return code


def format_json(code: str) -> str:
    """Format JSON."""
    try:
        import json
        parsed = json.loads(code)
        return json.dumps(parsed, indent=2)
    except Exception:
        return code


def format_sql(code: str) -> str:
    """Format SQL code."""
    try:
        import sqlparse
        formatted = sqlparse.format(
            code,
            reindent=True,
            keyword_case='upper'
        )
        return formatted
    except ImportError:
        return code
