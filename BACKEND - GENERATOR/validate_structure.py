"""
Validation script to check all imports work correctly.
"""

import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

print("🔍 Validating Backend Agent Structure...")
print()

# Test basic imports
try:
    from backend_agent.config import BackendAgentConfig
    print("✓ Config module")
except Exception as e:
    print(f"✗ Config module: {e}")

try:
    from backend_agent.workflow.backend_workflow import create_backend_workflow
    print("✓ Workflow module")
except Exception as e:
    print(f"✗ Workflow module: {e}")

try:
    from backend_agent.api.cli import main
    print("✓ CLI module")
except Exception as e:
    print(f"✗ CLI module: {e}")

# Test analyzer imports
try:
    from backend_agent.analyzers.frontend_analyzer import FrontendAnalyzerAgent
    from backend_agent.analyzers.requirements_parser import RequirementsParserAgent
    from backend_agent.analyzers.stack_selector import StackSelectorAgent
    from backend_agent.analyzers.architecture_planner import ArchitecturePlannerAgent
    print("✓ Analyzer modules")
except Exception as e:
    print(f"✗ Analyzer modules: {e}")

# Test generator imports
try:
    from backend_agent.generators.database.schema_generator import SchemaGeneratorAgent
    from backend_agent.generators.database.migration_generator import MigrationGeneratorAgent
    from backend_agent.generators.database.orm_generator import ORMGeneratorAgent
    print("✓ Database generator modules")
except Exception as e:
    print(f"✗ Database generator modules: {e}")

try:
    from backend_agent.generators.api.route_generator import RouteGeneratorAgent
    from backend_agent.generators.api.controller_generator import ControllerGeneratorAgent
    from backend_agent.generators.api.validation_generator import ValidationGeneratorAgent
    print("✓ API generator modules")
except Exception as e:
    print(f"✗ API generator modules: {e}")

try:
    from backend_agent.generators.auth.jwt_generator import JWTGeneratorAgent
    print("✓ Auth generator modules")
except Exception as e:
    print(f"✗ Auth generator modules: {e}")

try:
    from backend_agent.generators.business_logic.service_generator import ServiceGeneratorAgent
    print("✓ Business logic generator modules")
except Exception as e:
    print(f"✗ Business logic generator modules: {e}")

try:
    from backend_agent.generators.testing.unit_test_generator import UnitTestGeneratorAgent
    print("✓ Testing generator modules")
except Exception as e:
    print(f"✗ Testing generator modules: {e}")

try:
    from backend_agent.generators.deployment.docker_generator import DockerGeneratorAgent
    from backend_agent.generators.deployment.cicd_generator import CICDGeneratorAgent
    print("✓ Deployment generator modules")
except Exception as e:
    print(f"✗ Deployment generator modules: {e}")

# Test integrator imports
try:
    from backend_agent.integrators.code_integrator import CodeIntegratorAgent
    from backend_agent.integrators.frontend_backend_linker import FrontendBackendLinkerAgent
    print("✓ Integrator modules")
except Exception as e:
    print(f"✗ Integrator modules: {e}")

print()
print("✅ Validation complete!")
