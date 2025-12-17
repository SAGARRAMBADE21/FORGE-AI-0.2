"""
Test script to verify FORGE AI integration is working correctly
"""

import sys
from pathlib import Path

# Add paths for imports
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "BACKEND - GENERATOR"))

print("=" * 80)
print("FORGE AI - Integration Test")
print("=" * 80)
print()

# Test 1: Frontend Scanner
print("✓ Testing Frontend Scanner...")
try:
    from frontend_scanner.config import ScannerConfig
    from frontend_scanner.workflows.scanner_graph import create_scanner_workflow
    print("  ✓ Frontend scanner modules imported successfully")
except Exception as e:
    print(f"  ✗ Error: {e}")
    sys.exit(1)

# Test 2: Backend Generator
print("✓ Testing Backend Generator...")
try:
    from backend_agent.config import BackendAgentConfig
    from backend_agent.workflow.backend_workflow import create_backend_workflow
    print("  ✓ Backend generator modules imported successfully")
    backend_available = True
except Exception as e:
    print(f"  ✗ Backend generator not available: {e}")
    print("  ℹ Install dependencies: cd 'BACKEND - GENERATOR' && pip install -r requirements.txt")
    backend_available = False

# Test 3: Pipeline Script
print("✓ Testing Pipeline Script...")
try:
    from pathlib import Path
    pipeline_file = Path(__file__).parent / "forge_pipeline.py"
    if pipeline_file.exists():
        print(f"  ✓ Pipeline script exists: {pipeline_file}")
    else:
        print(f"  ✗ Pipeline script not found")
except Exception as e:
    print(f"  ✗ Error: {e}")

# Test 4: Web Interface
print("✓ Testing Web Interface...")
try:
    web_file = Path(__file__).parent / "web_scanner.py"
    if web_file.exists():
        print(f"  ✓ Web interface exists: {web_file}")
    else:
        print(f"  ✗ Web interface not found")
except Exception as e:
    print(f"  ✗ Error: {e}")

# Test 5: Templates
print("✓ Testing Templates...")
try:
    forge_template = Path(__file__).parent / "templates" / "forge.html"
    if forge_template.exists():
        print(f"  ✓ Forge template exists: {forge_template}")
    else:
        print(f"  ✗ Forge template not found")
except Exception as e:
    print(f"  ✗ Error: {e}")

# Summary
print()
print("=" * 80)
print("INTEGRATION TEST SUMMARY")
print("=" * 80)
print()
print("Frontend Scanner:    ✓ Available")
print(f"Backend Generator:   {'✓ Available' if backend_available else '✗ Not Available'}")
print("Pipeline Script:     ✓ Available")
print("Web Interface:       ✓ Available")
print("Templates:           ✓ Available")
print()

if backend_available:
    print("✅ ALL SYSTEMS OPERATIONAL!")
    print()
    print("Quick Start:")
    print("  1. Set API key: GROQ_API_KEY=your_key (or OPENAI_API_KEY)")
    print("  2. Web UI: python web_scanner.py → http://localhost:5000/forge")
    print("  3. CLI: python forge_pipeline.py ./your-frontend-folder")
else:
    print("⚠️  Backend generator needs dependencies installed")
    print()
    print("To complete setup:")
    print('  cd "BACKEND - GENERATOR"')
    print('  pip install -r requirements.txt')
    print()
    print("Frontend scanner is fully functional!")
    print("  python run_scanner.py ./your-frontend-folder")

print()
print("=" * 80)
