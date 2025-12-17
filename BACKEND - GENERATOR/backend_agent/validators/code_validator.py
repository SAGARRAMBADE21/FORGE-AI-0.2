"""
Code Validator
Validates generated code for syntax errors.
"""

import ast
from typing import Dict, List, Tuple


class CodeValidator:
    """Validates generated code."""
    
    def __init__(self):
        self.errors = []
    
    def validate_all(self, files: Dict[str, str]) -> Tuple[bool, List[str]]:
        """Validate all generated files."""
        
        self.errors = []
        
        for filepath, content in files.items():
            self.validate_file(filepath, content)
        
        return len(self.errors) == 0, self.errors
    
    def validate_file(self, filepath: str, content: str) -> bool:
        """Validate a single file."""
        
        if filepath.endswith('.py'):
            return self.validate_python(filepath, content)
        elif filepath.endswith(('.js', '.ts')):
            return self.validate_javascript(filepath, content)
        elif filepath.endswith('.json'):
            return self.validate_json(filepath, content)
        else:
            return True
    
    def validate_python(self, filepath: str, content: str) -> bool:
        """Validate Python syntax."""
        
        try:
            ast.parse(content)
            return True
        except SyntaxError as e:
            self.errors.append(f"{filepath}: Python syntax error at line {e.lineno}: {e.msg}")
            return False
    
    def validate_javascript(self, filepath: str, content: str) -> bool:
        """Validate JavaScript/TypeScript syntax."""
        
        # Would use a JS parser
        # For now, just check for basic issues
        
        if 'function(' in content and content.count('(') != content.count(')'):
            self.errors.append(f"{filepath}: Mismatched parentheses")
            return False
        
        if content.count('{') != content.count('}'):
            self.errors.append(f"{filepath}: Mismatched braces")
            return False
        
        return True
    
    def validate_json(self, filepath: str, content: str) -> bool:
        """Validate JSON syntax."""
        
        import json
        
        try:
            json.loads(content)
            return True
        except json.JSONDecodeError as e:
            self.errors.append(f"{filepath}: JSON error: {e.msg}")
            return False
