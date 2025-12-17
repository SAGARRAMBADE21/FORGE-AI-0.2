# Backend Generator Agent

AI-powered backend code generation system that creates production-ready backend code based on uploaded frontend projects and user prompts.

## Features

- **Frontend Analysis**: Analyzes scanned frontend code to understand API requirements
- **Smart Stack Selection**: Automatically selects optimal tech stack (Node.js/Python, Express/FastAPI/NestJS, etc.)
- **Complete Code Generation**:
  - Database schemas and ORM models
  - API routes and controllers
  - Authentication and authorization
  - Business logic and services
  - Input validation
  - Unit and integration tests
  - Docker configuration
  - CI/CD pipelines
- **Frontend-Backend Integration**: Generates API clients for seamless frontend integration

## Installation

```bash
cd "BACKEND - GENERATOR"
pip install -r requirements.txt
```

Or install in development mode:

```bash
pip install -e .
```

## Configuration

Create a `.env` file with your API keys:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

Customize settings in `backend-config.yaml`:

```yaml
project:
  name: "my-backend"
  output_dir: "./generated-backend"

stack:
  language: "auto"  # auto, node, python
  framework: "auto"  # auto, express, fastapi, nestjs, django
  database: "auto"  # auto, postgresql, mysql, mongodb, sqlite

architecture:
  style: "monolith"  # monolith, microservices
  api_style: "rest"  # rest, graphql, both

auth:
  enabled: true
  method: "jwt"  # jwt, oauth2, session

generation:
  include_tests: true
  include_docs: true
  
deployment:
  docker: true
  ci_cd: "github_actions"
```

## Usage

### Command Line

```bash
# Generate backend from frontend manifest
python run_backend_agent.py generate \
  --frontend-manifest ../scanner_output/manifest.json \
  --requirements "Create a REST API for e-commerce with product catalog, shopping cart, and user authentication" \
  --output ./my-backend

# With custom configuration
python run_backend_agent.py generate \
  -f ../scanner_output/manifest.json \
  -r "Build a blog API with posts, comments, and categories" \
  -c backend-config.yaml \
  -o ./blog-backend
```

### Python API

```python
from backend_agent import create_backend_workflow
from backend_agent.config import BackendAgentConfig
import json

# Load frontend manifest
with open("../scanner_output/manifest.json") as f:
    frontend_manifest = json.load(f)

# Configure
config = BackendAgentConfig(
    project={"name": "my-backend"},
    stack={"language": "python", "framework": "fastapi"},
    database={"migrations": True}
)

# Create workflow
workflow = create_backend_workflow(config)

# Generate backend
initial_state = {
    "frontend_manifest": frontend_manifest,
    "user_requirements": "Create a REST API with user authentication",
    "config": config.model_dump(),
    "logs": [],
    "errors": []
}

result = workflow.invoke(initial_state)

# Access generated code
print(result["integrated_code"])
print(result["documentation"])
```

## Project Structure

```
backend_agent/
├── analyzers/          # Frontend analysis and requirement parsing
│   ├── frontend_analyzer.py
│   ├── requirements_parser.py
│   ├── stack_selector.py
│   └── architecture_planner.py
├── generators/         # Code generation agents
│   ├── api/           # Routes, controllers, validation
│   ├── auth/          # JWT, OAuth, middleware
│   ├── business_logic/ # Services, repositories
│   ├── database/      # Schemas, ORM, migrations
│   ├── deployment/    # Docker, CI/CD
│   ├── integrations/  # ML, external APIs, messaging
│   └── testing/       # Unit and integration tests
├── integrators/       # Code integration and linking
│   ├── code_integrator.py
│   └── frontend_backend_linker.py
├── storage/           # Code and metadata storage
├── workflow/          # LangGraph workflow orchestration
└── api/              # CLI and REST API

```

## Workflow

1. **Analysis Phase**
   - Parse frontend manifest
   - Extract API requirements from frontend code
   - Parse user requirements
   - Select optimal tech stack
   - Plan architecture

2. **Generation Phase**
   - Generate database schema
   - Create ORM models
   - Build API routes and controllers
   - Implement authentication
   - Create business logic
   - Generate tests
   - Setup deployment configs

3. **Integration Phase**
   - Integrate all generated code
   - Create frontend API client
   - Generate documentation
   - Organize project structure

## Generated Output

The tool generates a complete, production-ready backend project:

```
generated-backend/
├── src/
│   ├── models/        # Database models
│   ├── routes/        # API routes
│   ├── controllers/   # Request handlers
│   ├── services/      # Business logic
│   ├── middleware/    # Auth, validation
│   └── config/        # Configuration
├── tests/
│   ├── unit/
│   └── integration/
├── migrations/        # Database migrations
├── Dockerfile
├── docker-compose.yml
├── .github/workflows/ # CI/CD
├── package.json       # or requirements.txt
├── README.md
└── .env.example
```

## Advanced Features

### Incremental Updates

Update existing backend code:

```python
result = workflow.invoke({
    "frontend_manifest": new_manifest,
    "user_requirements": "Add payment integration",
    "existing_backend": existing_code,
    "config": config.model_dump()
})
```

### Custom Stack

```bash
python run_backend_agent.py generate \
  --frontend-manifest manifest.json \
  --language python \
  --framework fastapi \
  --database postgresql \
  --requirements "Build API with caching and rate limiting"
```

## Requirements

- Python 3.10+
- OpenAI API key (or compatible LLM provider)
- Frontend Scanner output (manifest.json)

## Development

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Format code
black backend_agent/
isort backend_agent/
```

## License

MIT

## Support

For issues or questions, please open an issue on GitHub.
