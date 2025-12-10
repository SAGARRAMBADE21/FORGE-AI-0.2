"""Artifact store for saving scan outputs."""
import json
from pathlib import Path
from typing import Any, Dict


class ArtifactStore:
    """Store for scan artifacts (manifests, summaries, logs)."""
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def save_manifest(self, manifest: Dict[str, Any]) -> Path:
        """Save manifest.json."""
        path = self.output_dir / "manifest.json"
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
        return path
    
    def save_summaries(self, summaries: Dict[str, Any]) -> Path:
        """Save hierarchical_summaries.json."""
        path = self.output_dir / "hierarchical_summaries.json"
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(summaries, f, indent=2)
        return path
    
    def save_inventory(self, inventory: Dict[str, Any]) -> Path:
        """Save file_inventory.json."""
        path = self.output_dir / "file_inventory.json"
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(inventory, f, indent=2)
        return path
    
    def save_changeset(self, changeset: Dict[str, Any]) -> Path:
        """Save changeset.json (for incremental scans)."""
        path = self.output_dir / "changeset.json"
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(changeset, f, indent=2)
        return path
    
    def load_artifact(self, artifact_name: str) -> Dict[str, Any]:
        """Load an artifact by name."""
        path = self.output_dir / f"{artifact_name}.json"
        if not path.exists():
            return {}
        
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
