"""
File Utilities
Read and write files, create directories.
"""

from pathlib import Path
from typing import Dict, Union


def write_files(output_dir: Union[str, Path], files: Dict[str, str]) -> None:
    """Write multiple files to disk."""
    
    output_path = Path(output_dir)
    
    for filepath, content in files.items():
        full_path = output_path / filepath
        
        # Create parent directories
        ensure_directory(full_path.parent)
        
        # Write file
        try:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Created: {filepath}")
        except Exception as e:
            print(f"✗ Error writing {filepath}: {e}")


def read_file(filepath: Union[str, Path]) -> str:
    """Read file content."""
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return ""


def ensure_directory(directory: Union[str, Path]) -> None:
    """Ensure directory exists."""
    
    Path(directory).mkdir(parents=True, exist_ok=True)


def copy_file(src: Union[str, Path], dst: Union[str, Path]) -> None:
    """Copy file from src to dst."""
    
    import shutil
    
    src_path = Path(src)
    dst_path = Path(dst)
    
    ensure_directory(dst_path.parent)
    shutil.copy2(src_path, dst_path)


def delete_file(filepath: Union[str, Path]) -> None:
    """Delete file if exists."""
    
    path = Path(filepath)
    if path.exists():
        path.unlink()


def list_files(directory: Union[str, Path], pattern: str = "*") -> list:
    """List files in directory matching pattern."""
    
    path = Path(directory)
    if not path.exists():
        return []
    
    return list(path.glob(pattern))
