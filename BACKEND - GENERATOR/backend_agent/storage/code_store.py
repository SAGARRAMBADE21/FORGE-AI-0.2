"""
Code Store
Stores generated code and manages versions.
"""

from pathlib import Path
from typing import Dict, Optional
import json
from datetime import datetime


class CodeStore:
    """Stores generated code."""
    
    def __init__(self, storage_dir: str = "./code-store"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def save_generation(self, project_name: str, files: Dict[str, str], 
                       metadata: Dict) -> str:
        """Save a code generation."""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version_id = f"{project_name}_{timestamp}"
        
        version_dir = self.storage_dir / version_id
        version_dir.mkdir(parents=True, exist_ok=True)
        
        # Save files
        files_dir = version_dir / "files"
        files_dir.mkdir(exist_ok=True)
        
        for filepath, content in files.items():
            file_path = files_dir / filepath
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        # Save metadata
        metadata_file = version_dir / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return version_id
    
    def load_generation(self, version_id: str) -> Optional[Dict]:
        """Load a saved generation."""
        
        version_dir = self.storage_dir / version_id
        if not version_dir.exists():
            return None
        
        # Load metadata
        metadata_file = version_dir / "metadata.json"
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        # Load files
        files_dir = version_dir / "files"
        files = {}
        
        for file_path in files_dir.rglob("*"):
            if file_path.is_file():
                relative_path = file_path.relative_to(files_dir)
                with open(file_path, 'r', encoding='utf-8') as f:
                    files[str(relative_path)] = f.read()
        
        return {
            "version_id": version_id,
            "metadata": metadata,
            "files": files
        }
    
    def list_generations(self, project_name: Optional[str] = None) -> list:
        """List all saved generations."""
        
        generations = []
        
        for version_dir in self.storage_dir.iterdir():
            if version_dir.is_dir():
                if project_name and not version_dir.name.startswith(project_name):
                    continue
                
                metadata_file = version_dir / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    
                    generations.append({
                        "version_id": version_dir.name,
                        "timestamp": metadata.get("timestamp"),
                        "project": metadata.get("project_name")
                    })
        
        return sorted(generations, key=lambda x: x["timestamp"], reverse=True)
