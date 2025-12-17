"""
ORM Generator Agent
Generates ORM models (SQLAlchemy, Sequelize, Prisma, Mongoose, TypeORM).
"""

from typing import Dict, Any, List
from jinja2 import Template


class ORMGeneratorAgent:
    """Generates ORM models."""
    
    def __init__(self, orm_type: str, llm_config: Dict[str, Any]):
        self.orm_type = orm_type
    
    def generate(self, schema: Dict[str, Any], framework: str) -> Dict[str, str]:
        """Generate ORM models."""
        
        generators = {
            "sqlalchemy": self._generate_sqlalchemy,
            "sequelize": self._generate_sequelize,
            "prisma": self._generate_prisma,
            "mongoose": self._generate_mongoose,
            "typeorm": self._generate_typeorm,
        }
        
        generator = generators.get(self.orm_type)
        if not generator:
            raise ValueError(f"Unsupported ORM: {self.orm_type}")
        
        return generator(schema)
    
    def _generate_sqlalchemy(self, schema: Dict[str, Any]) -> Dict[str, str]:
        """Generate SQLAlchemy models."""
        
        models = {}
        
        # Base template
        base_template = '''"""Database models using SQLAlchemy."""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


'''
        
        model_template = Template('''class {{ model_name }}(Base):
    """{{ model_name }} model."""
    __tablename__ = "{{ table_name }}"
    
{% for field in fields %}    {{ field.name }} = Column({{ field.type }}{% if field.primary_key %}, primary_key=True{% endif %}{% if field.nullable == False %}, nullable=False{% endif %}{% if field.unique %}, unique=True{% endif %}{% if field.default %}, default={{ field.default }}{% endif %})
{% endfor %}
{% for rel in relationships %}    {{ rel.name }} = relationship("{{ rel.model }}", back_populates="{{ rel.back_populates }}")
{% endfor %}
''')
        
        all_models = ""
        for table in schema.get("tables", []):
            model_name = table["model"]
            table_name = table["name"]
            
            # Convert fields
            fields = []
            for col_def in table["ddl"].split("\n")[1:-1]:
                col_def = col_def.strip().rstrip(",")
                if not col_def:
                    continue
                
                parts = col_def.split()
                if len(parts) < 2:
                    continue
                
                field_name = parts[0]
                field_type = parts[1]
                
                type_map = {
                    "SERIAL": "Integer",
                    "INTEGER": "Integer",
                    "VARCHAR(255)": "String(255)",
                    "TEXT": "Text",
                    "BOOLEAN": "Boolean",
                    "TIMESTAMP": "DateTime(timezone=True), server_default=func.now()",
                    "DECIMAL(10,": "DECIMAL(10, 2)",
                }
                
                sa_type = type_map.get(field_type, "String")
                
                fields.append({
                    "name": field_name,
                    "type": sa_type,
                    "primary_key": "PRIMARY KEY" in col_def,
                    "nullable": "NOT NULL" not in col_def,
                    "unique": "UNIQUE" in col_def,
                    "default": None
                })
            
            model_code = model_template.render(
                model_name=model_name,
                table_name=table_name,
                fields=fields,
                relationships=[]
            )
            
            all_models += model_code + "\n\n"
        
        models[f"app/models/__init__.py"] = base_template + all_models
        
        return models
    
    def _generate_sequelize(self, schema: Dict[str, Any]) -> Dict[str, str]:
        """Generate Sequelize models."""
        
        models = {}
        
        template = Template('''const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const {{ model_name }} = sequelize.define('{{ model_name }}', {
{% for field in fields %}  {{ field.name }}: {
    type: DataTypes.{{ field.type }},
{% if field.primary_key %}    primaryKey: true,
    autoIncrement: true,
{% endif %}{% if field.allowNull == False %}    allowNull: false,
{% endif %}{% if field.unique %}    unique: true,
{% endif %}  },
{% endfor %}}, {
  tableName: '{{ table_name }}',
  timestamps: true,
});

module.exports = {{ model_name }};
''')
        
        for table in schema.get("tables", []):
            model_name = table["model"]
            table_name = table["name"]
            
            fields = []
            # Parse fields from DDL (simplified)
            for line in table["ddl"].split("\n")[1:-1]:
                line = line.strip().rstrip(",")
                if not line:
                    continue
                parts = line.split()
                if len(parts) < 2:
                    continue
                
                field_name = parts[0]
                field_type = parts[1]
                
                type_map = {
                    "SERIAL": "INTEGER",
                    "INTEGER": "INTEGER",
                    "VARCHAR(255)": "STRING",
                    "TEXT": "TEXT",
                    "BOOLEAN": "BOOLEAN",
                    "TIMESTAMP": "DATE",
                }
                
                seq_type = type_map.get(field_type, "STRING")
                
                fields.append({
                    "name": field_name,
                    "type": seq_type,
                    "primary_key": "PRIMARY KEY" in line,
                    "allowNull": "NOT NULL" not in line,
                    "unique": "UNIQUE" in line
                })
            
            model_code = template.render(
                model_name=model_name,
                table_name=table_name,
                fields=fields
            )
            
            models[f"src/models/{model_name}.js"] = model_code
        
        return models
    
    def _generate_prisma(self, schema: Dict[str, Any]) -> Dict[str, str]:
        """Generate Prisma schema."""
        
        prisma_schema = '''// Prisma schema
// Learn more: https://pris.ly/d/prisma-schema

generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

'''
        
        for table in schema.get("tables", []):
            model_name = table["model"]
            
            prisma_schema += f"model {model_name} {{\n"
            
            # Parse fields
            for line in table["ddl"].split("\n")[1:-1]:
                line = line.strip().rstrip(",")
                if not line:
                    continue
                parts = line.split()
                if len(parts) < 2:
                    continue
                
                field_name = parts[0]
                field_type = parts[1]
                
                type_map = {
                    "SERIAL": "Int @id @default(autoincrement())",
                    "INTEGER": "Int",
                    "VARCHAR(255)": "String",
                    "TEXT": "String",
                    "BOOLEAN": "Boolean",
                    "TIMESTAMP": "DateTime @default(now())",
                }
                
                prisma_type = type_map.get(field_type, "String")
                
                optional = "" if "NOT NULL" in line else "?"
                unique = " @unique" if "UNIQUE" in line else ""
                
                prisma_schema += f"  {field_name}  {prisma_type}{optional}{unique}\n"
            
            prisma_schema += "}\n\n"
        
        return {"prisma/schema.prisma": prisma_schema}
    
    def _generate_mongoose(self, schema: Dict[str, Any]) -> Dict[str, str]:
        """Generate Mongoose schemas."""
        
        models = {}
        
        template = Template('''const mongoose = require('mongoose');

const {{ model_name }}Schema = new mongoose.Schema({
{% for field in fields %}  {{ field.name }}: {
    type: {{ field.type }},
{% if field.required %}    required: true,
{% endif %}{% if field.unique %}    unique: true,
{% endif %}  },
{% endfor %}}, {
  timestamps: true
});

module.exports = mongoose.model('{{ model_name }}', {{ model_name }}Schema);
''')
        
        for collection in schema.get("collections", []):
            model_name = collection["name"]
            
            fields = []
            for field in collection["fields"]:
                type_map = {
                    "integer": "Number",
                    "string": "String",
                    "text": "String",
                    "boolean": "Boolean",
                    "datetime": "Date",
                    "decimal": "Number",
                }
                
                fields.append({
                    "name": field["name"],
                    "type": type_map.get(field["type"], "String"),
                    "required": field.get("required", False),
                    "unique": field.get("unique", False)
                })
            
            model_code = template.render(
                model_name=model_name,
                fields=fields
            )
            
            models[f"src/models/{model_name}.js"] = model_code
        
        return models
    
    def _generate_typeorm(self, schema: Dict[str, Any]) -> Dict[str, str]:
        """Generate TypeORM entities."""
        
        models = {}
        
        template = Template('''import { Entity, PrimaryGeneratedColumn, Column, CreateDateColumn, UpdateDateColumn } from 'typeorm';

@Entity('{{ table_name }}')
export class {{ model_name }} {
{% for field in fields %}  @{{ field.decorator }}
  {{ field.name }}{% if field.optional %}?{% endif %}: {{ field.type }};

{% endfor %}  @CreateDateColumn()
  created_at: Date;

  @UpdateDateColumn()
  updated_at: Date;
}
''')
        
        for table in schema.get("tables", []):
            model_name = table["model"]
            table_name = table["name"]
            
            fields = []
            for line in table["ddl"].split("\n")[1:-1]:
                line = line.strip().rstrip(",")
                if not line or "created_at" in line or "updated_at" in line:
                    continue
                parts = line.split()
                if len(parts) < 2:
                    continue
                
                field_name = parts[0]
                field_type = parts[1]
                
                if "PRIMARY KEY" in line:
                    decorator = "PrimaryGeneratedColumn()"
                    ts_type = "number"
                else:
                    unique = ", { unique: true }" if "UNIQUE" in line else ""
                    decorator = f"Column({unique})" if unique else "Column()"
                    
                    type_map = {
                        "INTEGER": "number",
                        "VARCHAR(255)": "string",
                        "TEXT": "string",
                        "BOOLEAN": "boolean",
                        "TIMESTAMP": "Date",
                    }
                    ts_type = type_map.get(field_type, "string")
                
                fields.append({
                    "name": field_name,
                    "type": ts_type,
                    "decorator": decorator,
                    "optional": "NOT NULL" not in line
                })
            
            model_code = template.render(
                model_name=model_name,
                table_name=table_name,
                fields=fields
            )
            
            models[f"src/entities/{model_name}.ts"] = model_code
        
        return models
