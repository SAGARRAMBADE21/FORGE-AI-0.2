"""
Docker Generator Agent
Generates Dockerfile and docker-compose.yml.
"""

from typing import Dict, Any
from jinja2 import Template


class DockerGeneratorAgent:
    """Generates Docker configuration."""
    
    def __init__(self, stack: Dict[str, str]):
        self.stack = stack
    
    def generate(self, project_structure: Dict[str, Any], 
                 dependencies: Dict[str, Any]) -> Dict[str, str]:
        """Generate Docker files."""
        
        docker_files = {}
        
        # Generate Dockerfile
        if self.stack["language"] == "node":
            docker_files["Dockerfile"] = self._generate_node_dockerfile()
        else:
            docker_files["Dockerfile"] = self._generate_python_dockerfile()
        
        # Generate docker-compose.yml
        docker_files["docker-compose.yml"] = self._generate_docker_compose()
        
        # Generate .dockerignore
        docker_files[".dockerignore"] = self._generate_dockerignore()
        
        return docker_files
    
    def _generate_node_dockerfile(self) -> str:
        """Generate Node.js Dockerfile."""
        
        template = '''# Node.js Backend Dockerfile
FROM node:18-alpine

# Create app directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy app source
COPY . .

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
  CMD node -e "require('http').get('http://localhost:3000/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

# Start app
CMD ["npm", "start"]
'''
        return template
    
    def _generate_python_dockerfile(self) -> str:
        """Generate Python Dockerfile."""
        
        template = '''# Python Backend Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \\
    PYTHONDONTWRITEBYTECODE=1 \\
    PIP_NO_CACHE_DIR=1 \\
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create app directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    postgresql-client \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
  CMD curl -f http://localhost:8000/health || exit 1

# Start app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
'''
        return template
    
    def _generate_docker_compose(self) -> str:
        """Generate docker-compose.yml."""
        
        database = self.stack["database"]
        
        if database == "postgresql":
            db_service = '''  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: ${DB_USER:-postgres}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-postgres}
      POSTGRES_DB: ${DB_NAME:-app_db}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5'''
            
            volumes = '''volumes:
  postgres_data:'''
        
        elif database == "mongodb":
            db_service = '''  db:
    image: mongo:7
    environment:
      MONGO_INITDB_ROOT_USERNAME: ${DB_USER:-admin}
      MONGO_INITDB_ROOT_PASSWORD: ${DB_PASSWORD:-admin}
    volumes:
      - mongo_data:/data/db
    ports:
      - "27017:27017"
    healthcheck:
      test: echo 'db.runCommand("ping").ok' | mongosh localhost:27017/test --quiet
      interval: 10s
      timeout: 5s
      retries: 5'''
            
            volumes = '''volumes:
  mongo_data:'''
        
        elif database == "mysql":
            db_service = '''  db:
    image: mysql:8
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_PASSWORD:-root}
      MYSQL_DATABASE: ${DB_NAME:-app_db}
      MYSQL_USER: ${DB_USER:-user}
      MYSQL_PASSWORD: ${DB_PASSWORD:-password}
    volumes:
      - mysql_data:/var/lib/mysql
    ports:
      - "3306:3306"
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5'''
            
            volumes = '''volumes:
  mysql_data:'''
        
        else:
            db_service = ""
            volumes = ""
        
        port = "3000" if self.stack["language"] == "node" else "8000"
        
        template = f'''version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "{port}:{port}"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgresql://${{DB_USER:-postgres}}:${{DB_PASSWORD:-postgres}}@db:5432/${{DB_NAME:-app_db}}
      - JWT_SECRET=${{JWT_SECRET:-change-this-secret}}
      - PORT={port}
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs

{db_service}

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

{volumes}
  redis_data:
'''
        return template
    
    def _generate_dockerignore(self) -> str:
        """Generate .dockerignore file."""
        
        if self.stack["language"] == "node":
            return '''# Node
node_modules
npm-debug.log
yarn-error.log

# Environment
.env
.env.*

# Git
.git
.gitignore

# IDE
.vscode
.idea

# Tests
tests
*.test.js
coverage

# Documentation
README.md
docs

# Misc
.DS_Store
*.log
'''
        else:
            return '''# Python
__pycache__
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info
dist
build

# Virtual environment
venv
env
ENV

# Environment
.env
.env.*

# Git
.git
.gitignore

# IDE
.vscode
.idea

# Tests
tests
*.test.py
.pytest_cache
.coverage
htmlcov

# Documentation
README.md
docs

# Misc
.DS_Store
*.log
'''
