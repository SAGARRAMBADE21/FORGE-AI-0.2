"""
Frontend-Backend Linker Agent
Generates API client for frontend integration.
"""

from typing import Dict, Any, List
from jinja2 import Template


class FrontendBackendLinkerAgent:
    """Links frontend and backend."""
    
    def __init__(self, framework: str):
        self.framework = framework
    
    def link(self, 
             frontend_manifest: Dict[str, Any],
             backend_endpoints: List[Dict[str, Any]],
             auth_config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate frontend API client."""
        
        api_client = self._generate_api_client(backend_endpoints, auth_config)
        documentation = self._generate_documentation(backend_endpoints)
        
        return {
            "api_client": api_client,
            "documentation": documentation
        }
    
    def _generate_api_client(self, endpoints: List[Dict[str, Any]], 
                            auth_config: Dict[str, Any]) -> str:
        """Generate TypeScript API client."""
        
        template = Template('''/**
 * Auto-generated API Client
 * Generated on: {{ timestamp }}
 */

import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';

const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor for auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('authToken');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response.data,
      (error) => {
        if (error.response?.status === 401) {
          // Handle unauthorized
          localStorage.removeItem('authToken');
          window.location.href = '/login';
        }
        return Promise.reject(error.response?.data || error.message);
      }
    );
  }

{% for resource in resources %}
  // {{ resource.name | capitalize }} API
  async get{{ resource.name | capitalize }}s() {
    return this.client.get('/{{ resource.name }}');
  }

  async get{{ resource.name | capitalize }}(id: number) {
    return this.client.get(`/{{ resource.name }}/${id}`);
  }

  async create{{ resource.name | capitalize }}(data: any) {
    return this.client.post('/{{ resource.name }}', data);
  }

  async update{{ resource.name | capitalize }}(id: number, data: any) {
    return this.client.put(`/{{ resource.name }}/${id}`, data);
  }

  async delete{{ resource.name | capitalize }}(id: number) {
    return this.client.delete(`/{{ resource.name }}/${id}`);
  }

{% endfor %}
  // Authentication API
  async register(username: string, email: string, password: string) {
    const response = await this.client.post('/auth/register', {
      username,
      email,
      password,
    });
    if (response.token) {
      localStorage.setItem('authToken', response.token);
    }
    return response;
  }

  async login(email: string, password: string) {
    const response = await this.client.post('/auth/login', {
      username: email,  // FastAPI OAuth2 uses username field
      password,
    });
    if (response.access_token) {
      localStorage.setItem('authToken', response.access_token);
    }
    return response;
  }

  async logout() {
    localStorage.removeItem('authToken');
    return { message: 'Logged out successfully' };
  }

  async getCurrentUser() {
    return this.client.get('/auth/me');
  }
}

export const apiClient = new APIClient();
export default apiClient;
''')
        
        # Extract unique resources
        resources = []
        seen = set()
        for endpoint in endpoints:
            resource = endpoint["resource"]
            if resource not in seen:
                resources.append({"name": resource})
                seen.add(resource)
        
        from datetime import datetime
        client_code = template.render(
            resources=resources,
            timestamp=datetime.now().isoformat()
        )
        
        return client_code
    
    def _generate_documentation(self, endpoints: List[Dict[str, Any]]) -> str:
        """Generate API documentation."""
        
        doc = """# Backend API Documentation

## Base URL
`http://localhost:3000/api`

## Endpoints

"""
        
        for endpoint in endpoints:
            method = endpoint.get('method', 'GET')
            path = endpoint.get('path', '/')
            description = endpoint.get('description', 'No description')
            request_example = endpoint.get('request_example', '{}')
            response_example = endpoint.get('response_example', '{}')
            
            doc += f"""### {method} {path}
{description}

**Request:**
```json
{request_example}
```

**Response:**
```json
{response_example}
```

---

"""
        
        return doc
