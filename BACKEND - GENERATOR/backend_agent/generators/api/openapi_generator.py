"""
OpenAPI Generator Agent
Generates OpenAPI/Swagger documentation.
"""

from typing import Dict, Any, List
import json


class OpenAPIGeneratorAgent:
    """Generates OpenAPI specification."""
    
    def __init__(self, framework: str):
        self.framework = framework
    
    def generate(self, endpoints: List[Dict[str, Any]], 
                 schemas: Dict[str, str],
                 project_info: Dict[str, str]) -> str:
        """Generate OpenAPI spec."""
        
        openapi_spec = {
            "openapi": "3.0.0",
            "info": {
                "title": project_info.get("name", "Generated API"),
                "version": project_info.get("version", "1.0.0"),
                "description": project_info.get("description", "Auto-generated backend API")
            },
            "servers": [
                {"url": "http://localhost:3000", "description": "Development server"},
                {"url": "http://localhost:8000", "description": "Development server (Python)"}
            ],
            "paths": {},
            "components": {
                "schemas": {},
                "securitySchemes": {
                    "bearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    }
                }
            }
        }
        
        # Add paths from endpoints
        for endpoint in endpoints:
            path = endpoint["path"]
            method = endpoint["method"].lower()
            
            if path not in openapi_spec["paths"]:
                openapi_spec["paths"][path] = {}
            
            openapi_spec["paths"][path][method] = {
                "summary": f"{method.upper()} {path}",
                "tags": [endpoint["resource"]],
                "responses": {
                    "200": {"description": "Successful response"},
                    "400": {"description": "Bad request"},
                    "401": {"description": "Unauthorized"},
                    "404": {"description": "Not found"}
                }
            }
            
            if endpoint.get("requires_auth"):
                openapi_spec["paths"][path][method]["security"] = [{"bearerAuth": []}]
        
        return json.dumps(openapi_spec, indent=2)
