"""
Validation Generator Agent
Generates validation schemas (Pydantic, Joi, class-validator).
"""

from typing import Dict, Any, List
from jinja2 import Template


class ValidationGeneratorAgent:
    """Generates validation schemas."""
    
    def __init__(self, framework: str, llm_config: Dict[str, Any]):
        self.framework = framework
    
    def generate(self, data_models: List[Dict[str, Any]], 
                 endpoints: List[Dict[str, Any]]) -> Dict[str, str]:
        """Generate validation schemas."""
        
        generators = {
            "express": self._generate_joi_schemas,
            "fastapi": self._generate_pydantic_schemas,
            "nestjs": self._generate_class_validator_dtos,
            "django": self._generate_drf_serializers,
        }
        
        generator = generators.get(self.framework)
        if not generator:
            raise ValueError(f"Unsupported framework: {self.framework}")
        
        return generator(data_models)
    
    def _generate_pydantic_schemas(self, data_models: List[Dict[str, Any]]) -> Dict[str, str]:
        """Generate Pydantic schemas for FastAPI."""
        
        schemas = {}
        
        template = Template('''"""Pydantic schemas for {{ model.name }}."""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class {{ model.name }}Base(BaseModel):
    """Base {{ model.name }} schema."""
{% for field in model.fields %}{% if field.name not in ['id', 'created_at', 'updated_at'] %}    {{ field.name }}: {% if not field.required %}Optional[{% endif %}{{ field.pydantic_type }}{% if not field.required %}]{% endif %}{% if field.description %} = Field(..., description="{{ field.description }}"){% endif %}
{% endif %}{% endfor %}


class {{ model.name }}Create({{ model.name }}Base):
    """Schema for creating {{ model.name }}."""
    pass


class {{ model.name }}Update(BaseModel):
    """Schema for updating {{ model.name }}."""
{% for field in model.fields %}{% if field.name not in ['id', 'created_at', 'updated_at'] %}    {{ field.name }}: Optional[{{ field.pydantic_type }}] = None
{% endif %}{% endfor %}


class {{ model.name }}Response({{ model.name }}Base):
    """Schema for {{ model.name }} response."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
''')
        
        for model in data_models:
            # Convert field types to Pydantic types
            processed_fields = []
            for field in model["fields"]:
                type_map = {
                    "integer": "int",
                    "string": "str",
                    "text": "str",
                    "boolean": "bool",
                    "datetime": "datetime",
                    "decimal": "float",
                    "float": "float",
                }
                
                pydantic_type = type_map.get(field["type"], "str")
                
                # Special case for email fields
                if field["name"] == "email":
                    pydantic_type = "EmailStr"
                
                processed_fields.append({
                    **field,
                    "pydantic_type": pydantic_type,
                    "required": field.get("required", True)
                })
            
            model_with_types = {**model, "fields": processed_fields}
            
            schema_code = template.render(model=model_with_types)
            schemas[f"app/schemas/{model['name'].lower()}.py"] = schema_code
        
        return schemas
    
    def _generate_joi_schemas(self, data_models: List[Dict[str, Any]]) -> Dict[str, str]:
        """Generate Joi validation schemas for Express."""
        
        schemas = {}
        
        template = Template('''const Joi = require('joi');

/**
 * Validation schemas for {{ model.name }}
 */

const {{ model.name.lower() }}Schema = {
  create: Joi.object({
{% for field in model.fields %}{% if field.name not in ['id', 'created_at', 'updated_at'] %}    {{ field.name }}: Joi.{{ field.joi_type }}(){% if field.required %}.required(){% endif %}{% if field.min %}.min({{ field.min }}){% endif %}{% if field.max %}.max({{ field.max }}){% endif %},
{% endif %}{% endfor %}  }),

  update: Joi.object({
{% for field in model.fields %}{% if field.name not in ['id', 'created_at', 'updated_at'] %}    {{ field.name }}: Joi.{{ field.joi_type }}(){% if field.min %}.min({{ field.min }}){% endif %}{% if field.max %}.max({{ field.max }}){% endif %},
{% endif %}{% endfor %}  }).min(1), // At least one field required for update
};

module.exports = {{ model.name.lower() }}Schema;
''')
        
        for model in data_models:
            # Convert to Joi types
            processed_fields = []
            for field in model["fields"]:
                type_map = {
                    "integer": "number().integer",
                    "string": "string",
                    "text": "string",
                    "boolean": "boolean",
                    "datetime": "date",
                    "decimal": "number",
                    "float": "number",
                }
                
                joi_type = type_map.get(field["type"], "string")
                
                # Add validations
                field_data = {
                    **field,
                    "joi_type": joi_type,
                    "required": field.get("required", True)
                }
                
                if field["name"] == "email":
                    field_data["joi_type"] = "string().email"
                
                if field["type"] == "string":
                    field_data["min"] = field.get("min_length", 1)
                    field_data["max"] = field.get("max_length", 255)
                
                processed_fields.append(field_data)
            
            model_with_types = {**model, "fields": processed_fields}
            
            schema_code = template.render(model=model_with_types)
            schemas[f"src/validators/{model['name'].lower()}.js"] = schema_code
        
        return schemas
    
    def _generate_class_validator_dtos(self, data_models: List[Dict[str, Any]]) -> Dict[str, str]:
        """Generate class-validator DTOs for NestJS."""
        
        dtos = {}
        
        template = Template('''import { IsString, IsEmail, IsInt, IsBoolean, IsOptional, MinLength, MaxLength } from 'class-validator';

export class Create{{ model.name }}Dto {
{% for field in model.fields %}{% if field.name not in ['id', 'created_at', 'updated_at'] %}{% for decorator in field.decorators %}  @{{ decorator }}
{% endfor %}  {{ field.name }}{% if not field.required %}?{% endif %}: {{ field.ts_type }};

{% endif %}{% endfor %}}

export class Update{{ model.name }}Dto {
{% for field in model.fields %}{% if field.name not in ['id', 'created_at', 'updated_at'] %}  @IsOptional()
{% for decorator in field.decorators %}  @{{ decorator }}
{% endfor %}  {{ field.name }}?: {{ field.ts_type }};

{% endif %}{% endfor %}}
''')
        
        for model in data_models:
            processed_fields = []
            for field in model["fields"]:
                type_map = {
                    "integer": "number",
                    "string": "string",
                    "text": "string",
                    "boolean": "boolean",
                    "datetime": "Date",
                    "decimal": "number",
                }
                
                ts_type = type_map.get(field["type"], "string")
                
                # Add decorators
                decorators = []
                if field["type"] in ["string", "text"]:
                    decorators.append("IsString()")
                    if field.get("min_length"):
                        decorators.append(f"MinLength({field['min_length']})")
                    if field.get("max_length"):
                        decorators.append(f"MaxLength({field['max_length']})")
                elif field["type"] == "integer":
                    decorators.append("IsInt()")
                elif field["type"] == "boolean":
                    decorators.append("IsBoolean()")
                
                if field["name"] == "email":
                    decorators = ["IsEmail()"]
                
                processed_fields.append({
                    **field,
                    "ts_type": ts_type,
                    "decorators": decorators,
                    "required": field.get("required", True)
                })
            
            model_with_types = {**model, "fields": processed_fields}
            
            dto_code = template.render(model=model_with_types)
            dtos[f"src/{model['name'].lower()}/dto/index.ts"] = dto_code
        
        return dtos
    
    def _generate_drf_serializers(self, data_models: List[Dict[str, Any]]) -> Dict[str, str]:
        """Generate Django REST Framework serializers."""
        
        serializers = {}
        
        template = Template('''from rest_framework import serializers
from .models import {{ model.name }}


class {{ model.name }}Serializer(serializers.ModelSerializer):
    """Serializer for {{ model.name }} model."""
    
    class Meta:
        model = {{ model.name }}
        fields = [{% for field in model.fields %}'{{ field.name }}'{% if not loop.last %}, {% endif %}{% endfor %}]
        read_only_fields = ['id', 'created_at', 'updated_at']
''')
        
        for model in data_models:
            serializer_code = template.render(model=model)
            serializers[f"{model['name'].lower()}/serializers.py"] = serializer_code
        
        return serializers
