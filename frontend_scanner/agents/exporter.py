"""Exporter Agent - Export all results."""
import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict


class ExporterAgent:
    """Agent that exports scan results to filesystem."""
    
    def __init__(self, config):
        self.config = config
        self.output_dir = Path(config.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export(self, manifest: Any, summaries: Dict[str, Any],
               vector_index: Dict[str, Any], file_inventory: Any):
        """Export all results."""
        print("\nExporting results...")
        
        try:
            self._export_manifest(manifest)
            self._export_summaries(summaries)
            self._export_inventory(file_inventory)
            self._export_logs(vector_index)
            
            print(f"\n✅ All results exported to: {self.output_dir}")
        
        except Exception as e:
            print(f"Error exporting results: {e}")
    
    def _export_manifest(self, manifest):
        """Export manifest.json."""
        try:
            output_path = self.output_dir / "manifest.json"
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(manifest.model_dump(), f, indent=2)
            print(f"  ✓ manifest.json")
        except Exception as e:
            print(f"  ✗ Error exporting manifest: {e}")
    
    def _export_summaries(self, summaries: Dict[str, Any]):
        """Export hierarchical_summaries.json."""
        try:
            output_path = self.output_dir / "hierarchical_summaries.json"
            
            export_data = {
                "file_summaries": [
                    s.model_dump() for s in summaries.get("file_summaries", [])
                ],
                "folder_summaries": [
                    s.model_dump() for s in summaries.get("folder_summaries", [])
                ],
                "project_summary": (
                    summaries.get("project_summary").model_dump()
                    if summaries.get("project_summary") else {}
                )
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2)
            print(f"  ✓ hierarchical_summaries.json")
        except Exception as e:
            print(f"  ✗ Error exporting summaries: {e}")
    
    def _export_inventory(self, inventory):
        """Export file_inventory.json."""
        try:
            output_path = self.output_dir / "file_inventory.json"
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(inventory.model_dump(), f, indent=2)
            print(f"  ✓ file_inventory.json")
        except Exception as e:
            print(f"  ✗ Error exporting inventory: {e}")
    
    def _export_logs(self, vector_index: Dict[str, Any]):
        """Export scan logs."""
        try:
            output_path = self.output_dir / "scan_logs.json"
            logs = {
                "timestamp": datetime.now().isoformat(),
                "total_chunks": vector_index.get("total_chunks", 0),
                "total_embeddings": vector_index.get("total_embeddings", 0),
                "status": "completed"
            }
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2)
            print(f"  ✓ scan_logs.json")
        except Exception as e:
            print(f"  ✗ Error exporting logs: {e}")
