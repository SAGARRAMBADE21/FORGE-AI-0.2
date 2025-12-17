"""
Web Interface for Frontend Scanner + Backend Generator
Upload and scan frontend projects, then generate backend code
"""

import os
import sys
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import tempfile
import shutil
from datetime import datetime
import json
import zipfile
from dotenv import load_dotenv
import os as _os

# Set environment variable for werkzeug multipart parser before importing
_os.environ['WERKZEUG_MAX_CONTENT_LENGTH'] = str(2 * 1024 * 1024 * 1024)  # 2GB

# Monkey-patch werkzeug's multipart parser size limits BEFORE importing
import werkzeug.sansio.multipart as multipart_module
from werkzeug.exceptions import RequestEntityTooLarge

# Override the max size constant
if hasattr(multipart_module, 'MAX_CONTENT_LENGTH'):
    multipart_module.MAX_CONTENT_LENGTH = 2 * 1024 * 1024 * 1024  # 2GB

# Patch the MultipartDecoder class to disable size checks
if hasattr(multipart_module, 'MultipartDecoder'):
    original_next_event = multipart_module.MultipartDecoder.next_event
    
    def patched_next_event(self):
        """Patched next_event that doesn't raise RequestEntityTooLarge"""
        try:
            return original_next_event(self)
        except RequestEntityTooLarge:
            # Log but don't raise - allow large uploads
            print("[WARNING] Size limit check bypassed for large upload")
            # Try to continue parsing
            return None
    
    multipart_module.MultipartDecoder.next_event = patched_next_event
    
    # Also patch __init__ to set large limits - accept all arguments
    original_init = multipart_module.MultipartDecoder.__init__
    def patched_init(self, boundary, max_form_memory_size=2*1024*1024*1024, **kwargs):
        # Call original with all arguments, setting large memory size
        original_init(self, boundary, max_form_memory_size=max_form_memory_size, **kwargs)
        # Override internal limits
        if hasattr(self, '_max_form_memory_size'):
            self._max_form_memory_size = 2 * 1024 * 1024 * 1024
    
    multipart_module.MultipartDecoder.__init__ = patched_init

# Load environment variables from BACKEND - GENERATOR/.env
backend_env_path = Path(__file__).parent / "BACKEND - GENERATOR" / ".env"
if backend_env_path.exists():
    load_dotenv(backend_env_path)
    print(f"✓ Loaded environment from {backend_env_path}")

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "BACKEND - GENERATOR"))

from frontend_scanner.config import ScannerConfig
from frontend_scanner.workflows.scanner_graph import create_scanner_workflow

# Backend generator imports (optional if not installed)
try:
    from backend_agent.config import BackendAgentConfig
    from backend_agent.workflow.backend_workflow import create_backend_workflow
    BACKEND_AVAILABLE = True
except ImportError:
    BACKEND_AVAILABLE = False
    print("Warning: Backend generator not available. Install dependencies in BACKEND - GENERATOR/")

# Custom Request class with unlimited form size
from flask import Request as FlaskRequest

class LargeUploadRequest(FlaskRequest):
    """Custom request class that allows large file uploads"""
    max_content_length = 2 * 1024 * 1024 * 1024  # 2GB
    max_form_memory_size = 2 * 1024 * 1024 * 1024  # 2GB
    max_form_parts = 10000

app = Flask(__name__)
app.request_class = LargeUploadRequest

# Configure maximum sizes for file uploads
MAX_SIZE = 2 * 1024 * 1024 * 1024  # 2GB
app.config['MAX_CONTENT_LENGTH'] = MAX_SIZE
app.config['MAX_FORM_MEMORY_SIZE'] = MAX_SIZE  
app.config['MAX_FORM_PARTS'] = 10000  # Allow up to 10000 form parts (files)
app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Global error handler to ensure JSON responses
@app.errorhandler(Exception)
def handle_exception(e):
    """Return JSON instead of HTML for errors"""
    import traceback
    print(f"\n=== UNHANDLED EXCEPTION ===")
    traceback.print_exc()
    print(f"===========================\n")
    
    # Get error details
    error_msg = str(e)
    status_code = getattr(e, 'code', 500)
    
    return jsonify({
        "success": False,
        "error": error_msg,
        "timestamp": datetime.now().isoformat()
    }), status_code

ALLOWED_EXTENSIONS = {'js', 'jsx', 'ts', 'tsx', 'vue', 'html', 'css', 'json', 'md', 'zip'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def scan_project(project_path: str) -> dict:
    """Scan a project and return results"""
    try:
        print(f"[scan_project] Starting scan for: {project_path}")
        
        # Create config
        config = ScannerConfig(
            project_root=project_path,
            output_dir="./scanner_output"
        )
        print(f"[scan_project] Config created")
        
        # Create and run workflow
        workflow = create_scanner_workflow(config)
        print(f"[scan_project] Workflow created, invoking...")
        
        result = workflow.invoke({
            "source_path": str(config.project_root),
            "files": [],
            "chunks": [],
            "embeddings": [],
            "metadata": {},
            "artifacts": {}
        })
        print(f"[scan_project] Workflow completed")
        
        # Debug: Print what we got
        print(f"\n=== WORKFLOW RESULT ===")
        print(f"Keys in result: {list(result.keys())}")
        
        parsed_files = result.get('parsed_files', [])
        chunks = result.get('chunks', [])
        embeddings = result.get('embeddings', [])
        file_inventory = result.get('file_inventory', None)
        
        print(f"Type of parsed_files: {type(parsed_files)}")
        print(f"Parsed Files count: {len(parsed_files) if isinstance(parsed_files, list) else 'not a list'}")
        print(f"Chunks count: {len(chunks) if isinstance(chunks, list) else 'not a list'}")
        print(f"Embeddings count: {len(embeddings) if isinstance(embeddings, list) else 'not a list'}")
        
        if file_inventory:
            print(f"File Inventory total_files: {getattr(file_inventory, 'total_files', 'N/A')}")
        
        print(f"======================\n")
        
        # Get the actual counts from the correct keys
        files_count = len(parsed_files) if isinstance(parsed_files, list) else 0
        chunks_count = len(chunks) if isinstance(chunks, list) else 0
        embeddings_count = len(embeddings) if isinstance(embeddings, list) else 0
        
        # Fallback to file_inventory if needed
        if files_count == 0 and file_inventory and hasattr(file_inventory, 'total_files'):
            files_count = file_inventory.total_files
        
        # Get manifest data for components and routes
        manifest = result.get("manifest", {})
        if isinstance(manifest, dict):
            components_count = len(manifest.get("components", []))
            routes_count = len(manifest.get("routes", []))
            framework = manifest.get("framework", "unknown")
        else:
            components_count = 0
            routes_count = 0
            framework = "unknown"
        
        # If framework is unknown, try to read from saved manifest file
        if framework == "unknown" or components_count == 0:
            try:
                import json
                manifest_file = Path("./scanner_output/manifest.json")
                if manifest_file.exists():
                    with open(manifest_file, 'r') as f:
                        saved_manifest = json.load(f)
                        if saved_manifest.get("framework") and saved_manifest.get("framework") != "unknown":
                            framework = saved_manifest.get("framework", "unknown")
                        if saved_manifest.get("components"):
                            components_count = len(saved_manifest.get("components", []))
                        if saved_manifest.get("routes"):
                            routes_count = len(saved_manifest.get("routes", []))
            except Exception as e:
                print(f"Warning: Could not read manifest file: {e}")
        
        response_data = {
            "success": True,
            "files_processed": files_count,
            "chunks_created": chunks_count,
            "embeddings_generated": embeddings_count,
            "components": components_count,
            "routes": routes_count,
            "timestamp": datetime.now().isoformat(),
            "project_path": project_path,
            "framework": framework
        }
        
        print(f"\n=== RESPONSE TO BROWSER ===")
        print(f"Response: {response_data}")
        print(f"===========================\n")
        
        return response_data
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.route('/')
def index():
    """Home page with upload form"""
    return render_template('forge.html')

@app.route('/forge')
def forge():
    """Integrated scanner + generator page"""
    return render_template('forge.html')

@app.route('/upload', methods=['POST'])
def upload_folder():
    """Handle folder upload and scanning"""
    project_path = None
    
    try:
        # Get content length for logging
        content_length = request.content_length
        if content_length:
            print(f"[Upload] Receiving {content_length / 1024 / 1024:.2f} MB of data")
        
        # Access files directly - the custom request class handles size limits
        if 'files[]' not in request.files:
            return jsonify({"success": False, "error": "No files provided"}), 400
        
        files = request.files.getlist('files[]')
        if not files or files[0].filename == '':
            return jsonify({"success": False, "error": "No files selected"}), 400
        
        # Create temporary directory for uploaded project
        project_name = request.form.get('projectName', 'uploaded_project')
        project_name = secure_filename(project_name)
        project_path = os.path.join(app.config['UPLOAD_FOLDER'], project_name)
        
    except Exception as e:
        print(f"Error in upload initial setup: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": f"Upload setup error: {str(e)}"}), 500
    
    try:
        # Save uploaded files maintaining directory structure
        os.makedirs(project_path, exist_ok=True)
        
        saved_files = []
        print(f"\n=== UPLOAD DEBUG ===")
        print(f"Received {len(files)} files")
        
        for idx, file in enumerate(files):
            if file and file.filename:
                # Check if it's a ZIP file
                if file.filename.lower().endswith('.zip'):
                    print(f"File {idx}: ZIP archive '{file.filename}'")
                    # Save ZIP temporarily
                    zip_path = os.path.join(project_path, secure_filename(file.filename))
                    file.save(zip_path)
                    
                    # Extract ZIP contents
                    try:
                        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                            print(f"  -> Extracting ZIP contents...")
                            zip_ref.extractall(project_path)
                            extracted_files = zip_ref.namelist()
                            print(f"  -> Extracted {len(extracted_files)} files")
                            saved_files.extend([os.path.join(project_path, f) for f in extracted_files])
                        
                        # Remove the ZIP file after extraction
                        os.remove(zip_path)
                    except zipfile.BadZipFile:
                        print(f"  -> Error: Invalid ZIP file")
                        return jsonify({"error": f"Invalid ZIP file: {file.filename}"}), 400
                else:
                    # Regular file upload
                    # Get relative path from the uploaded filename
                    # The filename already contains the full relative path from webkitRelativePath
                    rel_path = file.filename
                    print(f"File {idx}: filename='{file.filename}'")
                    
                    # Remove the root folder name from the path if it exists
                    # Example: "my-project/src/App.js" -> "src/App.js"
                    parts = rel_path.split('/', 1)
                    if len(parts) > 1:
                        rel_path = parts[1]  # Use everything after first slash
                    
                    file_path = os.path.join(project_path, rel_path)
                    print(f"  -> Saving to: {file_path}")
                    
                    # Create directories if needed
                    dir_path = os.path.dirname(file_path)
                    if dir_path:
                        os.makedirs(dir_path, exist_ok=True)
                    
                    # Save file
                    file.save(file_path)
                    saved_files.append(file_path)
        
        print(f"Saved {len(saved_files)} files to {project_path}")
        
        # List what was uploaded
        all_files = []
        for root, dirs, files_in_dir in os.walk(project_path):
            for f in files_in_dir:
                all_files.append(os.path.join(root, f))
        print(f"Total files in project: {len(all_files)}")
        for f in all_files[:10]:  # Print first 10
            print(f"  - {f}")
        print(f"===================\n")
        
        # Scan the project
        scan_result = scan_project(project_path)
        
        # Add debug info
        scan_result['uploaded_files'] = len(saved_files)
        scan_result['total_files_found'] = len(all_files)
        
        # Clean up uploaded files AFTER scanning
        shutil.rmtree(project_path, ignore_errors=True)
        
        return jsonify(scan_result)
    
    except Exception as e:
        # Clean up on error
        print(f"Error during upload/scan: {e}")
        import traceback
        traceback.print_exc()
        if 'project_path' in locals() and os.path.exists(project_path):
            shutil.rmtree(project_path, ignore_errors=True)
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/scan-local', methods=['POST'])
def scan_local():
    """Scan a local folder path"""
    data = request.get_json()
    folder_path = data.get('folderPath', '')
    
    if not folder_path:
        return jsonify({"error": "No folder path provided"}), 400
    
    if not os.path.exists(folder_path):
        return jsonify({"error": "Folder does not exist"}), 400
    
    if not os.path.isdir(folder_path):
        return jsonify({"error": "Path is not a directory"}), 400
    
    try:
        scan_result = scan_project(folder_path)
        return jsonify(scan_result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/status')
def status():
    """Get scanner status and database info"""
    from chromadb import PersistentClient
    
    try:
        client = PersistentClient(path="./vector_store")
        collection = client.get_or_create_collection("frontend_code")
        count = collection.count()
        
        return jsonify({
            "database_connected": True,
            "embeddings_count": count,
            "status": "ready"
        })
    except Exception as e:
        return jsonify({
            "database_connected": False,
            "error": str(e),
            "status": "error"
        })

@app.route('/search', methods=['POST'])
def search():
    """Search embeddings by query"""
    from chromadb import PersistentClient
    from sentence_transformers import SentenceTransformer
    
    data = request.get_json()
    query = data.get('query', '')
    n_results = data.get('n_results', 5)
    
    if not query:
        return jsonify({"error": "No query provided"}), 400
    
    try:
        # Initialize embedding model
        model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        
        # Embed query
        query_embedding = model.encode([query])[0].tolist()
        
        # Search ChromaDB
        client = PersistentClient(path="./vector_store")
        collection = client.get_or_create_collection("frontend_code")
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results['ids'][0])):
            formatted_results.append({
                "id": results['ids'][0][i],
                "distance": results['distances'][0][i],
                "content": results['documents'][0][i],
                "metadata": results['metadatas'][0][i]
            })
        
        return jsonify({
            "query": query,
            "results": formatted_results,
            "count": len(formatted_results)
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/generate-backend', methods=['POST'])
def generate_backend():
    """Generate backend from scan results"""
    if not BACKEND_AVAILABLE:
        return jsonify({
            "error": "Backend generator not available",
            "message": "Install dependencies: cd 'BACKEND - GENERATOR' && pip install -r requirements.txt"
        }), 503
    
    data = request.get_json()
    manifest_path = data.get('manifest_path', './scanner_output/manifest.json')
    requirements = data.get('requirements', 'Create a complete REST API backend with authentication')
    output_dir = data.get('output_dir', './generated-backend')
    
    try:
        # Load manifest
        with open(manifest_path) as f:
            manifest = json.load(f)
        
        # Create config
        config = BackendAgentConfig()
        config.project.output_dir = Path(output_dir)
        
        # Create workflow
        workflow = create_backend_workflow()
        
        # Initial state
        initial_state = {
            "frontend_manifest": manifest,
            "user_requirements": requirements,
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
            "workflow_stage": "init",
            "timestamp": datetime.now().isoformat()
        }
        
        # Generate with config for checkpointer
        config_dict = {"configurable": {"thread_id": f"backend_gen_{datetime.now().timestamp()}"}}
        result = workflow.invoke(initial_state, config_dict)
        
        return jsonify({
            "success": True,
            "stack": result.get('selected_stack', {}),
            "output_dir": output_dir,
            "files_generated": len(result.get('integrated_code', {})),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == '__main__':
    print("=" * 80)
    print("FORGE AI - Frontend Scanner + Backend Generator")
    print("=" * 80)
    print(f"Backend Generator: {'Available ✓' if BACKEND_AVAILABLE else 'Not Available ✗'}")
    print("=" * 80)
    print(f"\nServer starting at http://localhost:5000")
    print("\nFeatures:")
    print("  - Upload folders to scan")
    print("  - Scan local directories")
    print("  - Search code embeddings")
    print("  - View database status")
    print("\n" + "=" * 80)
    
    app.run(debug=True, host='127.0.0.1', port=5000)
