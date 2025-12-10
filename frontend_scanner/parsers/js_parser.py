"""JavaScript/TypeScript parser utilities."""
from typing import List, Dict, Any
import re


class JSParser:
    """Advanced JavaScript/TypeScript parser utilities."""
    
    @staticmethod
    def extract_functions(code: str) -> List[Dict[str, Any]]:
        """Extract function declarations using regex."""
        functions = []
        
        # Match function declarations
        pattern = r'function\s+(\w+)\s*\([^)]*\)\s*\{'
        matches = re.finditer(pattern, code)
        
        for match in matches:
            functions.append({
                "name": match.group(1),
                "start_line": code[:match.start()].count('\n') + 1,
                "type": "function"
            })
        
        # Match arrow functions
        pattern = r'const\s+(\w+)\s*=\s*\([^)]*\)\s*=>'
        matches = re.finditer(pattern, code)
        
        for match in matches:
            functions.append({
                "name": match.group(1),
                "start_line": code[:match.start()].count('\n') + 1,
                "type": "arrow_function"
            })
        
        return functions
    
    @staticmethod
    def extract_classes(code: str) -> List[Dict[str, Any]]:
        """Extract class declarations."""
        classes = []
        
        pattern = r'class\s+(\w+)(?:\s+extends\s+(\w+))?\s*\{'
        matches = re.finditer(pattern, code)
        
        for match in matches:
            classes.append({
                "name": match.group(1),
                "extends": match.group(2),
                "start_line": code[:match.start()].count('\n') + 1
            })
        
        return classes
    
    @staticmethod
    def extract_imports(code: str) -> List[Dict[str, Any]]:
        """Extract import statements."""
        imports = []
        
        pattern = r'import\s+.*?\s+from\s+["\']([^"\']+)["\']'
        matches = re.finditer(pattern, code)
        
        for match in matches:
            imports.append({
                "source": match.group(1),
                "line": code[:match.start()].count('\n') + 1
            })
        
        return imports
