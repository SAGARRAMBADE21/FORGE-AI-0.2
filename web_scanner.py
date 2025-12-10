"""
Web Interface for Frontend Scanner
Upload and scan frontend projects through a browser
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

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from frontend_scanner.config import ScannerConfig
from frontend_scanner.workflows.scanner_graph import create_scanner_workflow

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max upload
app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
app.config['SECRET_KEY'] = 'your-secret-key-here'

ALLOWED_EXTENSIONS = {'js', 'jsx', 'ts', 'tsx', 'vue', 'html', 'css', 'json', 'md', 'zip'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def scan_project(project_path: str) -> dict:
    """Scan a project and return results"""
    try:
        # Create config
        config = ScannerConfig(
            project_root=project_path,
            output_dir="./scanner_output"
        )
        
        # Create and run workflow
        workflow = create_scanner_workflow(config)
        result = workflow.invoke({
            "source_path": str(config.project_root),
            "files": [],
            "chunks": [],
            "embeddings": [],
            "metadata": {},
            "artifacts": {}
        })
        
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
        
        response_data = {
            "success": True,
            "files_processed": files_count,
            "chunks_created": chunks_count,
            "embeddings_generated": embeddings_count,
            "timestamp": datetime.now().isoformat(),
            "project_path": project_path,
            "framework": result.get("manifest", {}).get("framework", "unknown") if isinstance(result.get("manifest"), dict) else "unknown"
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
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_folder():
    """Handle folder upload and scanning"""
    if 'files[]' not in request.files:
        return jsonify({"error": "No files provided"}), 400
    
    files = request.files.getlist('files[]')
    if not files or files[0].filename == '':
        return jsonify({"error": "No files selected"}), 400
    
    # Create temporary directory for uploaded project
    project_name = request.form.get('projectName', 'uploaded_project')
    project_name = secure_filename(project_name)
    project_path = os.path.join(app.config['UPLOAD_FOLDER'], project_name)
    
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
        if os.path.exists(project_path):
            shutil.rmtree(project_path, ignore_errors=True)
        return jsonify({"error": str(e)}), 500

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

if __name__ == '__main__':
    print("=" * 80)
    print("Frontend Scanner Web Interface")
    print("=" * 80)
    print(f"\nServer starting at http://localhost:5000")
    print("\nFeatures:")
    print("  - Upload folders to scan")
    print("  - Scan local directories")
    print("  - Search code embeddings")
    print("  - View database status")
    print("\n" + "=" * 80)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
