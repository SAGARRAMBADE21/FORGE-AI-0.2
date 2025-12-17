"""
Code Integrator Agent
Combines all generated code into final project structure.
"""

from typing import Dict, Any, List
from pathlib import Path


class CodeIntegratorAgent:
    """Integrates all generated code."""
    
    def __init__(self, framework: str):
        self.framework = framework
    
    def integrate(self, 
                  orm_models: Dict[str, str],
                  routes: Dict[str, str],
                  controllers: Dict[str, str],
                  services: Dict[str, str],
                  auth: Dict[str, str],
                  validation: Dict[str, str],
                  tests: Dict[str, str],
                  migrations: List[Dict[str, str]],
                  docker: Dict[str, str],
                  cicd: Dict[str, str],
                  structure: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate all code files."""
        
        all_files = {}
        
        # Merge all file dictionaries
        all_files.update(orm_models)
        all_files.update(routes)
        all_files.update(controllers)
        all_files.update(services)
        all_files.update(auth)
        all_files.update(validation)
        all_files.update(tests)
        all_files.update(docker)
        all_files.update(cicd)
        
        # Add migrations
        for migration in migrations:
            all_files[migration["filename"]] = migration["up"]
        
        # Generate main application file
        if self.framework == "express":
            all_files.update(self._generate_express_main())
        elif self.framework == "fastapi":
            all_files.update(self._generate_fastapi_main())
        elif self.framework == "nestjs":
            all_files.update(self._generate_nestjs_main())
        
        # Extract dependencies
        dependencies = self._extract_dependencies(all_files)
        
        # Extract environment variables
        env_vars = self._extract_env_variables(all_files)
        
        return {
            "files": all_files,
            "dependencies": dependencies,
            "env_vars": env_vars
        }
    
    def _generate_express_main(self) -> Dict[str, str]:
        """Generate Express main application files."""
        
        app_js = '''const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
require('dotenv').config();

const routes = require('./routes');
const errorHandler = require('./middleware/errorHandler');

const app = express();

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(morgan('combined'));

// Routes
app.use('/api', routes);

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Error handler
app.use(errorHandler);

module.exports = app;
'''
        
        server_js = '''const app = require('./app');
const port = process.env.PORT || 3000;

app.listen(port, () => {
  console.log(`Server running on port ${port}`);
  console.log(`Environment: ${process.env.NODE_ENV || 'development'}`);
});
'''
        
        return {
            "src/app.js": app_js,
            "src/server.js": server_js
        }
    
    def _generate_fastapi_main(self) -> Dict[str, str]:
        """Generate FastAPI main application file."""
        
        main_py = '''"""Main FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.api import api_router
from app.core.config import settings
from app.core.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Auto-generated backend API"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include API router
app.include_router(api_router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "version": "1.0.0"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to the API", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
        
        database_py = '''"""Database configuration."""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Database dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
'''
        
        return {
            "app/main.py": main_py,
            "app/core/database.py": database_py
        }
    
    def _generate_nestjs_main(self) -> Dict[str, str]:
        """Generate NestJS main file."""
        
        main_ts = '''import { NestFactory } from '@nestjs/core';
import { ValidationPipe } from '@nestjs/common';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  
  app.useGlobalPipes(new ValidationPipe());
  app.enableCors();
  
  await app.listen(3000);
  console.log(`Application is running on: ${await app.getUrl()}`);
}
bootstrap();
'''
        
        return {"src/main.ts": main_ts}
    
    def _extract_dependencies(self, files: Dict[str, str]) -> Dict[str, Any]:
        """Extract dependencies from code."""
        # Simplified - should parse imports
        return {
            "npm": [],
            "pip": []
        }
    
    def _extract_env_variables(self, files: Dict[str, str]) -> Dict[str, str]:
        """Extract environment variables from code."""
        env_vars = {
            "PORT": "3000",
            "NODE_ENV": "development",
            "DATABASE_URL": "postgresql://user:password@localhost:5432/dbname",
            "JWT_SECRET": "change-this-secret-key",
            "JWT_EXPIRATION": "24h"
        }
        return env_vars
