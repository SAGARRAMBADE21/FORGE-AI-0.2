"""Redactor Agent - Remove secrets and sensitive data."""
import re
from typing import List
from frontend_scanner.agents.chunker import CodeChunk


class RedactorAgent:
    """Agent that sanitizes sensitive information from code chunks."""
    
    def __init__(self, config):
        self.config = config
        self.patterns = []
        
        if self.config.security.redact_secrets:
            self.patterns = [
                re.compile(p) for p in self.config.security.redact_patterns
            ]
    
    def redact(self, chunk: CodeChunk) -> CodeChunk:
        """Redact sensitive information from a chunk."""
        if not self.config.security.redact_secrets or not self.patterns:
            return chunk
        
        redacted_content = chunk.content
        
        try:
            for pattern in self.patterns:
                redacted_content = pattern.sub('[REDACTED]', redacted_content)
        except Exception as e:
            print(f"Error redacting chunk {chunk.chunk_id}: {e}")
            return chunk
        
        # Create new chunk with redacted content
        return CodeChunk(
            chunk_id=chunk.chunk_id,
            file_path=chunk.file_path,
            content=redacted_content,
            start_line=chunk.start_line,
            end_line=chunk.end_line,
            token_count=chunk.token_count,
            chunk_type=chunk.chunk_type,
            language=chunk.language,
            metadata={**chunk.metadata, "redacted": True},
            provenance=chunk.provenance
        )
