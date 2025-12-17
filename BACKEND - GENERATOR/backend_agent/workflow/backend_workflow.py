"""
Main LangGraph workflow for Backend Generation Agent.
Orchestrates all agents from frontend analysis to code generation.
"""

from typing import TypedDict, Annotated, List, Dict, Any, Optional, Literal
import operator
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from datetime import datetime

# Import all agents
from backend_agent.analyzers.frontend_analyzer import FrontendAnalyzerAgent
from backend_agent.analyzers.requirements_parser import RequirementsParserAgent
from backend_agent.analyzers.stack_selector import StackSelectorAgent
from backend_agent.analyzers.architecture_planner import ArchitecturePlannerAgent

from backend_agent.generators.database.schema_generator import SchemaGeneratorAgent
from backend_agent.generators.database.migration_generator import MigrationGeneratorAgent
from backend_agent.generators.database.orm_generator import ORMGeneratorAgent

from backend_agent.generators.api.route_generator import RouteGeneratorAgent
from backend_agent.generators.api.controller_generator import ControllerGeneratorAgent
from backend_agent.generators.api.validation_generator import ValidationGeneratorAgent

from backend_agent.generators.auth.jwt_generator import JWTGeneratorAgent
from backend_agent.generators.business_logic.service_generator import ServiceGeneratorAgent

from backend_agent.generators.integrations.ml_integration_generator import MLIntegrationGeneratorAgent
from backend_agent.generators.testing.unit_test_generator import UnitTestGeneratorAgent
from backend_agent.generators.deployment.docker_generator import DockerGeneratorAgent
from backend_agent.generators.deployment.cicd_generator import CICDGeneratorAgent

from backend_agent.integrators.code_integrator import CodeIntegratorAgent
from backend_agent.integrators.frontend_backend_linker import FrontendBackendLinkerAgent


# ==================== STATE DEFINITION ====================

class BackendAgentState(TypedDict):
    """Global state for backend generation workflow."""
    
    # ===== INPUT =====
    frontend_manifest: Dict[str, Any]  # From Frontend Scanner
    user_requirements: str  # Natural language prompt
    config: Dict[str, Any]  # BackendAgentConfig
    existing_backend: Optional[Dict[str, Any]]  # For incremental updates
    
    # ===== ANALYSIS OUTPUTS =====
    parsed_requirements: Dict[str, Any]  # Structured requirements
    required_endpoints: List[Dict[str, Any]]  # API endpoints needed
    data_models: List[Dict[str, Any]]  # Data entities
    selected_stack: Dict[str, str]  # Language, framework, database
    architecture_plan: Dict[str, Any]  # Monolith/microservices plan
    
    # ===== GENERATION OUTPUTS =====
    database_schema: Dict[str, Any]  # DB schema
    orm_models: Dict[str, str]  # ORM code files
    migrations: List[Dict[str, str]]  # Migration scripts
    api_routes: Dict[str, str]  # Route files
    controllers: Dict[str, str]  # Controller files
    validation_schemas: Dict[str, str]  # Validation code
    auth_system: Dict[str, str]  # Auth files
    services: Dict[str, str]  # Service layer
    tests: Dict[str, str]  # Test files
    docker_config: Dict[str, str]  # Dockerfile, docker-compose
    cicd_config: Dict[str, str]  # CI/CD pipeline files
    
    # ===== INTEGRATION =====
    integrated_code: Dict[str, str]  # Final organized code
    frontend_client: str  # API client for frontend
    documentation: str  # README, API docs
    
    # ===== METADATA =====
    project_structure: Dict[str, Any]  # Directory structure
    dependencies: Dict[str, List[str]]  # NPM/pip dependencies
    env_variables: Dict[str, str]  # Environment variables
    logs: Annotated[List[str], operator.add]
    errors: Annotated[List[str], operator.add]
    workflow_stage: str
    timestamp: str


# ==================== HELPER FUNCTIONS ====================

def log_step(state: BackendAgentState, message: str) -> BackendAgentState:
    """Add log entry with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    state["logs"].append(f"[{timestamp}] {message}")
    print(f"[{timestamp}] {message}")  # Also print to console
    return state


# ==================== STAGE 1: ANALYSIS ====================

def analyze_frontend(state: BackendAgentState) -> BackendAgentState:
    """
    NODE 1: Analyze Frontend Manifest
    - Parse frontend scanner output
    - Extract API calls, routes, data structures
    - Identify required endpoints
    """
    state = log_step(state, "🔍 STAGE 1.1: Analyzing frontend manifest...")
    
    agent = FrontendAnalyzerAgent()
    
    analysis = agent.analyze(state["frontend_manifest"])
    
    state["required_endpoints"] = analysis["endpoints"]
    state["data_models"] = analysis["data_models"]
    state["workflow_stage"] = "frontend_analysis_complete"
    
    state = log_step(state, f"✓ Found {len(analysis['endpoints'])} required endpoints")
    state = log_step(state, f"✓ Identified {len(analysis['data_models'])} data models")
    
    return state


def parse_requirements(state: BackendAgentState) -> BackendAgentState:
    """
    NODE 2: Parse User Requirements
    - Parse natural language requirements
    - Extract features, constraints, preferences
    """
    state = log_step(state, "📝 STAGE 1.2: Parsing user requirements...")
    
    agent = RequirementsParserAgent(state["config"]["llm"])
    
    parsed = agent.parse(state["user_requirements"])
    
    state["parsed_requirements"] = parsed
    state["workflow_stage"] = "requirements_parsing_complete"
    
    state = log_step(state, f"✓ Parsed {len(parsed['features'])} features")
    
    return state


def select_stack(state: BackendAgentState) -> BackendAgentState:
    """
    NODE 3: Select Tech Stack
    - Choose language (Node.js vs Python)
    - Select framework (Express, FastAPI, NestJS, Django)
    - Choose database (PostgreSQL, MongoDB, MySQL)
    - Select ORM (Sequelize, Prisma, SQLAlchemy, Mongoose)
    """
    state = log_step(state, "🎯 STAGE 1.3: Selecting optimal tech stack...")
    
    agent = StackSelectorAgent(state["config"]["llm"])
    
    selection = agent.select(
        frontend_manifest=state["frontend_manifest"],
        requirements=state["parsed_requirements"],
        config=state["config"]["stack"]
    )
    
    state["selected_stack"] = selection
    state["workflow_stage"] = "stack_selection_complete"
    
    state = log_step(state, f"✓ Selected: {selection['language']} + {selection['framework']} + {selection['database']}")
    
    return state


def plan_architecture(state: BackendAgentState) -> BackendAgentState:
    """
    NODE 4: Plan Architecture
    - Decide monolith vs microservices
    - Design project structure
    - Plan service boundaries
    """
    state = log_step(state, "🏗️ STAGE 1.4: Planning architecture...")
    
    agent = ArchitecturePlannerAgent(state["config"]["llm"])
    
    plan = agent.plan(
        requirements=state["parsed_requirements"],
        stack=state["selected_stack"],
        style=state["config"]["architecture"]["style"]
    )
    
    state["architecture_plan"] = plan
    state["project_structure"] = plan["structure"]
    state["workflow_stage"] = "architecture_planning_complete"
    
    state = log_step(state, f"✓ Architecture: {plan['style']}")
    
    return state


# ==================== STAGE 2: DATABASE GENERATION ====================

def generate_database_schema(state: BackendAgentState) -> BackendAgentState:
    """
    NODE 5: Generate Database Schema
    - Create DDL for tables
    - Define relationships
    - Add indexes and constraints
    """
    state = log_step(state, "🗄️ STAGE 2.1: Generating database schema...")
    
    agent = SchemaGeneratorAgent(
        database_type=state["selected_stack"]["database"],
        llm_config=state["config"]["llm"]
    )
    
    schema = agent.generate(state["data_models"])
    
    state["database_schema"] = schema
    state["workflow_stage"] = "database_schema_complete"
    
    state = log_step(state, f"✓ Generated schema with {len(schema['tables'])} tables")
    
    return state


def generate_orm_models(state: BackendAgentState) -> BackendAgentState:
    """
    NODE 6: Generate ORM Models
    - Generate SQLAlchemy/Sequelize/Prisma/Mongoose models
    - Add relationships and validations
    """
    state = log_step(state, "📦 STAGE 2.2: Generating ORM models...")
    
    agent = ORMGeneratorAgent(
        orm_type=state["selected_stack"]["orm"],
        llm_config=state["config"]["llm"]
    )
    
    models = agent.generate(
        schema=state["database_schema"],
        framework=state["selected_stack"]["framework"]
    )
    
    state["orm_models"] = models
    state["workflow_stage"] = "orm_generation_complete"
    
    state = log_step(state, f"✓ Generated {len(models)} ORM model files")
    
    return state


def generate_migrations(state: BackendAgentState) -> BackendAgentState:
    """
    NODE 7: Generate Migration Scripts
    - Create Alembic/Prisma/Sequelize migrations
    - Handle incremental updates
    """
    state = log_step(state, "🔄 STAGE 2.3: Generating migration scripts...")
    
    agent = MigrationGeneratorAgent(
        orm_type=state["selected_stack"]["orm"],
        database_type=state["selected_stack"]["database"]
    )
    
    # Safely get existing schema
    existing_backend = state.get("existing_backend") or {}
    existing_schema = existing_backend.get("schema") if isinstance(existing_backend, dict) else None
    
    migrations = agent.generate(
        schema=state["database_schema"],
        existing_schema=existing_schema
    )
    
    state["migrations"] = migrations
    state["workflow_stage"] = "migration_generation_complete"
    
    state = log_step(state, f"✓ Generated {len(migrations)} migration(s)")
    
    return state


# ==================== STAGE 3: API GENERATION ====================

def generate_routes(state: BackendAgentState) -> BackendAgentState:
    """
    NODE 8: Generate API Routes
    - Create Express/FastAPI route definitions
    - Map frontend endpoints to backend routes
    """
    state = log_step(state, "🛣️ STAGE 3.1: Generating API routes...")
    
    agent = RouteGeneratorAgent(
        framework=state["selected_stack"]["framework"],
        llm_config=state["config"]["llm"]
    )
    
    routes = agent.generate(
        endpoints=state["required_endpoints"],
        architecture=state["architecture_plan"]
    )
    
    state["api_routes"] = routes
    state["workflow_stage"] = "route_generation_complete"
    
    state = log_step(state, f"✓ Generated {len(routes)} route files")
    
    return state


def generate_controllers(state: BackendAgentState) -> BackendAgentState:
    """
    NODE 9: Generate Controllers
    - Create CRUD controller logic
    - Implement business logic placeholders
    """
    state = log_step(state, "🎮 STAGE 3.2: Generating controllers...")
    
    agent = ControllerGeneratorAgent(
        framework=state["selected_stack"]["framework"],
        llm_config=state["config"]["llm"]
    )
    
    controllers = agent.generate(
        routes=state["api_routes"],
        models=state["orm_models"],
        requirements=state["parsed_requirements"]
    )
    
    state["controllers"] = controllers
    state["workflow_stage"] = "controller_generation_complete"
    
    state = log_step(state, f"✓ Generated {len(controllers)} controller files")
    
    return state


def generate_validation(state: BackendAgentState) -> BackendAgentState:
    """
    NODE 10: Generate Validation Schemas
    - Create Pydantic/Joi validation schemas
    - Add input sanitization
    """
    state = log_step(state, "✅ STAGE 3.3: Generating validation schemas...")
    
    agent = ValidationGeneratorAgent(
        framework=state["selected_stack"]["framework"],
        llm_config=state["config"]["llm"]
    )
    
    validation = agent.generate(
        data_models=state["data_models"],
        endpoints=state["required_endpoints"]
    )
    
    state["validation_schemas"] = validation
    state["workflow_stage"] = "validation_generation_complete"
    
    state = log_step(state, f"✓ Generated {len(validation)} validation schemas")
    
    return state


# ==================== STAGE 4: AUTH & SECURITY ====================

def generate_auth_system(state: BackendAgentState) -> BackendAgentState:
    """
    NODE 11: Generate Authentication System
    - Create JWT/OAuth2/Session auth
    - Generate login/register endpoints
    - Add auth middleware
    """
    if not state["config"]["auth"]["enabled"]:
        state = log_step(state, "⏭️ STAGE 4: Skipping auth (disabled in config)")
        state["auth_system"] = {}
        return state
    
    state = log_step(state, "🔐 STAGE 4: Generating authentication system...")
    
    agent = JWTGeneratorAgent(
        framework=state["selected_stack"]["framework"],
        method=state["config"]["auth"]["method"],
        llm_config=state["config"]["llm"]
    )
    
    auth_system = agent.generate(
        user_model=next((m for m in state["data_models"] if m["name"].lower() == "user"), None)
    )
    
    state["auth_system"] = auth_system
    state["workflow_stage"] = "auth_generation_complete"
    
    state = log_step(state, f"✓ Generated {state['config']['auth']['method'].upper()} authentication system")
    
    return state


# ==================== STAGE 5: BUSINESS LOGIC ====================

def generate_services(state: BackendAgentState) -> BackendAgentState:
    """
    NODE 12: Generate Service Layer
    - Create service classes
    - Implement repository pattern
    - Add transaction management
    """
    state = log_step(state, "⚙️ STAGE 5: Generating service layer...")
    
    agent = ServiceGeneratorAgent(
        framework=state["selected_stack"]["framework"],
        llm_config=state["config"]["llm"]
    )
    
    # Safely get business rules
    parsed_reqs = state.get("parsed_requirements") or {}
    business_logic = parsed_reqs.get("business_rules", []) if isinstance(parsed_reqs, dict) else []
    
    services = agent.generate(
        models=state["orm_models"],
        controllers=state["controllers"],
        business_logic=business_logic
    )
    
    state["services"] = services
    state["workflow_stage"] = "service_generation_complete"
    
    state = log_step(state, f"✓ Generated {len(services)} service files")
    
    return state


# ==================== STAGE 6: INTEGRATIONS ====================

def generate_ml_integration(state: BackendAgentState) -> BackendAgentState:
    """
    NODE 13: Generate ML Integration (if needed)
    - Create ML model endpoints
    - Add prediction/inference logic
    """
    if not state["config"]["features"]["ml_integration"]:
        state = log_step(state, "⏭️ STAGE 6.1: Skipping ML integration (disabled)")
        return state
    
    state = log_step(state, "🤖 STAGE 6.1: Generating ML integration...")
    
    agent = MLIntegrationGeneratorAgent(
        framework=state["selected_stack"]["framework"],
        llm_config=state["config"]["llm"]
    )
    
    # Safely get ML features
    parsed_reqs = state.get("parsed_requirements") or {}
    ml_features = parsed_reqs.get("ml_features", []) if isinstance(parsed_reqs, dict) else []
    
    ml_code = agent.generate(ml_features)
    
    # Merge ML code into services
    state["services"].update(ml_code)
    state["workflow_stage"] = "ml_integration_complete"
    
    state = log_step(state, "✓ Generated ML integration endpoints")
    
    return state


# ==================== STAGE 7: TESTING ====================

def generate_tests(state: BackendAgentState) -> BackendAgentState:
    """
    NODE 14: Generate Test Suites
    - Create unit tests
    - Generate integration tests
    """
    if not state["config"]["generation"]["include_tests"]:
        state = log_step(state, "⏭️ STAGE 7: Skipping test generation (disabled)")
        state["tests"] = {}
        return state
    
    state = log_step(state, "🧪 STAGE 7: Generating test suites...")
    
    agent = UnitTestGeneratorAgent(
        framework=state["selected_stack"]["framework"],
        llm_config=state["config"]["llm"]
    )
    
    tests = agent.generate(
        routes=state["api_routes"],
        controllers=state["controllers"],
        services=state["services"]
    )
    
    state["tests"] = tests
    state["workflow_stage"] = "test_generation_complete"
    
    state = log_step(state, f"✓ Generated {len(tests)} test files")
    
    return state


# ==================== STAGE 8: DEPLOYMENT ====================

def generate_docker_config(state: BackendAgentState) -> BackendAgentState:
    """
    NODE 15: Generate Docker Configuration
    - Create Dockerfile
    - Generate docker-compose.yml
    """
    if not state["config"]["deployment"]["docker"]:
        state = log_step(state, "⏭️ STAGE 8.1: Skipping Docker (disabled)")
        state["docker_config"] = {}
        return state
    
    state = log_step(state, "🐳 STAGE 8.1: Generating Docker configuration...")
    
    agent = DockerGeneratorAgent(
        stack=state["selected_stack"]
    )
    
    docker_config = agent.generate(
        project_structure=state["project_structure"],
        dependencies=state["dependencies"]
    )
    
    state["docker_config"] = docker_config
    state["workflow_stage"] = "docker_generation_complete"
    
    state = log_step(state, "✓ Generated Dockerfile and docker-compose.yml")
    
    return state


def generate_cicd(state: BackendAgentState) -> BackendAgentState:
    """
    NODE 16: Generate CI/CD Pipeline
    - Create GitHub Actions / GitLab CI config
    - Add build, test, deploy steps
    """
    if state["config"]["deployment"]["ci_cd"] == "none":
        state = log_step(state, "⏭️ STAGE 8.2: Skipping CI/CD (disabled)")
        state["cicd_config"] = {}
        return state
    
    state = log_step(state, f"🚀 STAGE 8.2: Generating CI/CD pipeline ({state['config']['deployment']['ci_cd']})...")
    
    agent = CICDGeneratorAgent(
        ci_system=state["config"]["deployment"]["ci_cd"],
        stack=state["selected_stack"]
    )
    
    cicd_config = agent.generate(
        tests_available=bool(state["tests"]),
        docker_enabled=state["config"]["deployment"]["docker"]
    )
    
    state["cicd_config"] = cicd_config
    state["workflow_stage"] = "cicd_generation_complete"
    
    state = log_step(state, "✓ Generated CI/CD pipeline")
    
    return state


# ==================== STAGE 9: INTEGRATION ====================

def integrate_code(state: BackendAgentState) -> BackendAgentState:
    """
    NODE 17: Integrate All Code
    - Combine all generated files
    - Organize into project structure
    - Resolve dependencies
    """
    state = log_step(state, "🔗 STAGE 9.1: Integrating all code...")
    
    agent = CodeIntegratorAgent(
        framework=state["selected_stack"]["framework"]
    )
    
    integrated = agent.integrate(
        orm_models=state["orm_models"],
        routes=state["api_routes"],
        controllers=state["controllers"],
        services=state["services"],
        auth=state["auth_system"],
        validation=state["validation_schemas"],
        tests=state["tests"],
        migrations=state["migrations"],
        docker=state["docker_config"],
        cicd=state["cicd_config"],
        structure=state["project_structure"]
    )
    
    state["integrated_code"] = integrated["files"]
    state["dependencies"] = integrated["dependencies"]
    state["env_variables"] = integrated["env_vars"]
    state["workflow_stage"] = "code_integration_complete"
    
    state = log_step(state, f"✓ Integrated {len(integrated['files'])} files")
    
    return state


def link_frontend_backend(state: BackendAgentState) -> BackendAgentState:
    """
    NODE 18: Link Frontend & Backend
    - Generate API client for frontend
    - Create TypeScript types
    - Generate .env for frontend
    """
    state = log_step(state, "🔗 STAGE 9.2: Linking frontend and backend...")
    
    agent = FrontendBackendLinkerAgent(
        framework=state["selected_stack"]["framework"]
    )
    
    linker_output = agent.link(
        frontend_manifest=state["frontend_manifest"],
        backend_endpoints=state["required_endpoints"],
        auth_config=state["config"]["auth"]
    )
    
    state["frontend_client"] = linker_output["api_client"]
    state["documentation"] = linker_output["documentation"]
    
    # Add frontend integration files to integrated code
    state["integrated_code"]["frontend_client.ts"] = linker_output["api_client"]
    state["integrated_code"]["README.md"] = linker_output["documentation"]
    
    state["workflow_stage"] = "frontend_backend_linking_complete"
    
    state = log_step(state, "✓ Generated frontend API client")
    
    return state


# ==================== FINAL NODE ====================

def finalize_backend(state: BackendAgentState) -> BackendAgentState:
    """
    NODE 19: Finalize & Export
    - Write all files to disk
    - Format code
    - Generate final documentation
    """
    state = log_step(state, "📦 STAGE 10: Finalizing backend generation...")
    
    from backend_agent.utils.file_utils import write_files
    from backend_agent.utils.code_formatter import format_code
    
    output_dir = state["config"]["project"]["output_dir"]
    
    # Format all code
    formatted_code = {}
    for filepath, content in state["integrated_code"].items():
        formatted = format_code(content, filepath, state["config"]["generation"]["code_style"])
        formatted_code[filepath] = formatted
    
    # Write files
    write_files(output_dir, formatted_code)
    
    # Write dependencies
    if state["selected_stack"]["language"] == "node":
        write_files(output_dir, {"package.json": state["dependencies"]["package_json"]})
    else:
        write_files(output_dir, {"requirements.txt": "\n".join(state["dependencies"]["pip"])})
    
    # Write .env.example
    env_content = "\n".join([f"{k}={v}" for k, v in state["env_variables"].items()])
    write_files(output_dir, {".env.example": env_content})
    
    state["workflow_stage"] = "complete"
    state["timestamp"] = datetime.now().isoformat()
    
    state = log_step(state, f"✅ Backend generation complete! Output: {output_dir}")
    
    return state


# ==================== BUILD WORKFLOW ====================

def create_backend_workflow():
    """Create and compile the backend generation workflow."""
    
    workflow = StateGraph(BackendAgentState)
    
    # ===== ADD NODES =====
    
    # Stage 1: Analysis
    workflow.add_node("analyze_frontend", analyze_frontend)
    workflow.add_node("parse_requirements", parse_requirements)
    workflow.add_node("select_stack", select_stack)
    workflow.add_node("plan_architecture", plan_architecture)
    
    # Stage 2: Database
    workflow.add_node("generate_database_schema", generate_database_schema)
    workflow.add_node("generate_orm_models", generate_orm_models)
    workflow.add_node("generate_migrations", generate_migrations)
    
    # Stage 3: API
    workflow.add_node("generate_routes", generate_routes)
    workflow.add_node("generate_controllers", generate_controllers)
    workflow.add_node("generate_validation", generate_validation)
    
    # Stage 4: Auth
    workflow.add_node("generate_auth_system", generate_auth_system)
    
    # Stage 5: Business Logic
    workflow.add_node("generate_services", generate_services)
    
    # Stage 6: Integrations
    workflow.add_node("generate_ml_integration", generate_ml_integration)
    
    # Stage 7: Testing
    workflow.add_node("generate_tests", generate_tests)
    
    # Stage 8: Deployment
    workflow.add_node("generate_docker_config", generate_docker_config)
    workflow.add_node("generate_cicd", generate_cicd)
    
    # Stage 9: Integration
    workflow.add_node("integrate_code", integrate_code)
    workflow.add_node("link_frontend_backend", link_frontend_backend)
    
    # Final
    workflow.add_node("finalize_backend", finalize_backend)
    
    # ===== ADD EDGES =====
    
    # Analysis flow
    workflow.add_edge(START, "analyze_frontend")
    workflow.add_edge("analyze_frontend", "parse_requirements")
    workflow.add_edge("parse_requirements", "select_stack")
    workflow.add_edge("select_stack", "plan_architecture")
    
    # Database generation
    workflow.add_edge("plan_architecture", "generate_database_schema")
    workflow.add_edge("generate_database_schema", "generate_orm_models")
    workflow.add_edge("generate_orm_models", "generate_migrations")
    
    # API generation
    workflow.add_edge("generate_migrations", "generate_routes")
    workflow.add_edge("generate_routes", "generate_controllers")
    workflow.add_edge("generate_controllers", "generate_validation")
    
    # Auth
    workflow.add_edge("generate_validation", "generate_auth_system")
    
    # Business logic
    workflow.add_edge("generate_auth_system", "generate_services")
    
    # Integrations
    workflow.add_edge("generate_services", "generate_ml_integration")
    
    # Testing
    workflow.add_edge("generate_ml_integration", "generate_tests")
    
    # Deployment
    workflow.add_edge("generate_tests", "generate_docker_config")
    workflow.add_edge("generate_docker_config", "generate_cicd")
    
    # Integration
    workflow.add_edge("generate_cicd", "integrate_code")
    workflow.add_edge("integrate_code", "link_frontend_backend")
    
    # Final
    workflow.add_edge("link_frontend_backend", "finalize_backend")
    workflow.add_edge("finalize_backend", END)
    
    # ===== COMPILE =====
    
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    return app


# ==================== USAGE ====================

if __name__ == "__main__":
    import json
    from pathlib import Path
    
    # Load frontend manifest
    manifest_path = Path("scan-output/manifest.json")
    if manifest_path.exists():
        with open(manifest_path) as f:
            frontend_manifest = json.load(f)
    else:
        frontend_manifest = {
            "routes": ["/", "/about"],
            "api_calls": ["GET /api/users", "POST /api/posts"],
            "components": []
        }
    
    # Create workflow
    workflow = create_backend_workflow()
    
    # Initial state
    from backend_agent.config import BackendAgentConfig
    config = BackendAgentConfig()
    
    initial_state = {
        "frontend_manifest": frontend_manifest,
        "user_requirements": "Create a blog backend with user authentication and CRUD for posts",
        "config": config.model_dump(),
        "existing_backend": None,
        "parsed_requirements": {},
        "required_endpoints": [],
        "data_models": [],
        "selected_stack": {},
        "architecture_plan": {},
        "database_schema": {},
        "orm_models": {},
        "migrations": [],
        "api_routes": {},
        "controllers": {},
        "validation_schemas": {},
        "auth_system": {},
        "services": {},
        "tests": {},
        "docker_config": {},
        "cicd_config": {},
        "integrated_code": {},
        "frontend_client": "",
        "documentation": "",
        "project_structure": {},
        "dependencies": {},
        "env_variables": {},
        "logs": [],
        "errors": [],
        "workflow_stage": "initialized",
        "timestamp": ""
    }
    
    # Execute
    result = workflow.invoke(initial_state)
    
    print("\n" + "="*60)
    print("✅ BACKEND GENERATION COMPLETE")
    print("="*60)
    print(f"Output: {result['config']['project']['output_dir']}")
    print(f"Framework: {result['selected_stack']['framework']}")
    print(f"Database: {result['selected_stack']['database']}")
    print(f"Files generated: {len(result['integrated_code'])}")
