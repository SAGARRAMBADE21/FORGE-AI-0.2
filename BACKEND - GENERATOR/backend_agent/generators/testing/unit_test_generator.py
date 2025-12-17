"""
Unit Test Generator Agent
Generates unit tests for routes, controllers, services.
"""

from typing import Dict, Any
from jinja2 import Template


class UnitTestGeneratorAgent:
    """Generates unit tests."""
    
    def __init__(self, framework: str, llm_config: Dict[str, Any]):
        self.framework = framework
    
    def generate(self, routes: Dict[str, str], 
                 controllers: Dict[str, str],
                 services: Dict[str, str]) -> Dict[str, str]:
        """Generate test files."""
        
        if self.framework == "fastapi":
            return self._generate_pytest_tests(routes)
        elif self.framework == "express":
            return self._generate_jest_tests(routes)
        elif self.framework == "nestjs":
            return self._generate_nestjs_tests()
        else:
            return {}
    
    def _generate_pytest_tests(self, routes: Dict[str, str]) -> Dict[str, str]:
        """Generate pytest tests for FastAPI."""
        
        tests = {}
        
        # Conftest (fixtures)
        conftest_template = '''"""PyTest configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db():
    """Database fixture."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db):
    """Test client fixture."""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)
'''
        
        # API tests template
        test_template = Template('''"""Test {{ resource }} API endpoints."""

import pytest
from fastapi import status


def test_get_{{ resource }}_list(client):
    """Test GET /{{ resource }}/ endpoint."""
    response = client.get("/api/{{ resource }}/")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


def test_create_{{ resource }}(client):
    """Test POST /{{ resource }}/ endpoint."""
    data = {
        "name": "Test {{ resource | capitalize }}",
        "description": "Test description"
    }
    response = client.post("/api/{{ resource }}/", json=data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["name"] == data["name"]


def test_get_{{ resource }}_by_id(client):
    """Test GET /{{ resource }}/:id endpoint."""
    # Create first
    data = {"name": "Test", "description": "Test"}
    create_response = client.post("/api/{{ resource }}/", json=data)
    {{ resource }}_id = create_response.json()["id"]
    
    # Get
    response = client.get(f"/api/{{ resource }}/{ {{ resource }}_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == {{ resource }}_id


def test_update_{{ resource }}(client):
    """Test PUT /{{ resource }}/:id endpoint."""
    # Create first
    data = {"name": "Test", "description": "Test"}
    create_response = client.post("/api/{{ resource }}/", json=data)
    {{ resource }}_id = create_response.json()["id"]
    
    # Update
    update_data = {"name": "Updated"}
    response = client.put(f"/api/{{ resource }}/{ {{ resource }}_id}", json=update_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "Updated"


def test_delete_{{ resource }}(client):
    """Test DELETE /{{ resource }}/:id endpoint."""
    # Create first
    data = {"name": "Test", "description": "Test"}
    create_response = client.post("/api/{{ resource }}/", json=data)
    {{ resource }}_id = create_response.json()["id"]
    
    # Delete
    response = client.delete(f"/api/{{ resource }}/{ {{ resource }}_id}")
    assert response.status_code == status.HTTP_200_OK
    
    # Verify deleted
    get_response = client.get(f"/api/{{ resource }}/{ {{ resource }}_id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND
''')
        
        tests["tests/conftest.py"] = conftest_template
        
        # Generate test for each route
        for route_path in routes.keys():
            if "/routes/" in route_path:
                resource = route_path.split("/routes/")[1].replace(".py", "")
                test_code = test_template.render(resource=resource)
                tests[f"tests/test_{resource}.py"] = test_code
        
        return tests
    
    def _generate_jest_tests(self, routes: Dict[str, str]) -> Dict[str, str]:
        """Generate Jest tests for Express."""
        
        tests = {}
        
        # Setup file
        setup_template = '''const request = require('supertest');
const app = require('../src/app');

// Test helpers
global.request = request;
global.app = app;
'''
        
        # Test template
        test_template = Template('''const request = require('supertest');
const app = require('../src/app');

describe('{{ resource | capitalize }} API', () => {
  let {{ resource }}Id;

  it('should get all {{ resource }}s', async () => {
    const response = await request(app)
      .get('/api/{{ resource }}')
      .expect(200);
    
    expect(Array.isArray(response.body)).toBe(true);
  });

  it('should create a {{ resource }}', async () => {
    const data = {
      name: 'Test {{ resource | capitalize }}',
      description: 'Test description'
    };
    
    const response = await request(app)
      .post('/api/{{ resource }}')
      .send(data)
      .expect(201);
    
    expect(response.body.name).toBe(data.name);
    {{ resource }}Id = response.body.id;
  });

  it('should get {{ resource }} by ID', async () => {
    const response = await request(app)
      .get(`/api/{{ resource }}/${{{ resource }}Id}`)
      .expect(200);
    
    expect(response.body.id).toBe({{ resource }}Id);
  });

  it('should update {{ resource }}', async () => {
    const updateData = { name: 'Updated Name' };
    
    const response = await request(app)
      .put(`/api/{{ resource }}/${{{ resource }}Id}`)
      .send(updateData)
      .expect(200);
    
    expect(response.body.name).toBe(updateData.name);
  });

  it('should delete {{ resource }}', async () => {
    await request(app)
      .delete(`/api/{{ resource }}/${{{ resource }}Id}`)
      .expect(204);
  });
});
''')
        
        tests["tests/setup.js"] = setup_template
        
        # Generate test for each route
        for route_path in routes.keys():
            if "/routes/" in route_path and route_path.split("/routes/")[1] != "index.js":
                resource = route_path.split("/routes/")[1].replace(".js", "")
                test_code = test_template.render(resource=resource)
                tests[f"tests/{resource}.test.js"] = test_code
        
        return tests
    
    def _generate_nestjs_tests(self) -> Dict[str, str]:
        """Generate tests for NestJS."""
        return {
            "test/app.e2e-spec.ts": '''import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication } from '@nestjs/common';
import * as request from 'supertest';
import { AppModule } from './../src/app.module';

describe('AppController (e2e)', () => {
  let app: INestApplication;

  beforeEach(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleFixture.createNestApplication();
    await app.init();
  });

  it('/ (GET)', () => {
    return request(app.getHttpServer())
      .get('/')
      .expect(200);
  });
});
'''
        }
