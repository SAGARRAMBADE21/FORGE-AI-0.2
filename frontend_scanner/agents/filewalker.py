"""FileWalker Agent - Recursively scans project directories."""
import hashlib
import mimetypes
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

try:
    from gitignore_parser import parse_gitignore
    GITIGNORE_AVAILABLE = True
except ImportError:
    GITIGNORE_AVAILABLE = False
    print("Warning: gitignore-parser not available. .gitignore files will be ignored.")


class FileMetadata(BaseModel):
    """Metadata for a single file."""
    path: str
    relative_path: str
    file_type: str
    extension: str
    size_bytes: int
    last_modified: str
    sha256_hash: str
    mime_type: Optional[str] = None
    is_binary: bool = False
    framework_hints: List[str] = Field(default_factory=list)


class FileInventory(BaseModel):
    """Complete file inventory for a project."""
    project_root: str
    scan_timestamp: str
    total_files: int
    total_size_bytes: int
    files: List[FileMetadata]
    errors: List[Dict[str, str]] = Field(default_factory=list)


class FileWalkerAgent:
    """Agent that walks directory tree and collects file metadata."""
    
    def __init__(self, config):
        self.config = config
        self.gitignore_matcher = None
        
        if GITIGNORE_AVAILABLE:
            gitignore_path = Path(config.project_root) / ".gitignore"
            if gitignore_path.exists():
                try:
                    self.gitignore_matcher = parse_gitignore(gitignore_path)
                except Exception as e:
                    print(f"Warning: Could not parse .gitignore: {e}")
    
    def should_process(self, file_path: Path) -> bool:
        """Check if file should be processed."""
        try:
            # Check if file exists and is a file
            if not file_path.is_file():
                return False
            
            # Check gitignore
            if self.gitignore_matcher:
                try:
                    if self.gitignore_matcher(str(file_path)):
                        return False
                except:
                    pass
            
            # Check exclude patterns
            from fnmatch import fnmatch
            try:
                rel_path = file_path.relative_to(self.config.project_root)
            except ValueError:
                return False
            
            for pattern in self.config.security.exclude_patterns:
                if fnmatch(str(rel_path), pattern) or fnmatch(file_path.name, pattern):
                    return False
            
            # Check file size
            try:
                if file_path.stat().st_size > self.config.max_file_size_mb * 1024 * 1024:
                    return False
            except:
                return False
            
            # Check extension
            if file_path.suffix and file_path.suffix not in self.config.supported_extensions:
                return False
            
            return True
        except Exception:
            return False
    
    def compute_hash(self, file_path: Path) -> str:
        """Compute SHA256 hash of file."""
        sha256 = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception as e:
            print(f"Error hashing {file_path}: {e}")
            return ""
    
    def detect_framework_hints(self, file_path: Path) -> List[str]:
        """Detect framework hints from file path and name."""
        hints = []
        path_str = str(file_path).lower()
        
        if 'next.config' in path_str or '/pages/' in path_str or '/app/' in path_str:
            hints.append("nextjs")
        if '.vue' in file_path.suffix:
            hints.append("vue")
        if '.svelte' in file_path.suffix:
            hints.append("svelte")
        if 'vite.config' in path_str:
            hints.append("vite")
        if 'webpack.config' in path_str:
            hints.append("webpack")
        if 'react' in path_str.lower():
            hints.append("react")
        
        return hints
    
    def scan(self) -> FileInventory:
        """Execute file walk and produce inventory."""
        root = Path(self.config.project_root).resolve()
        
        if not root.exists():
            raise ValueError(f"Project root does not exist: {root}")
        
        files = []
        total_size = 0
        errors = []
        
        print(f"Scanning: {root}")
        
        try:
            for file_path in root.rglob('*'):
                if not file_path.is_file():
                    continue
                
                try:
                    if not self.should_process(file_path):
                        continue
                    
                    stat = file_path.stat()
                    mime_type, _ = mimetypes.guess_type(str(file_path))
                    is_binary = mime_type and not mime_type.startswith('text') if mime_type else False
                    
                    metadata = FileMetadata(
                        path=str(file_path),
                        relative_path=str(file_path.relative_to(root)),
                        file_type=file_path.suffix[1:] if file_path.suffix else "unknown",
                        extension=file_path.suffix,
                        size_bytes=stat.st_size,
                        last_modified=datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        sha256_hash=self.compute_hash(file_path),
                        mime_type=mime_type,
                        is_binary=is_binary,
                        framework_hints=self.detect_framework_hints(file_path)
                    )
                    
                    files.append(metadata)
                    total_size += stat.st_size
                    
                except Exception as e:
                    errors.append({
                        "file": str(file_path),
                        "error": str(e)
                    })
        
        except Exception as e:
            errors.append({
                "scan": "global",
                "error": str(e)
            })
        
        return FileInventory(
            project_root=str(root),
            scan_timestamp=datetime.now().isoformat(),
            total_files=len(files),
            total_size_bytes=total_size,
            files=files,
            errors=errors
        )
