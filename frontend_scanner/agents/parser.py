"""Parser Agent - AST extraction using tree-sitter."""
from __future__ import annotations
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, TYPE_CHECKING
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from tree_sitter import Language, Parser

try:
    import tree_sitter_javascript as tsjs  # type: ignore
    import tree_sitter_typescript as tsts  # type: ignore
    from tree_sitter import Language, Parser  # type: ignore
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False
    print("Warning: tree-sitter not available. AST parsing will be limited.")


class ComponentMetadata(BaseModel):
    """Metadata for a React/Vue/Svelte component."""
    name: str
    type: str
    props: List[str] = Field(default_factory=list)
    hooks: List[str] = Field(default_factory=list)
    api_calls: List[Dict[str, Any]] = Field(default_factory=list)
    exports: List[str] = Field(default_factory=list)
    imports: List[Dict[str, Any]] = Field(default_factory=list)
    env_vars: List[str] = Field(default_factory=list)
    start_line: int
    end_line: int


class ParsedFile(BaseModel):
    """Complete parse result for a file."""
    file_path: str
    language: str
    framework: Optional[str] = None
    components: List[ComponentMetadata] = Field(default_factory=list)
    exports: List[str] = Field(default_factory=list)
    imports: List[Dict[str, Any]] = Field(default_factory=list)
    api_calls: List[Dict[str, Any]] = Field(default_factory=list)
    env_vars: List[str] = Field(default_factory=list)
    routes: List[str] = Field(default_factory=list)
    ast_summary: Optional[str] = None
    parse_errors: List[str] = Field(default_factory=list)


class ParserAgent:
    """Agent that parses code files and extracts AST metadata."""
    
    def __init__(self, config):
        self.config = config
        self.parsers_available = TREE_SITTER_AVAILABLE
        
        if self.parsers_available:
            self._setup_parsers()
        else:
            print("Tree-sitter parsers not available. Using fallback parsing.")
    
    def _setup_parsers(self):
        """Initialize tree-sitter parsers."""
        try:
            self.js_language = Language(tsjs.language())
            self.ts_language = Language(tsts.language_typescript())
            self.tsx_language = Language(tsts.language_tsx())
            
            self.js_parser = Parser(self.js_language)
            self.ts_parser = Parser(self.ts_language)
            self.tsx_parser = Parser(self.tsx_language)
        except Exception as e:
            print(f"Error setting up parsers: {e}")
            self.parsers_available = False
    
    def get_parser(self, extension: str) -> Optional[Tuple[Parser, Language]]:
        """Get appropriate parser for file extension."""
        if not self.parsers_available:
            return None
        
        try:
            if extension in ['.ts']:
                return self.ts_parser, self.ts_language
            elif extension in ['.tsx']:
                return self.tsx_parser, self.tsx_language
            else:
                return self.js_parser, self.js_language
        except:
            return None
    
    def parse(self, file_path: str, content: str) -> ParsedFile:
        """Parse a file and extract metadata."""
        path = Path(file_path)
        extension = path.suffix
        
        parsed = ParsedFile(
            file_path=file_path,
            language=self._detect_language(extension),
            framework=self._detect_framework(path, content)
        )
        
        try:
            if self.parsers_available:
                parser_tuple = self.get_parser(extension)
                if parser_tuple:
                    parser, language = parser_tuple
                    tree = parser.parse(bytes(content, "utf8"))
                    root_node = tree.root_node
                    
                    parsed.components = self._extract_components(root_node, content, language)
                    parsed.imports = self._extract_imports(root_node, content, language)
                    parsed.exports = self._extract_exports(root_node, content, language)
                    parsed.api_calls = self._extract_api_calls(content)
                    parsed.env_vars = self._extract_env_vars(content)
            else:
                # Fallback parsing
                parsed.api_calls = self._extract_api_calls(content)
                parsed.env_vars = self._extract_env_vars(content)
                parsed.imports = self._extract_imports_regex(content)
            
            # Extract routes based on framework
            if parsed.framework == "nextjs":
                parsed.routes = self._extract_nextjs_routes(path)
            elif parsed.framework == "react":
                parsed.routes = self._extract_react_router_routes(content)
            
            parsed.ast_summary = self._generate_ast_summary(parsed)
            
        except Exception as e:
            parsed.parse_errors.append(str(e))
        
        return parsed
    
    def _detect_language(self, extension: str) -> str:
        """Detect programming language from extension."""
        mapping = {
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.vue': 'vue',
            '.svelte': 'svelte',
            '.html': 'html',
            '.css': 'css',
        }
        return mapping.get(extension, 'unknown')
    
    def _detect_framework(self, path: Path, content: str) -> Optional[str]:
        """Detect framework from file path and content."""
        path_str = str(path).lower()
        content_lower = content.lower()
        
        if '/pages/' in path_str or '/app/' in path_str or 'next' in content_lower:
            return "nextjs"
        if 'react' in content_lower or 'usestate' in content_lower or 'useeffect' in content_lower:
            return "react"
        if path.suffix == '.vue':
            return "vue"
        if path.suffix == '.svelte':
            return "svelte"
        
        return None
    
    def _extract_components(self, root_node, content: str, language) -> List[ComponentMetadata]:
        """Extract components from AST."""
        components = []
        
        # Use regex-based extraction as it's more reliable
        import re
        
        # Match function components
        patterns = [
            r'function\s+(\w+)\s*\([^)]*\)\s*{',
            r'const\s+(\w+)\s*=\s*\([^)]*\)\s*=>',
            r'export\s+default\s+function\s+(\w+)',
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, content):
                name = match.group(1)
                line_num = content[:match.start()].count('\n') + 1
                components.append(ComponentMetadata(
                    name=name,
                    type="function",
                    start_line=line_num,
                    end_line=line_num,
                    hooks=self._extract_hooks(content)
                ))
                if len(components) >= 20:
                    break
            if len(components) >= 20:
                break
        
        return components[:20]  # Limit to 20 components
    
    def _extract_imports(self, root_node, content: str, language) -> List[Dict[str, Any]]:
        """Extract import statements."""
        # Use regex-based extraction (more reliable than tree-sitter queries)
        return self._extract_imports_regex(content)
    
    def _extract_imports_regex(self, content: str) -> List[Dict[str, Any]]:
        """Fallback import extraction using regex."""
        import re
        imports = []
        
        pattern = r'import\s+.*?\s+from\s+["\'](.+?)["\']'
        matches = re.finditer(pattern, content)
        
        for i, match in enumerate(matches):
            imports.append({
                "source": match.group(1),
                "line": content[:match.start()].count('\n') + 1
            })
            if i >= 50:
                break
        
        return imports
    
    def _extract_exports(self, root_node, content: str, language) -> List[str]:
        """Extract export declarations."""
        import re
        exports = []
        
        patterns = [
            r'export\s+default\s+\w+',
            r'export\s+{[^}]+}',
            r'export\s+const\s+\w+',
            r'export\s+function\s+\w+',
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, content):
                export_text = match.group(0)
                if export_text:
                    exports.append(export_text[:100])
                if len(exports) >= 20:
                    break
            if len(exports) >= 20:
                break
        
        return exports[:20]
    
    def _extract_api_calls(self, content: str) -> List[Dict[str, Any]]:
        """Extract fetch/axios/API calls using regex."""
        import re
        api_calls = []
        
        patterns = [
            r'fetch\s*\(\s*["\']([^"\']+)["\']',
            r'axios\.\w+\s*\(\s*["\']([^"\']+)["\']',
            r'\.get\s*\(\s*["\']([^"\']+)["\']',
            r'\.post\s*\(\s*["\']([^"\']+)["\']',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content)
            for i, match in enumerate(matches):
                api_calls.append({
                    "call": match.group(0)[:200],
                    "url": match.group(1),
                    "line": content[:match.start()].count('\n') + 1
                })
                if len(api_calls) >= 20:
                    break
            if len(api_calls) >= 20:
                break
        
        return api_calls
    
    def _extract_env_vars(self, content: str) -> List[str]:
        """Extract environment variable usage."""
        import re
        env_vars = []
        
        matches = re.findall(r'process\.env\.(\w+)', content)
        env_vars.extend(matches)
        
        matches = re.findall(r'import\.meta\.env\.(\w+)', content)
        env_vars.extend(matches)
        
        return list(set(env_vars))[:20]
    
    def _extract_hooks(self, code: str) -> List[str]:
        """Extract React hooks usage."""
        import re
        hooks = []
        
        hook_pattern = r'\b(use[A-Z]\w+)\s*\('
        matches = re.findall(hook_pattern, code)
        hooks.extend(matches)
        
        return list(set(hooks))[:10]
    
    def _extract_nextjs_routes(self, path: Path) -> List[str]:
        """Extract Next.js routes from file path."""
        routes = []
        path_str = str(path)
        
        if '/pages/' in path_str:
            route = path_str.split('/pages/')[-1]
            route = route.replace('index.js', '').replace('index.tsx', '')
            route = route.replace('.js', '').replace('.tsx', '').replace('.jsx', '').replace('.ts', '')
            route = '/' + route.strip('/')
            routes.append(route)
        
        return routes
    
    def _extract_react_router_routes(self, content: str) -> List[str]:
        """Extract routes from React Router configuration."""
        import re
        routes = []
        
        # Match <Route path="..." />
        pattern = r'<Route\s+path=["\'](.*?)["\']'
        matches = re.findall(pattern, content)
        routes.extend(matches)
        
        # Match routes object/array patterns: path: "..." or "path": "..."
        pattern2 = r'["\']?path["\']?\s*:\s*["\']([^"\']+)["\']'
        matches2 = re.findall(pattern2, content)
        routes.extend(matches2)
        
        return routes
    
    def _get_node_text(self, node, content: str) -> str:
        """Get text content of AST node."""
        try:
            return content[node.start_byte:node.end_byte]
        except:
            return ""
    
    def _generate_ast_summary(self, parsed: ParsedFile) -> str:
        """Generate human-readable AST summary."""
        parts = [f"File: {Path(parsed.file_path).name}"]
        
        if parsed.framework:
            parts.append(f"Framework: {parsed.framework}")
        
        parts.append(f"Components: {len(parsed.components)}")
        parts.append(f"Imports: {len(parsed.imports)}")
        parts.append(f"API Calls: {len(parsed.api_calls)}")
        
        return " | ".join(parts)
