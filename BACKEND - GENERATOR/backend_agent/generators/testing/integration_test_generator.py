"""
Integration Test Generator Agent
Generates integration tests for complete API flows.
"""

from typing import Dict, Any


class IntegrationTestGeneratorAgent:
    """Generates integration tests."""
    
    def __init__(self, framework: str):
        self.framework = framework
    
    def generate(self) -> Dict[str, str]:
        """Generate integration tests."""
        
        if self.framework == "fastapi":
            return {
                "tests/test_integration.py": '''"""Integration tests."""

import pytest
from fastapi import status


def test_complete_user_flow(client):
    """Test complete user registration and authentication flow."""
    # Register
    register_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123"
    }
    register_response = client.post("/api/auth/register", json=register_data)
    assert register_response.status_code == status.HTTP_201_CREATED
    
    # Login
    login_data = {
        "username": "test@example.com",
        "password": "testpassword123"
    }
    login_response = client.post("/api/auth/login", data=login_data)
    assert login_response.status_code == status.HTTP_200_OK
    token = login_response.json()["access_token"]
    
    # Access protected endpoint
    headers = {"Authorization": f"Bearer {token}"}
    me_response = client.get("/api/auth/me", headers=headers)
    assert me_response.status_code == status.HTTP_200_OK
    assert me_response.json()["email"] == "test@example.com"
'''
            }
        
        else:  # Express
            return {
                "tests/integration.test.js": '''const request = require('supertest');
const app = require('../src/app');

describe('Integration Tests', () => {
  let authToken;

  it('should complete user registration and authentication flow', async () => {
    // Register
    const registerData = {
      username: 'testuser',
      email: 'test@example.com',
      password: 'testpassword123'
    };
    
    const registerResponse = await request(app)
      .post('/api/auth/register')
      .send(registerData)
      .expect(201);
    
    expect(registerResponse.body.user.email).toBe(registerData.email);
    
    // Login
    const loginData = {
      email: 'test@example.com',
      password: 'testpassword123'
    };
    
    const loginResponse = await request(app)
      .post('/api/auth/login')
      .send(loginData)
      .expect(200);
    
    authToken = loginResponse.body.token;
    expect(authToken).toBeDefined();
    
    // Access protected route
    const meResponse = await request(app)
      .get('/api/auth/me')
      .set('Authorization', `Bearer ${authToken}`)
      .expect(200);
    
    expect(meResponse.body.user.email).toBe('test@example.com');
  });
});
'''
            }
