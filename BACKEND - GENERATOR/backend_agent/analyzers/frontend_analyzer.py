"""
Frontend Analyzer Agent
Analyzes frontend scanner output to extract backend requirements.
"""

from typing import Dict, Any, List
import re


class FrontendAnalyzerAgent:
    """Analyzes frontend manifest to extract backend requirements."""
    
    def __init__(self):
        self.endpoints = []
        self.data_models = []
    
    def analyze(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze frontend manifest and extract:
        - Required API endpoints
        - Data models from API calls
        - Authentication requirements
        """
        
        # Extract endpoints from API calls
        self.endpoints = self._extract_endpoints(manifest.get("api_calls", []))
        
        # Extract data models from API calls and components
        self.data_models = self._extract_data_models(manifest)
        
        # Detect auth requirements
        auth_required = self._detect_auth_requirements(manifest)
        
        return {
            "endpoints": self.endpoints,
            "data_models": self.data_models,
            "auth_required": auth_required,
            "frontend_framework": manifest.get("framework", "react"),
            "routes": manifest.get("routes", [])
        }
    
    def _extract_endpoints(self, api_calls: List[str]) -> List[Dict[str, Any]]:
        """
        Parse API calls to extract endpoints.
        Examples:
        - "fetch('/api/users')" -> GET /api/users
        - "axios.post('/api/posts', data)" -> POST /api/posts
        - "api.get('/users/:id')" -> GET /users/:id
        """
        endpoints = []
        
        # Patterns to match API calls
        patterns = [
            r"(get|post|put|delete|patch)\s*\(\s*['\"]([^'\"]+)['\"]",  # axios.get('/path')
            r"fetch\s*\(\s*['\"]([^'\"]+)['\"].*method:\s*['\"](\w+)['\"]",  # fetch with method
            r"fetch\s*\(\s*['\"]([^'\"]+)['\"]",  # fetch (default GET)
        ]
        
        for call in api_calls:
            for pattern in patterns:
                match = re.search(pattern, call, re.IGNORECASE)
                if match:
                    if len(match.groups()) == 2:
                        if "fetch" in pattern and "method" in pattern:
                            path, method = match.groups()
                        else:
                            method, path = match.groups()
                    else:
                        path = match.group(1)
                        method = "GET"
                    
                    endpoint = {
                        "method": method.upper(),
                        "path": path,
                        "resource": self._extract_resource(path),
                        "requires_auth": self._check_auth_required(path),
                        "source": call
                    }
                    
                    # Avoid duplicates
                    if not any(e["method"] == endpoint["method"] and e["path"] == endpoint["path"] 
                              for e in endpoints):
                        endpoints.append(endpoint)
                    break
        
        return endpoints
    
    def _extract_resource(self, path: str) -> str:
        """Extract resource name from path. E.g., /api/users -> users"""
        parts = [p for p in path.split('/') if p and p != 'api']
        if parts:
            # Remove path parameters
            resource = re.sub(r':\w+', '', parts[0])
            return resource
        return "unknown"
    
    def _check_auth_required(self, path: str) -> bool:
        """Check if endpoint likely requires authentication."""
        public_paths = ['/login', '/register', '/public', '/health', '/docs']
        return not any(pub in path.lower() for pub in public_paths)
    
    def _extract_data_models(self, manifest: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract data models from API endpoints.
        Infer entities like User, Post, Comment from paths.
        """
        models = {}
        
        # Extract from API calls
        for call in manifest.get("api_calls", []):
            # Look for resource names in paths
            matches = re.findall(r'/api/(\w+)', call)
            for resource in matches:
                # Singularize (simple approach)
                singular = self._singularize(resource)
                model_name = singular.capitalize()
                
                if model_name not in models:
                    models[model_name] = {
                        "name": model_name,
                        "fields": self._infer_fields(model_name, call),
                        "relationships": []
                    }
        
        # Extract from components (if available)
        for component in manifest.get("components", []):
            if not isinstance(component, dict):
                continue
            comp_name = component.get("name", "")
            # If component has Form/List/Detail, likely a model
            if any(suffix in comp_name for suffix in ["Form", "List", "Table", "Detail"]):
                model_name = re.sub(r'(Form|List|Table|Detail)', '', comp_name)
                if model_name and model_name not in models:
                    models[model_name] = {
                        "name": model_name,
                        "fields": self._infer_fields_from_component(component),
                        "relationships": []
                    }
        
        # Add common fields to all models
        for model in models.values():
            if not any(f["name"] == "id" for f in model["fields"]):
                model["fields"].insert(0, {"name": "id", "type": "integer", "primary_key": True})
            if not any(f["name"] in ["created_at", "updated_at"] for f in model["fields"]):
                model["fields"].extend([
                    {"name": "created_at", "type": "datetime"},
                    {"name": "updated_at", "type": "datetime"}
                ])
        
        return list(models.values())
    
    def _singularize(self, word: str) -> str:
        """Simple singularization (just remove 's' for now)."""
        if word.endswith('ies'):
            return word[:-3] + 'y'
        elif word.endswith('ses'):
            return word[:-2]
        elif word.endswith('s'):
            return word[:-1]
        return word
    
    def _infer_fields(self, model_name: str, api_call: str) -> List[Dict[str, str]]:
        """Infer likely fields for a model."""
        common_fields = {
            "User": [
                {"name": "username", "type": "string"},
                {"name": "email", "type": "string"},
                {"name": "password_hash", "type": "string"},
            ],
            "Post": [
                {"name": "title", "type": "string"},
                {"name": "content", "type": "text"},
                {"name": "author_id", "type": "integer"},
            ],
            "Comment": [
                {"name": "content", "type": "text"},
                {"name": "author_id", "type": "integer"},
                {"name": "post_id", "type": "integer"},
            ],
            "Product": [
                {"name": "name", "type": "string"},
                {"name": "description", "type": "text"},
                {"name": "price", "type": "decimal"},
            ],
        }
        
        return common_fields.get(model_name, [
            {"name": "name", "type": "string"},
            {"name": "description", "type": "text"},
        ])
    
    def _infer_fields_from_component(self, component: Dict[str, Any]) -> List[Dict[str, str]]:
        """Infer fields from component metadata."""
        # This would parse component props/state
        # For now, return empty as we'd need component source code
        return []
    
    def _detect_auth_requirements(self, manifest: Dict[str, Any]) -> bool:
        """Detect if authentication is required."""
        auth_indicators = [
            'login', 'register', 'logout', 'token', 'auth',
            'user', 'profile', 'account'
        ]
        
        # Check API calls
        api_calls_text = ' '.join(manifest.get("api_calls", [])).lower()
        if any(indicator in api_calls_text for indicator in auth_indicators):
            return True
        
        # Check routes
        routes_text = ' '.join(manifest.get("routes", [])).lower()
        if any(indicator in routes_text for indicator in auth_indicators):
            return True
        
        return False
