"""Embedder Agent - Generate vector embeddings for code chunks."""
from typing import List, Any
from pydantic import BaseModel
import os

try:
    from langchain_openai import OpenAIEmbeddings
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI embeddings not available")

try:
    from langchain_community.embeddings import HuggingFaceEmbeddings
    HUGGINGFACE_AVAILABLE = True
except ImportError:
    HUGGINGFACE_AVAILABLE = False
    print("Warning: HuggingFace embeddings not available")


class ChunkEmbedding(BaseModel):
    """Embedding result for a chunk."""
    chunk_id: str
    embedding: List[float]
    model: str


class EmbedderAgent:
    """Agent that generates embeddings for code chunks."""
    
    def __init__(self, config):
        self.config = config
        self.embedder = None
        self._init_embedder()
    
    def _init_embedder(self):
        """Initialize embedding model."""
        try:
            if self.config.embedding.provider == "openai" and OPENAI_AVAILABLE:
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    print("Warning: OPENAI_API_KEY not set. Embeddings will fail.")
                
                self.embedder = OpenAIEmbeddings(
                    model=self.config.embedding.model,
                    dimensions=self.config.embedding.dimensions
                )
                print(f"✓ Initialized OpenAI embeddings: {self.config.embedding.model}")
            
            elif self.config.embedding.provider == "local" and HUGGINGFACE_AVAILABLE:
                self.embedder = HuggingFaceEmbeddings(
                    model_name=self.config.embedding.model
                )
                print(f"✓ Initialized local HuggingFace embeddings: {self.config.embedding.model}")
            
            else:
                print("Error: No embedding provider available")
                print("Install: pip install langchain-openai")
        
        except Exception as e:
            print(f"Error initializing embedder: {e}")
            self.embedder = None
    
    def embed_chunks(self, chunks: List[Any]) -> List[ChunkEmbedding]:
        """Generate embeddings for all chunks."""
        if not self.embedder:
            print("Warning: No embedder available. Returning empty embeddings.")
            return []
        
        embeddings = []
        batch_size = self.config.embedding.batch_size
        
        print(f"Generating embeddings for {len(chunks)} chunks...")
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            texts = [chunk.content for chunk in batch]
            
            try:
                batch_embeddings = self.embedder.embed_documents(texts)
                
                for chunk, embedding in zip(batch, batch_embeddings):
                    embeddings.append(ChunkEmbedding(
                        chunk_id=chunk.chunk_id,
                        embedding=embedding,
                        model=self.config.embedding.model
                    ))
                
                if (i // batch_size + 1) % 5 == 0:
                    print(f"  Processed {i + len(batch)}/{len(chunks)} chunks")
            
            except Exception as e:
                print(f"Error embedding batch {i // batch_size}: {e}")
                # Continue with next batch
                continue
        
        print(f"✓ Generated {len(embeddings)} embeddings")
        return embeddings
