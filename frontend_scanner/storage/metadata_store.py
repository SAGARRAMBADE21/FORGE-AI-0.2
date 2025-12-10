"""Metadata store using SQLite."""
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional
import json


class MetadataStore:
    """SQLite-based metadata store for file inventory and scan history."""
    
    def __init__(self, db_path: str = "./metadata.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self._init_schema()
    
    def _init_schema(self):
        """Initialize database schema."""
        cursor = self.conn.cursor()
        
        # Files table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE NOT NULL,
                relative_path TEXT,
                file_type TEXT,
                size_bytes INTEGER,
                sha256_hash TEXT,
                last_modified TEXT,
                last_scanned TEXT,
                metadata TEXT
            )
        """)
        
        # Scans table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_timestamp TEXT NOT NULL,
                project_root TEXT,
                total_files INTEGER,
                total_chunks INTEGER,
                status TEXT
            )
        """)
        
        self.conn.commit()
    
    def store_file(self, file_path: str, metadata: Dict[str, Any]):
        """Store or update file metadata."""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO files 
            (path, relative_path, file_type, size_bytes, sha256_hash, last_modified, last_scanned, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            file_path,
            metadata.get("relative_path"),
            metadata.get("file_type"),
            metadata.get("size_bytes"),
            metadata.get("sha256_hash"),
            metadata.get("last_modified"),
            datetime.now().isoformat(),
            json.dumps(metadata)
        ))
        
        self.conn.commit()
    
    def get_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Retrieve file metadata."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM files WHERE path = ?", (file_path,))
        row = cursor.fetchone()
        
        if row:
            return {
                "id": row[0],
                "path": row[1],
                "relative_path": row[2],
                "file_type": row[3],
                "size_bytes": row[4],
                "sha256_hash": row[5],
                "last_modified": row[6],
                "last_scanned": row[7],
                "metadata": json.loads(row[8]) if row[8] else {}
            }
        return None
    
    def get_changed_files(self, current_hashes: Dict[str, str]) -> List[str]:
        """Get list of files that have changed since last scan."""
        changed = []
        
        for path, new_hash in current_hashes.items():
            stored = self.get_file(path)
            if not stored or stored["sha256_hash"] != new_hash:
                changed.append(path)
        
        return changed
    
    def record_scan(self, scan_data: Dict[str, Any]):
        """Record a scan session."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO scans (scan_timestamp, project_root, total_files, total_chunks, status)
            VALUES (?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            scan_data.get("project_root"),
            scan_data.get("total_files"),
            scan_data.get("total_chunks"),
            "completed"
        ))
        self.conn.commit()
    
    def close(self):
        """Close database connection."""
        self.conn.close()
