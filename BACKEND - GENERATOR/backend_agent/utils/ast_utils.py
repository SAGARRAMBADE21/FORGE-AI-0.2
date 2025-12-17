"""
AST Utilities
Parse and analyze code AST.
"""

import ast
from typing import List, Dict, Any


def parse_ast(code: str, language: str = "python") -> Any:
    """Parse code into AST."""
    
    if language == "python":
        return parse_python_ast(code)
    elif language == "javascript":
        return parse_javascript_ast(code)
    else:
        return None


def parse_python_ast(code: str) -> ast.AST:
    """Parse Python code into AST."""
    try:
        return ast.parse(code)
    except SyntaxError as e:
        print(f"Python syntax error: {e}")
        return None


def parse_javascript_ast(code: str) -> Dict[str, Any]:
    """Parse JavaScript code (simplified)."""
    # Would use a JS parser like esprima
    # For now, return placeholder
    return {"type": "Program", "body": []}


def extract_imports(code: str, language: str = "python") -> List[str]:
    """Extract import statements from code."""
    
    if language == "python":
        return extract_python_imports(code)
    elif language == "javascript":
        return extract_javascript_imports(code)
    else:
        return []


def extract_python_imports(code: str) -> List[str]:
    """Extract Python imports."""
    imports = []
    
    try:
        tree = ast.parse(code)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
    except SyntaxError:
        pass
    
    return imports


def extract_javascript_imports(code: str) -> List[str]:
    """Extract JavaScript imports (regex-based)."""
    import re
    
    imports = []
    
    # Match: import ... from '...'
    pattern = r"import\s+.*\s+from\s+['\"]([^'\"]+)['\"]"
    matches = re.findall(pattern, code)
    imports.extend(matches)
    
    # Match: require('...')
    pattern = r"require\(['\"]([^'\"]+)['\"]\)"
    matches = re.findall(pattern, code)
    imports.extend(matches)
    
    return imports


def extract_functions(code: str, language: str = "python") -> List[str]:
    """Extract function names from code."""
    
    if language == "python":
        try:
            tree = ast.parse(code)
            functions = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
            
            return functions
        except SyntaxError:
            return []
    
    return []


def extract_classes(code: str, language: str = "python") -> List[str]:
    """Extract class names from code."""
    
    if language == "python":
        try:
            tree = ast.parse(code)
            classes = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append(node.name)
            
            return classes
        except SyntaxError:
            return []
    
    return []
