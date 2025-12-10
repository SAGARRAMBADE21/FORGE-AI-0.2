"""Chunker Agent - AST-aware code chunking."""
from typing import List, Dict, Any
from pydantic import BaseModel, Field
import tiktoken


class CodeChunk(BaseModel):
    """Represents a chunk of code with metadata."""
    chunk_id: str
    file_path: str
    content: str
    start_line: int
    end_line: int
    token_count: int
    chunk_type: str
    language: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    provenance: Dict[str, Any] = Field(default_factory=dict)


class ChunkerAgent:
    """Agent that chunks code using AST-aware strategies."""
    
    def __init__(self, config):
        self.config = config
        try:
            self.encoding = tiktoken.get_encoding("cl100k_base")
        except Exception as e:
            print(f"Warning: Could not load tiktoken encoding: {e}")
            self.encoding = None
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        if self.encoding:
            try:
                return len(self.encoding.encode(text))
            except:
                pass
        # Fallback: approximate tokens
        return len(text) // 4
    
    def chunk(self, parsed_file, file_content: str) -> List[CodeChunk]:
        """Create chunks from parsed file."""
        chunks = []
        
        if not file_content.strip():
            return chunks
        
        try:
            if self.config.chunking.use_ast_chunking and parsed_file.components:
                chunks.extend(self._chunk_by_components(parsed_file, file_content))
            else:
                chunks.extend(self._chunk_by_tokens(parsed_file, file_content))
        except Exception as e:
            print(f"Error chunking {parsed_file.file_path}: {e}")
            # Fallback to simple chunking
            chunks.extend(self._chunk_by_lines(parsed_file, file_content))
        
        return chunks
    
    def _chunk_by_components(self, parsed_file, content: str) -> List[CodeChunk]:
        """Chunk code by AST components."""
        chunks = []
        lines = content.splitlines()
        
        if not lines:
            return chunks
        
        for i, component in enumerate(parsed_file.components):
            try:
                start_line = max(0, component.start_line)
                end_line = min(len(lines), component.end_line + 1)
                
                if start_line >= end_line:
                    continue
                
                chunk_content = "\n".join(lines[start_line:end_line])
                
                if not chunk_content.strip():
                    continue
                
                token_count = self.count_tokens(chunk_content)
                
                if token_count > self.config.chunking.chunk_size:
                    chunks.extend(self._split_large_chunk(
                        chunk_content,
                        parsed_file.file_path,
                        start_line,
                        component,
                        parsed_file.language
                    ))
                else:
                    chunk = CodeChunk(
                        chunk_id=f"{parsed_file.file_path}:component:{i}",
                        file_path=parsed_file.file_path,
                        content=chunk_content,
                        start_line=start_line,
                        end_line=end_line,
                        token_count=token_count,
                        chunk_type="component",
                        language=parsed_file.language,
                        metadata={
                            "component_name": component.name,
                            "component_type": component.type,
                            "hooks": component.hooks,
                            "framework": parsed_file.framework,
                        },
                        provenance={
                            "file": parsed_file.file_path,
                            "lines": f"{start_line}-{end_line}",
                            "framework": parsed_file.framework,
                        }
                    )
                    chunks.append(chunk)
            except Exception as e:
                print(f"Error processing component {i}: {e}")
                continue
        
        return chunks
    
    def _chunk_by_tokens(self, parsed_file, content: str) -> List[CodeChunk]:
        """Token-based chunking with overlap."""
        chunks = []
        lines = content.splitlines()
        
        if not lines:
            return chunks
        
        chunk_size = self.config.chunking.chunk_size
        overlap = self.config.chunking.chunk_overlap
        
        current_chunk = []
        current_tokens = 0
        chunk_start_line = 0
        chunk_idx = 0
        
        for i, line in enumerate(lines):
            line_tokens = self.count_tokens(line)
            
            if current_tokens + line_tokens > chunk_size and current_chunk:
                chunk_content = "\n".join(current_chunk)
                
                if chunk_content.strip():
                    chunks.append(CodeChunk(
                        chunk_id=f"{parsed_file.file_path}:token:{chunk_idx}",
                        file_path=parsed_file.file_path,
                        content=chunk_content,
                        start_line=chunk_start_line,
                        end_line=i,
                        token_count=current_tokens,
                        chunk_type="text",
                        language=parsed_file.language,
                        metadata={"framework": parsed_file.framework},
                        provenance={
                            "file": parsed_file.file_path,
                            "lines": f"{chunk_start_line}-{i}",
                        }
                    ))
                
                overlap_lines = self._get_overlap_lines(current_chunk, overlap)
                current_chunk = overlap_lines + [line]
                current_tokens = self.count_tokens("\n".join(current_chunk))
                chunk_start_line = i - len(overlap_lines)
                chunk_idx += 1
            else:
                current_chunk.append(line)
                current_tokens += line_tokens
        
        if current_chunk and "\n".join(current_chunk).strip():
            chunks.append(CodeChunk(
                chunk_id=f"{parsed_file.file_path}:token:{chunk_idx}",
                file_path=parsed_file.file_path,
                content="\n".join(current_chunk),
                start_line=chunk_start_line,
                end_line=len(lines),
                token_count=current_tokens,
                chunk_type="text",
                language=parsed_file.language,
                metadata={"framework": parsed_file.framework},
                provenance={
                    "file": parsed_file.file_path,
                    "lines": f"{chunk_start_line}-{len(lines)}",
                }
            ))
        
        return chunks
    
    def _chunk_by_lines(self, parsed_file, content: str) -> List[CodeChunk]:
        """Simple line-based chunking fallback."""
        chunks = []
        lines = content.splitlines()
        
        lines_per_chunk = 50
        
        for i in range(0, len(lines), lines_per_chunk):
            chunk_lines = lines[i:i + lines_per_chunk]
            chunk_content = "\n".join(chunk_lines)
            
            if chunk_content.strip():
                chunks.append(CodeChunk(
                    chunk_id=f"{parsed_file.file_path}:lines:{i}",
                    file_path=parsed_file.file_path,
                    content=chunk_content,
                    start_line=i,
                    end_line=i + len(chunk_lines),
                    token_count=self.count_tokens(chunk_content),
                    chunk_type="text",
                    language=parsed_file.language,
                    metadata={},
                    provenance={
                        "file": parsed_file.file_path,
                        "lines": f"{i}-{i + len(chunk_lines)}",
                    }
                ))
        
        return chunks
    
    def _split_large_chunk(self, content: str, file_path: str,
                          start_line: int, component, language: str) -> List[CodeChunk]:
        """Split a large component into smaller chunks."""
        chunks = []
        lines = content.splitlines()
        chunk_size = self.config.chunking.chunk_size
        
        current_chunk = []
        current_tokens = 0
        chunk_start = 0
        
        for i, line in enumerate(lines):
            line_tokens = self.count_tokens(line)
            
            if current_tokens + line_tokens > chunk_size and current_chunk:
                chunk_content = "\n".join(current_chunk)
                if chunk_content.strip():
                    chunks.append(CodeChunk(
                        chunk_id=f"{file_path}:component-split:{len(chunks)}",
                        file_path=file_path,
                        content=chunk_content,
                        start_line=start_line + chunk_start,
                        end_line=start_line + i,
                        token_count=current_tokens,
                        chunk_type="component",
                        language=language,
                        metadata={"component_name": component.name, "split": True},
                        provenance={
                            "file": file_path,
                            "lines": f"{start_line + chunk_start}-{start_line + i}",
                        }
                    ))
                current_chunk = [line]
                current_tokens = line_tokens
                chunk_start = i
            else:
                current_chunk.append(line)
                current_tokens += line_tokens
        
        if current_chunk and "\n".join(current_chunk).strip():
            chunks.append(CodeChunk(
                chunk_id=f"{file_path}:component-split:{len(chunks)}",
                file_path=file_path,
                content="\n".join(current_chunk),
                start_line=start_line + chunk_start,
                end_line=start_line + len(lines),
                token_count=current_tokens,
                chunk_type="component",
                language=language,
                metadata={"component_name": component.name, "split": True},
                provenance={
                    "file": file_path,
                    "lines": f"{start_line + chunk_start}-{start_line + len(lines)}",
                }
            ))
        
        return chunks
    
    def _get_overlap_lines(self, lines: List[str], overlap_tokens: int) -> List[str]:
        """Get lines for overlap based on token count."""
        overlap_lines = []
        tokens = 0
        
        for line in reversed(lines):
            line_tokens = self.count_tokens(line)
            if tokens + line_tokens > overlap_tokens:
                break
            overlap_lines.insert(0, line)
            tokens += line_tokens
        
        return overlap_lines
