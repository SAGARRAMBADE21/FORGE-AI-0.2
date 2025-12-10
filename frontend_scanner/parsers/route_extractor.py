"""Route extraction for different frameworks."""
from pathlib import Path
from typing import List
import re


class RouteExtractor:
    """Extract routes from framework-specific structures."""
    
    @staticmethod
    def extract_nextjs_routes(pages_dir: Path) -> List[str]:
        """Extract Next.js routes from pages/ or app/ directory."""
        routes = []
        
        if not pages_dir.exists():
            return routes
        
        for file_path in pages_dir.rglob("*.{js,jsx,ts,tsx}"):
            try:
                # Convert file path to route
                route = str(file_path.relative_to(pages_dir))
                
                # Remove file extension
                route = route.rsplit('.', 1)[0]
                
                # Convert index to /
                if route.endswith('/index') or route == 'index':
                    route = route.replace('index', '')
                
                # Convert [param] to :param
                route = route.replace('[', ':').replace(']', '')
                
                # Add leading slash
                if not route.startswith('/'):
                    route = '/' + route
                
                if not route:
                    route = '/'
                
                routes.append(route)
            except Exception:
                continue
        
        return routes
    
    @staticmethod
    def extract_react_router_routes(code: str) -> List[str]:
        """Extract routes from React Router configuration."""
        routes = []
        
        # Match <Route path="..." />
        pattern = r'<Route\s+path=["\'](.*?)["\']'
        matches = re.findall(pattern, code)
        routes.extend(matches)
        
        return routes
    
    @staticmethod
    def extract_vue_routes(code: str) -> List[str]:
        """Extract routes from Vue Router configuration."""
        routes = []
        
        # Match path: '...'
        pattern = r'path:\s*["\']([^"\']+)["\']'
        matches = re.findall(pattern, code)
        routes.extend(matches)
        
        return routes
