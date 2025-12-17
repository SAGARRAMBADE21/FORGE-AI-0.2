"""
Controller Generator Agent
Generates controller/handler logic for API routes.
"""

from typing import Dict, Any, List
from jinja2 import Template


class ControllerGeneratorAgent:
    """Generates API controllers."""
    
    def __init__(self, framework: str, llm_config: Dict[str, Any]):
        self.framework = framework
    
    def generate(self, routes: Dict[str, str], 
                 models: Dict[str, str],
                 requirements: Dict[str, Any]) -> Dict[str, str]:
        """Generate controller files."""
        
        generators = {
            "express": self._generate_express_controllers,
            "fastapi": self._generate_fastapi_crud,
            "nestjs": self._generate_nestjs_services,
            "django": self._generate_django_views,
        }
        
        generator = generators.get(self.framework)
        if not generator:
            raise ValueError(f"Unsupported framework: {self.framework}")
        
        return generator(routes, models)
    
    def _generate_express_controllers(self, routes: Dict[str, str], 
                                      models: Dict[str, str]) -> Dict[str, str]:
        """Generate Express controllers."""
        
        controllers = {}
        
        template = Template('''const {{ model }} = require('../models/{{ model }}');

/**
 * {{ model | capitalize }} Controller
 * Handles CRUD operations for {{ model }}
 */

// Get all {{ model }}s
exports.getAll = async (req, res) => {
  try {
    const {{ model }}s = await {{ model }}.findAll();
    res.json({{ model }}s);
  } catch (error) {
    console.error('Error fetching {{ model }}s:', error);
    res.status(500).json({ error: 'Failed to fetch {{ model }}s' });
  }
};

// Get {{ model }} by ID
exports.getById = async (req, res) => {
  try {
    const {{ model }} = await {{ model }}.findByPk(req.params.id);
    if (!{{ model }}) {
      return res.status(404).json({ error: '{{ model | capitalize }} not found' });
    }
    res.json({{ model }});
  } catch (error) {
    console.error('Error fetching {{ model }}:', error);
    res.status(500).json({ error: 'Failed to fetch {{ model }}' });
  }
};

// Create new {{ model }}
exports.create = async (req, res) => {
  try {
    const {{ model }} = await {{ model }}.create(req.body);
    res.status(201).json({{ model }});
  } catch (error) {
    console.error('Error creating {{ model }}:', error);
    res.status(400).json({ error: 'Failed to create {{ model }}', details: error.message });
  }
};

// Update {{ model }}
exports.update = async (req, res) => {
  try {
    const {{ model }} = await {{ model }}.findByPk(req.params.id);
    if (!{{ model }}) {
      return res.status(404).json({ error: '{{ model | capitalize }} not found' });
    }
    await {{ model }}.update(req.body);
    res.json({{ model }});
  } catch (error) {
    console.error('Error updating {{ model }}:', error);
    res.status(400).json({ error: 'Failed to update {{ model }}', details: error.message });
  }
};

// Delete {{ model }}
exports.delete = async (req, res) => {
  try {
    const {{ model }} = await {{ model }}.findByPk(req.params.id);
    if (!{{ model }}) {
      return res.status(404).json({ error: '{{ model | capitalize }} not found' });
    }
    await {{ model }}.destroy();
    res.status(204).send();
  } catch (error) {
    console.error('Error deleting {{ model }}:', error);
    res.status(500).json({ error: 'Failed to delete {{ model }}' });
  }
};
''')
        
        # Extract model names from routes
        for route_path in routes.keys():
            if "/routes/" in route_path:
                model_name = route_path.split("/routes/")[1].replace(".js", "")
                
                controller_code = template.render(model=model_name)
                controllers[f"src/controllers/{model_name}Controller.js"] = controller_code
        
        return controllers
    
    def _generate_fastapi_crud(self, routes: Dict[str, str], 
                               models: Dict[str, str]) -> Dict[str, str]:
        """Generate FastAPI CRUD operations."""
        
        crud_files = {}
        
        template = Template('''"""CRUD operations for {{ model | capitalize }}."""

from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.{{ model }} import {{ model | capitalize }}
from app.schemas.{{ model }} import {{ model | capitalize }}Create, {{ model | capitalize }}Update


def get(db: Session, {{ model }}_id: int) -> Optional[{{ model | capitalize }}]:
    """Get {{ model }} by ID."""
    return db.query({{ model | capitalize }}).filter({{ model | capitalize }}.id == {{ model }}_id).first()


def get_multi(db: Session, skip: int = 0, limit: int = 100) -> List[{{ model | capitalize }}]:
    """Get multiple {{ model }}s."""
    return db.query({{ model | capitalize }}).offset(skip).limit(limit).all()


def create(db: Session, obj_in: {{ model | capitalize }}Create, owner_id: Optional[int] = None) -> {{ model | capitalize }}:
    """Create new {{ model }}."""
    obj_data = obj_in.model_dump()
    if owner_id:
        obj_data["owner_id"] = owner_id
    db_obj = {{ model | capitalize }}(**obj_data)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(db: Session, db_obj: {{ model | capitalize }}, obj_in: {{ model | capitalize }}Update) -> {{ model | capitalize }}:
    """Update {{ model }}."""
    obj_data = obj_in.model_dump(exclude_unset=True)
    for field, value in obj_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def remove(db: Session, {{ model }}_id: int) -> {{ model | capitalize }}:
    """Delete {{ model }}."""
    obj = db.query({{ model | capitalize }}).get({{ model }}_id)
    db.delete(obj)
    db.commit()
    return obj
''')
        
        # Extract model names from routes
        for route_path in routes.keys():
            if "/routes/" in route_path:
                model_name = route_path.split("/routes/")[1].replace(".py", "")
                
                crud_code = template.render(model=model_name)
                crud_files[f"app/crud/{model_name}.py"] = crud_code
        
        return crud_files
    
    def _generate_nestjs_services(self, routes: Dict[str, str], 
                                  models: Dict[str, str]) -> Dict[str, str]:
        """Generate NestJS services."""
        
        services = {}
        
        template = Template('''import { Injectable, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { {{ model | capitalize }} } from './{{ model }}.entity';
import { Create{{ model | capitalize }}Dto, Update{{ model | capitalize }}Dto } from './dto';

@Injectable()
export class {{ model | capitalize }}Service {
  constructor(
    @InjectRepository({{ model | capitalize }})
    private {{ model }}Repository: Repository<{{ model | capitalize }}>,
  ) {}

  async findAll(): Promise<{{ model | capitalize }}[]> {
    return this.{{ model }}Repository.find();
  }

  async findOne(id: string): Promise<{{ model | capitalize }}> {
    const {{ model }} = await this.{{ model }}Repository.findOne({ where: { id } });
    if (!{{ model }}) {
      throw new NotFoundException(`{{ model | capitalize }} with ID ${id} not found`);
    }
    return {{ model }};
  }

  async create(data: Create{{ model | capitalize }}Dto): Promise<{{ model | capitalize }}> {
    const {{ model }} = this.{{ model }}Repository.create(data);
    return this.{{ model }}Repository.save({{ model }});
  }

  async update(id: string, data: Update{{ model | capitalize }}Dto): Promise<{{ model | capitalize }}> {
    await this.findOne(id);
    await this.{{ model }}Repository.update(id, data);
    return this.findOne(id);
  }

  async remove(id: string): Promise<void> {
    const result = await this.{{ model }}Repository.delete(id);
    if (result.affected === 0) {
      throw new NotFoundException(`{{ model | capitalize }} with ID ${id} not found`);
    }
  }
}
''')
        
        for route_path in routes.keys():
            if ".controller.ts" in route_path:
                model_name = route_path.split("/")[1]
                
                service_code = template.render(model=model_name)
                services[f"src/{model_name}/{model_name}.service.ts"] = service_code
        
        return services
    
    def _generate_django_views(self, routes: Dict[str, str], 
                               models: Dict[str, str]) -> Dict[str, str]:
        """Generate Django REST Framework ViewSets."""
        
        views = {}
        
        template = Template('''from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .models import {{ model | capitalize }}
from .serializers import {{ model | capitalize }}Serializer


class {{ model | capitalize }}ViewSet(viewsets.ModelViewSet):
    """ViewSet for {{ model | capitalize }} model."""
    queryset = {{ model | capitalize }}.objects.all()
    serializer_class = {{ model | capitalize }}Serializer
    permission_classes = [permissions.IsAuthenticated]
''')
        
        for route_path in routes.keys():
            if "/urls.py" in route_path:
                model_name = route_path.split("/")[0]
                
                view_code = template.render(model=model_name)
                views[f"{model_name}/views.py"] = view_code
        
        return views
