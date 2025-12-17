"""
CI/CD Generator Agent
Generates CI/CD pipeline configurations.
"""

from typing import Dict, Any


class CICDGeneratorAgent:
    """Generates CI/CD pipeline configurations."""
    
    def __init__(self, ci_system: str, stack: Dict[str, str]):
        self.ci_system = ci_system
        self.stack = stack
    
    def generate(self, tests_available: bool, docker_enabled: bool) -> Dict[str, str]:
        """Generate CI/CD configuration."""
        
        if self.ci_system == "github_actions":
            return self._generate_github_actions(tests_available, docker_enabled)
        elif self.ci_system == "gitlab_ci":
            return self._generate_gitlab_ci(tests_available, docker_enabled)
        elif self.ci_system == "jenkins":
            return self._generate_jenkins(tests_available, docker_enabled)
        else:
            return {}
    
    def _generate_github_actions(self, tests_available: bool, docker_enabled: bool) -> Dict[str, str]:
        """Generate GitHub Actions workflow."""
        
        if self.stack["language"] == "node":
            workflow = '''name: Node.js CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        node-version: [18.x, 20.x]
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Use Node.js ${{ matrix.node-version }}
      uses: actions/setup-node@v3
      with:
        node-version: ${{ matrix.node-version }}
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Run linter
      run: npm run lint
    
    - name: Run tests
      run: npm test
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
        JWT_SECRET: test-secret
    
    - name: Build
      run: npm run build --if-present

  docker:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to Docker Hub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}
    
    - name: Build and push
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: |
          ${{ secrets.DOCKER_USERNAME }}/app:latest
          ${{ secrets.DOCKER_USERNAME }}/app:${{ github.sha }}
        cache-from: type=registry,ref=${{ secrets.DOCKER_USERNAME }}/app:latest
        cache-to: type=inline

  deploy:
    needs: docker
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    steps:
    - name: Deploy to production
      run: |
        echo "Add deployment steps here"
        # Example: SSH to server and pull new image
        # ssh user@server 'cd /app && docker-compose pull && docker-compose up -d'
'''
        else:  # Python
            workflow = '''name: Python CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
        cache: 'pip'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Lint with flake8
      run: |
        flake8 app --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 app --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
    
    - name: Format check with black
      run: black --check app
    
    - name: Type check with mypy
      run: mypy app --ignore-missing-imports
    
    - name: Run tests with pytest
      run: pytest --cov=app --cov-report=xml
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
        SECRET_KEY: test-secret
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  docker:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to Docker Hub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}
    
    - name: Build and push
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: |
          ${{ secrets.DOCKER_USERNAME }}/app:latest
          ${{ secrets.DOCKER_USERNAME }}/app:${{ github.sha }}
        cache-from: type=registry,ref=${{ secrets.DOCKER_USERNAME }}/app:latest
        cache-to: type=inline

  deploy:
    needs: docker
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    steps:
    - name: Deploy to production
      run: |
        echo "Add deployment steps here"
        # Example: Deploy to cloud provider
'''
        
        return {".github/workflows/ci-cd.yml": workflow}
    
    def _generate_gitlab_ci(self, tests_available: bool, docker_enabled: bool) -> Dict[str, str]:
        """Generate GitLab CI configuration."""
        
        gitlab_ci = '''stages:
  - test
  - build
  - deploy

variables:
  DOCKER_DRIVER: overlay2
  DOCKER_TLS_CERTDIR: "/certs"

test:
  stage: test
  image: python:3.11
  services:
    - postgres:15
  variables:
    POSTGRES_DB: test_db
    POSTGRES_USER: postgres
    POSTGRES_PASSWORD: postgres
    DATABASE_URL: postgresql://postgres:postgres@postgres:5432/test_db
  before_script:
    - pip install -r requirements.txt
    - pip install -r requirements-dev.txt
  script:
    - black --check app
    - flake8 app
    - pytest --cov=app
  coverage: '/TOTAL.*\\s+(\\d+%)$/'

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  only:
    - main
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - docker build -t $CI_REGISTRY_IMAGE:latest .
    - docker push $CI_REGISTRY_IMAGE:latest

deploy:
  stage: deploy
  only:
    - main
  script:
    - echo "Deploy to production"
'''
        
        return {".gitlab-ci.yml": gitlab_ci}
    
    def _generate_jenkins(self, tests_available: bool, docker_enabled: bool) -> Dict[str, str]:
        """Generate Jenkinsfile."""
        
        jenkinsfile = '''pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = "myapp"
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Test') {
            steps {
                sh 'pip install -r requirements.txt'
                sh 'pytest --cov=app'
            }
        }
        
        stage('Build') {
            when {
                branch 'main'
            }
            steps {
                sh 'docker build -t ${DOCKER_IMAGE}:${BUILD_NUMBER} .'
                sh 'docker tag ${DOCKER_IMAGE}:${BUILD_NUMBER} ${DOCKER_IMAGE}:latest'
            }
        }
        
        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                sh 'docker-compose up -d'
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
    }
}
'''
        
        return {"Jenkinsfile": jenkinsfile}
