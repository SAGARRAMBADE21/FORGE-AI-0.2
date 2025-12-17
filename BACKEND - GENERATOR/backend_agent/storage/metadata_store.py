"""
Metadata Store
Stores metadata about generations.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional


class MetadataStore:
    """Stores generation metadata."""
    
    def __init__(self, db_path: str = "./metadata.json"):
        self.db_path = Path(db_path)
        self.data = self._load()
    
    def _load(self) -> Dict:
        """Load metadata from disk."""
        if self.db_path.exists():
            with open(self.db_path, 'r') as f:
                return json.load(f)
        return {"generations": {}, "projects": {}}
    
    def _save(self) -> None:
        """Save metadata to disk."""
        with open(self.db_path, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def add_generation(self, version_id: str, metadata: Dict[str, Any]) -> None:
        """Add generation metadata."""
        self.data["generations"][version_id] = metadata
        self._save()
    
    def get_generation(self, version_id: str) -> Optional[Dict[str, Any]]:
        """Get generation metadata."""
        return self.data["generations"].get(version_id)
    
    def add_project(self, project_name: str, config: Dict[str, Any]) -> None:
        """Add project configuration."""
        self.data["projects"][project_name] = config
        self._save()
    
    def get_project(self, project_name: str) -> Optional[Dict[str, Any]]:
        """Get project configuration."""
        return self.data["projects"].get(project_name)
