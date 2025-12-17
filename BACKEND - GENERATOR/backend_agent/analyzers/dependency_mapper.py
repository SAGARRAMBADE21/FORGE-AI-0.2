"""
Dependency Mapper Agent
Maps and resolves dependencies between components.
"""

from typing import Dict, Any, List


class DependencyMapperAgent:
    """Maps dependencies for the backend."""
    
    def __init__(self):
        self.dependency_map = {
            "node": {
                "express": {
                    "core": ["express", "dotenv", "cors"],
                    "database": {
                        "postgresql": ["pg", "sequelize"],
                        "mongodb": ["mongoose"],
                        "mysql": ["mysql2", "sequelize"]
                    },
                    "auth": ["jsonwebtoken", "bcrypt", "passport"],
                    "validation": ["joi", "express-validator"],
                    "testing": ["jest", "supertest"],
                    "dev": ["nodemon", "eslint", "prettier"]
                },
                "nestjs": {
                    "core": ["@nestjs/core", "@nestjs/common", "@nestjs/platform-express"],
                    "database": {
                        "postgresql": ["@nestjs/typeorm", "typeorm", "pg"],
                        "mongodb": ["@nestjs/mongoose", "mongoose"]
                    },
                    "auth": ["@nestjs/jwt", "@nestjs/passport", "bcrypt"],
                    "validation": ["class-validator", "class-transformer"],
                    "testing": ["@nestjs/testing", "jest"],
                    "dev": ["@nestjs/cli"]
                }
            },
            "python": {
                "fastapi": {
                    "core": ["fastapi==0.110.0", "uvicorn[standard]==0.29.0", "python-dotenv==1.0.1"],
                    "database": {
                        "postgresql": ["sqlalchemy==2.0.27", "psycopg2-binary==2.9.9", "alembic==1.13.1"],
                        "mongodb": ["motor==3.3.2", "beanie==1.24.0"],
                        "mysql": ["sqlalchemy==2.0.27", "pymysql==1.1.0", "alembic==1.13.1"]
                    },
                    "auth": ["python-jose[cryptography]==3.3.0", "passlib[bcrypt]==1.7.4", "python-multipart==0.0.9"],
                    "validation": ["pydantic==2.6.4", "pydantic-settings==2.2.1"],
                    "testing": ["pytest==8.0.2", "pytest-asyncio==0.23.5", "httpx==0.27.0"],
                    "dev": ["black==24.2.0", "isort==5.13.2"]
                },
                "django": {
                    "core": ["Django==5.0.2", "python-dotenv==1.0.1"],
                    "database": {
                        "postgresql": ["psycopg2-binary==2.9.9"],
                        "mongodb": ["djongo==1.3.6"],
                        "mysql": ["mysqlclient==2.2.4"]
                    },
                    "auth": ["djangorestframework==3.14.0", "djangorestframework-simplejwt==5.3.1"],
                    "validation": ["django-cors-headers==4.3.1"],
                    "testing": ["pytest-django==4.8.0"],
                    "dev": ["black==24.2.0"]
                }
            }
        }
    
    def map_dependencies(self, stack: Dict[str, str], 
                        features: Dict[str, bool]) -> Dict[str, Any]:
        """Map dependencies based on stack and features."""
        
        language = stack["language"]
        framework = stack["framework"]
        database = stack["database"]
        
        deps = self.dependency_map.get(language, {}).get(framework, {})
        
        # Core dependencies
        dependencies = list(deps.get("core", []))
        
        # Database dependencies
        db_deps = deps.get("database", {}).get(database, [])
        dependencies.extend(db_deps)
        
        # Feature dependencies
        if features.get("auth"):
            dependencies.extend(deps.get("auth", []))
        
        if features.get("validation"):
            dependencies.extend(deps.get("validation", []))
        
        if features.get("testing"):
            dependencies.extend(deps.get("testing", []))
        
        # Dev dependencies
        dev_dependencies = list(deps.get("dev", []))
        
        # Format for package manager
        if language == "node":
            return {
                "package_json": self._format_package_json(dependencies, dev_dependencies),
                "npm": dependencies,
                "npm_dev": dev_dependencies
            }
        else:
            return {
                "pip": dependencies,
                "pip_dev": dev_dependencies
            }
    
    def _format_package_json(self, deps: List[str], dev_deps: List[str]) -> str:
        """Format package.json content."""
        import json
        
        # Parse version from deps
        dependencies = {}
        for dep in deps:
            parts = dep.split("@")
            name = parts[0]
            version = f"^{parts[1]}" if len(parts) > 1 else "latest"
            dependencies[name] = version
        
        dev_dependencies = {}
        for dep in dev_deps:
            parts = dep.split("@")
            name = parts[0]
            version = f"^{parts[1]}" if len(parts) > 1 else "latest"
            dev_dependencies[name] = version
        
        package = {
            "name": "generated-backend",
            "version": "1.0.0",
            "description": "Auto-generated backend",
            "main": "src/server.js",
            "scripts": {
                "start": "node src/server.js",
                "dev": "nodemon src/server.js",
                "test": "jest"
            },
            "dependencies": dependencies,
            "devDependencies": dev_dependencies
        }
        
        return json.dumps(package, indent=2)
                