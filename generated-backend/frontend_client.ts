/**
 * Auto-generated API Client
 * Generated on: 2025-12-13T16:33:58.811400
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