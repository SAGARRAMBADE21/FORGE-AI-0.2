"""Framework detection utilities."""
import json
from pathlib import Path
from typing import Literal, Optional

Framework = Literal["react", "nextjs", "vue", "svelte", "angular", "static"]


class FrameworkDetector:
    """Detect frontend framework from project structure."""
    
    @staticmethod
    def detect(project_root: Path) -> Optional[Framework]:
        """Detect framework from project structure and files."""
        
        # Check package.json
        package_json = project_root / "package.json"
        if package_json.exists():
            try:
                with open(package_json, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    deps = {
                        **data.get("dependencies", {}),
                        **data.get("devDependencies", {})
                    }
                    
                    if "next" in deps:
                        return "nextjs"
                    elif "react" in deps:
                        return "react"
                    elif "vue" in deps:
                        return "vue"
                    elif "svelte" in deps:
                        return "svelte"
                    elif "@angular/core" in deps:
                        return "angular"
            except Exception as e:
                print(f"Error reading package.json: {e}")
        
        # Check for specific config files
        if (project_root / "next.config.js").exists() or \
           (project_root / "next.config.mjs").exists() or \
           (project_root / "next.config.ts").exists():
            return "nextjs"
        
        if (project_root / "vue.config.js").exists():
            return "vue"
        
        if (project_root / "svelte.config.js").exists():
            return "svelte"
        
        if (project_root / "angular.json").exists():
            return "angular"
        
        return "static"
    
    @staticmethod
    def detect_build_tool(project_root: Path) -> Optional[str]:
        """Detect build tool (Vite, webpack, etc.)."""
        if (project_root / "vite.config.js").exists() or \
           (project_root / "vite.config.ts").exists():
            return "vite"
        
        if (project_root / "webpack.config.js").exists():
            return "webpack"
        
        if (project_root / "rollup.config.js").exists():
            return "rollup"
        
        return None
