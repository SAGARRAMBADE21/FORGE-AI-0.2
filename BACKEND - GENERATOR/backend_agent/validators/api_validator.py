"""
API Validator
Validates API endpoint definitions.
"""

from typing import List, Dict, Any


class APIValidator:
    """Validates API endpoints."""
    
    def __init__(self):
        self.warnings = []
    
    def validate_endpoints(self, endpoints: List[Dict[str, Any]]) -> bool:
        """Validate API endpoints."""
        
        self.warnings = []
        
        # Check for duplicate endpoints
        seen = set()
        for endpoint in endpoints:
            key = f"{endpoint['method']} {endpoint['path']}"
            if key in seen:
                self.warnings.append(f"Duplicate endpoint: {key}")
            seen.add(key)
        
        # Check for missing auth on sensitive endpoints
        for endpoint in endpoints:
            path = endpoint['path'].lower()
            if any(word in path for word in ['delete', 'update', 'create']):
                if not endpoint.get('requires_auth'):
                    self.warnings.append(
                        f"Warning: {endpoint['method']} {endpoint['path']} may need authentication"
                    )
        
        return len(self.warnings) == 0
