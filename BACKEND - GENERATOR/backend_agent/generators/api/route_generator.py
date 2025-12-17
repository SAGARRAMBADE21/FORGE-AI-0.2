"""
Route Generator Agent
Generates API route definitions (Express/FastAPI/NestJS).
"""

from typing import Dict, Any, List
from jinja2 import Template


class RouteGeneratorAgent:
    """Generates API routes."""
    
    def __init__(self, framework: str, llm_config: Dict[str, Any]):
        self.framework = framework
    
    def generate(self, endpoints: List[Dict[str, Any]], 
                 architecture: Dict[str, Any]) -> Dict[str, str]:
        """Generate route files."""
        
        generators = {
            "express": self._generate_express_routes,
            "fastapi": self._generate_fastapi_routes,
            "nestjs": self._generate_nestjs_routes,
            "django": self._generate_django_routes,
        }
        
        generator = generators.get(self.framework)
        if not generator:
            raise ValueError(f"Unsupported framework: {self.framework}")
        
        return generator(endpoints)
    
    def _generate_express_routes(self, endpoints: List[Dict[str, Any]]) -> Dict[str, str]:
        """Generate Express.js routes."""
        
        # Group endpoints by resource
        resources = {}
        for endpoint in endpoints:
            resource = endpoint["resource"]
            if resource not in resources:
                resources[resource] = []
            resources[resource].append(endpoint)
        
        routes = {}
        
        # Template for individual route file
        route_template = Template('''const express = require('express');
const router = express.Router();
const {{ resource }}Controller = require('../controllers/{{ resource }}Controller');
const authMiddleware = require('../middleware/auth');

{% for endpoint in endpoints %}
// {{ endpoint.method }} {{ endpoint.path }}
router.{{ endpoint.method.lower() }}('{{ endpoint.route_path }}',
  {% if endpoint.requires_auth %}authMiddleware,{% endif %}
  {{ resource }}Controller.{{ endpoint.handler_name }}
);

{% endfor %}
module.exports = router;
''')
        
        # Generate route file for each resource
        for resource, resource_endpoints in resources.items():
            processed_endpoints = []
            
            for ep in resource_endpoints:
                # Convert /api/users/:id to /:id
                route_path = ep["path"].replace(f"/api/{resource}", "")
                if not route_path:
                    route_path = "/"
                
                # Generate handler name
                method = ep["method"].lower()
                if route_path == "/":
                    handler_name = f"getAll" if method == "get" else f"create"
                elif ":id" in route_path:
                    handler_map = {
                        "get": "getById",
                        "put": "update",
                        "patch": "update",
                        "delete": "delete"
                    }
                    handler_name = handler_map.get(method, method)
                else:
                    handler_name = method + route_path.replace("/", "").capitalize()
                
                processed_endpoints.append({
                    "method": ep["method"],
                    "path": ep["path"],
                    "route_path": route_path,
                    "handler_name": handler_name,
                    "requires_auth": ep.get("requires_auth", True)
                })
            
            route_code = route_template.render(
                resource=resource,
                endpoints=processed_endpoints
            )
            
            routes[f"src/routes/{resource}.js"] = route_code
        
        # Generate main routes index
        index_template = Template('''const express = require('express');
const router = express.Router();

{% for resource in resources %}
const {{ resource }}Routes = require('./{{ resource }}');
{% endfor %}

{% for resource in resources %}
router.use('/{{ resource }}', {{ resource }}Routes);
{% endfor %}

module.exports = router;
''')
        
        routes["src/routes/index.js"] = index_template.render(
            resources=list(resources.keys())
        )
        
        return routes
    
    def _generate_fastapi_routes(self, endpoints: List[Dict[str, Any]]) -> Dict[str, str]:
        """Generate FastAPI routes."""
        
        # Group endpoints by resource
        resources = {}
        for endpoint in endpoints:
            resource = endpoint["resource"]
            if resource not in resources:
                resources[resource] = []
            resources[resource].append(endpoint)
        
        routes = {}
        
        # Template for FastAPI router
        route_template = Template('''"""{{ resource | capitalize }} API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.dependencies import get_db, get_current_user
from app.schemas.{{ resource }} import {{ resource | capitalize }}Create, {{ resource | capitalize }}Update, {{ resource | capitalize }}Response
from app.crud import {{ resource }} as crud_{{ resource }}
from app.models.user import User

router = APIRouter(
    prefix="/{{ resource }}",
    tags=["{{ resource }}"]
)


{% for endpoint in endpoints %}
@router.{{ endpoint.method.lower() }}("{{ endpoint.route_path }}"{% if endpoint.method.lower() == 'get' and ':id' not in endpoint.route_path %}, response_model=List[{{ resource | capitalize }}Response]{% elif endpoint.method.lower() in ['get', 'post', 'put', 'patch'] %}, response_model={{ resource | capitalize }}Response{% endif %})
async def {{ endpoint.handler_name }}(
    {% if ':id' in endpoint.route_path %}{{ resource }}_id: int,
    {% endif %}{% if endpoint.method.lower() in ['post', 'put', 'patch'] %}{{ resource }}_data: {{ resource | capitalize }}{% if endpoint.method.lower() == 'post' %}Create{% else %}Update{% endif %},
    {% endif %}db: Session = Depends(get_db){% if endpoint.requires_auth %},
    current_user: User = Depends(get_current_user){% endif %}
):
    """{{ endpoint.description }}"""
    {% if endpoint.method.lower() == 'get' and ':id' not in endpoint.route_path %}
    return crud_{{ resource }}.get_multi(db)
    {% elif endpoint.method.lower() == 'get' %}
    {{ resource }} = crud_{{ resource }}.get(db, id={{ resource }}_id)
    if not {{ resource }}:
        raise HTTPException(status_code=404, detail="{{ resource | capitalize }} not found")
    return {{ resource }}
    {% elif endpoint.method.lower() == 'post' %}
    return crud_{{ resource }}.create(db, obj_in={{ resource }}_data{% if endpoint.requires_auth %}, owner_id=current_user.id{% endif %})
    {% elif endpoint.method.lower() in ['put', 'patch'] %}
    {{ resource }} = crud_{{ resource }}.get(db, id={{ resource }}_id)
    if not {{ resource }}:
        raise HTTPException(status_code=404, detail="{{ resource | capitalize }} not found")
    return crud_{{ resource }}.update(db, db_obj={{ resource }}, obj_in={{ resource }}_data)
    {% elif endpoint.method.lower() == 'delete' %}
    {{ resource }} = crud_{{ resource }}.get(db, id={{ resource }}_id)
    if not {{ resource }}:
        raise HTTPException(status_code=404, detail="{{ resource | capitalize }} not found")
    crud_{{ resource }}.remove(db, id={{ resource }}_id)
    return {"message": "{{ resource | capitalize }} deleted successfully"}
    {% endif %}

{% endfor %}
''')
        
        # Generate route file for each resource
        for resource, resource_endpoints in resources.items():
            processed_endpoints = []
            
            for ep in resource_endpoints:
                # Convert /api/users/:id to /{user_id}
                route_path = ep["path"].replace(f"/api/{resource}", "")
                if not route_path:
                    route_path = "/"
                route_path = route_path.replace(":id", f"{{{resource}_id}}")
                
                # Generate handler name
                method = ep["method"].lower()
                if route_path == "/":
                    if method == "get":
                        handler_name = f"get_{resource}_list"
                    elif method == "post":
                        handler_name = f"create_{resource}"
                    else:
                        handler_name = f"{method}_{resource}"
                elif f"{{{resource}_id}}" in route_path:
                    handler_map = {
                        "get": f"get_{resource}",
                        "put": f"update_{resource}",
                        "patch": f"update_{resource}",
                        "delete": f"delete_{resource}"
                    }
                    handler_name = handler_map.get(method, f"{method}_{resource}")
                else:
                    handler_name = f"{method}_{resource}"
                
                # Generate description
                descriptions = {
                    "get": f"Get {resource}(s)" if route_path == "/" else f"Get {resource} by ID",
                    "post": f"Create new {resource}",
                    "put": f"Update {resource}",
                    "patch": f"Partially update {resource}",
                    "delete": f"Delete {resource}"
                }
                
                processed_endpoints.append({
                    "method": ep["method"],
                    "path": ep["path"],
                    "route_path": route_path,
                    "handler_name": handler_name,
                    "requires_auth": ep.get("requires_auth", True),
                    "description": descriptions.get(method, f"{method.upper()} {resource}")
                })
            
            route_code = route_template.render(
                resource=resource,
                endpoints=processed_endpoints
            )
            
            routes[f"app/api/routes/{resource}.py"] = route_code
        
        # Generate main API router
        api_init_template = Template('''"""API router configuration."""

from fastapi import APIRouter

{% for resource in resources %}
from app.api.routes import {{ resource }}
{% endfor %}

api_router = APIRouter()

{% for resource in resources %}
api_router.include_router({{ resource }}.router, prefix="/api")
{% endfor %}
''')
        
        routes["app/api/__init__.py"] = api_init_template.render(
            resources=list(resources.keys())
        )
        
        return routes
    
    def _generate_nestjs_routes(self, endpoints: List[Dict[str, Any]]) -> Dict[str, str]:
        """Generate NestJS routes (controllers)."""
        
        resources = {}
        for endpoint in endpoints:
            resource = endpoint["resource"]
            if resource not in resources:
                resources[resource] = []
            resources[resource].append(endpoint)
        
        routes = {}
        
        template = Template('''import { Controller, Get, Post, Put, Delete, Body, Param, UseGuards } from '@nestjs/common';
import { {{ resource | capitalize }}Service } from './{{ resource }}.service';
import { Create{{ resource | capitalize }}Dto, Update{{ resource | capitalize }}Dto } from './dto';
import { JwtAuthGuard } from '../auth/jwt-auth.guard';

@Controller('{{ resource }}')
export class {{ resource | capitalize }}Controller {
  constructor(private readonly {{ resource }}Service: {{ resource | capitalize }}Service) {}

{% for endpoint in endpoints %}
  @{{ endpoint.decorator }}('{{ endpoint.route_path }}')
  {% if endpoint.requires_auth %}@UseGuards(JwtAuthGuard)
  {% endif %}async {{ endpoint.handler_name }}(
    {% if ':id' in endpoint.path %}@Param('id') id: string{% endif %}{% if endpoint.method.lower() in ['post', 'put', 'patch'] %}{% if ':id' in endpoint.path %}, {% endif %}@Body() data: {% if endpoint.method.lower() == 'post' %}Create{% else %}Update{% endif %}{{ resource | capitalize }}Dto{% endif %}
  ) {
    {% if endpoint.method.lower() == 'get' and ':id' not in endpoint.path %}return this.{{ resource }}Service.findAll();
    {% elif endpoint.method.lower() == 'get' %}return this.{{ resource }}Service.findOne(id);
    {% elif endpoint.method.lower() == 'post' %}return this.{{ resource }}Service.create(data);
    {% elif endpoint.method.lower() in ['put', 'patch'] %}return this.{{ resource }}Service.update(id, data);
    {% elif endpoint.method.lower() == 'delete' %}return this.{{ resource }}Service.remove(id);
    {% endif %}
  }

{% endfor %}
}
''')
        
        for resource, resource_endpoints in resources.items():
            processed_endpoints = []
            
            for ep in resource_endpoints:
                route_path = ep["path"].replace(f"/api/{resource}", "")
                if not route_path:
                    route_path = ""
                
                method = ep["method"].lower()
                decorator = method.capitalize()
                
                if route_path == "" or route_path == "/":
                    handler_name = "findAll" if method == "get" else "create"
                elif ":id" in route_path:
                    handler_map = {
                        "get": "findOne",
                        "put": "update",
                        "patch": "update",
                        "delete": "remove"
                    }
                    handler_name = handler_map.get(method, method)
                else:
                    handler_name = method
                
                processed_endpoints.append({
                    "method": ep["method"],
                    "path": ep["path"],
                    "route_path": route_path or "",
                    "decorator": decorator,
                    "handler_name": handler_name,
                    "requires_auth": ep.get("requires_auth", True)
                })
            
            route_code = template.render(
                resource=resource,
                endpoints=processed_endpoints
            )
            
            routes[f"src/{resource}/{resource}.controller.ts"] = route_code
        
        return routes
    
    def _generate_django_routes(self, endpoints: List[Dict[str, Any]]) -> Dict[str, str]:
        """Generate Django URLs."""
        
        resources = {}
        for endpoint in endpoints:
            resource = endpoint["resource"]
            if resource not in resources:
                resources[resource] = []
            resources[resource].append(endpoint)
        
        routes = {}
        
        # Django uses ViewSets, so we generate urlpatterns
        template = Template('''from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import {{ resource | capitalize }}ViewSet

router = DefaultRouter()
router.register(r'{{ resource }}', {{ resource | capitalize }}ViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
''')
        
        for resource in resources.keys():
            route_code = template.render(resource=resource)
            routes[f"{{ resource }}/urls.py"] = route_code
        
        return routes
