"""Vector store abstraction layer."""
from abc import ABC, abstractmethod
from typing import Any, List, Dict, Optional
import os

try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    print("Warning: ChromaDB not available")

try:
    import faiss
    import numpy as np
    import pickle
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("Warning: FAISS not available")


class VectorStore(ABC):
    """Abstract vector store interface."""
    
    @abstractmethod
    def add(self, chunk_id: str, embedding: List[float],
            content: str, metadata: Dict[str, Any], provenance: Dict[str, Any]):
        """Add a chunk with embedding."""
        pass
    
    @abstractmethod
    def query(self, query_embedding: List[float], k: int = 5,
              filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Semantic search."""
        pass
    
    @abstractmethod
    def persist(self):
        """Persist to disk."""
        pass


class ChromaVectorStore(VectorStore):
    """Chroma implementation."""
    
    def __init__(self, config):
        if not CHROMA_AVAILABLE:
            raise ImportError("ChromaDB not available. Install: pip install chromadb")
        
        self.config = config
        persist_dir = config.vector_store.persist_directory
        
        # Create directory
        from pathlib import Path
        Path(persist_dir).mkdir(parents=True, exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=persist_dir)
        
        # Get or create collection
        try:
            self.collection = self.client.get_or_create_collection(
                name=config.vector_store.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            print(f"✓ Chroma collection: {config.vector_store.collection_name}")
        except Exception as e:
            print(f"Error creating Chroma collection: {e}")
            raise
    
    def add(self, chunk_id: str, embedding: List[float],
            content: str, metadata: Dict[str, Any], provenance: Dict[str, Any]):
        """Add chunk to Chroma."""
        try:
            # Combine metadata and provenance
            full_metadata = {**metadata, **provenance}
            
            # Convert non-string values to strings for Chroma
            clean_metadata = {}
            for k, v in full_metadata.items():
                if isinstance(v, (str, int, float, bool)):
                    clean_metadata[k] = v
                elif isinstance(v, (list, dict)):
                    clean_metadata[k] = str(v)
                else:
                    clean_metadata[k] = str(v)
            
            self.collection.add(
                ids=[chunk_id],
                embeddings=[embedding],
                documents=[content],
                metadatas=[clean_metadata]
            )
        except Exception as e:
            print(f"Error adding to Chroma: {e}")
    
    def query(self, query_embedding: List[float], k: int = 5,
              filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Query Chroma."""
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=k,
                where=filters
            )
            
            return [
                {
                    "chunk_id": results["ids"][0][i],
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i] if results.get("distances") else 0
                }
                for i in range(len(results["ids"][0]))
            ]
        except Exception as e:
            print(f"Error querying Chroma: {e}")
            return []
    
    def persist(self):
        """Chroma auto-persists."""
        pass


class FAISSVectorStore(VectorStore):
    """FAISS implementation."""
    
    def __init__(self, config):
        if not FAISS_AVAILABLE:
            raise ImportError("FAISS not available. Install: pip install faiss-cpu")
        
        self.config = config
        self.dimension = config.embedding.dimensions
        self.index = faiss.IndexFlatL2(self.dimension)
        self.chunk_data = []
        
        print(f"✓ FAISS index initialized (dimension: {self.dimension})")
    
    def add(self, chunk_id: str, embedding: List[float],
            content: str, metadata: Dict[str, Any], provenance: Dict[str, Any]):
        """Add to FAISS."""
        try:
            embedding_array = np.array([embedding]).astype('float32')
            self.index.add(embedding_array)
            
            self.chunk_data.append({
                "chunk_id": chunk_id,
                "content": content,
                "metadata": metadata,
                "provenance": provenance
            })
        except Exception as e:
            print(f"Error adding to FAISS: {e}")
    
    def query(self, query_embedding: List[float], k: int = 5,
              filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Query FAISS."""
        try:
            query_array = np.array([query_embedding]).astype('float32')
            distances, indices = self.index.search(query_array, min(k, len(self.chunk_data)))
            
            results = []
            for i, idx in enumerate(indices[0]):
                if idx < len(self.chunk_data) and idx >= 0:
                    result = {
                        **self.chunk_data[idx],
                        "distance": float(distances[0][i])
                    }
                    
                    # Apply filters if provided
                    if filters:
                        match = True
                        for key, value in filters.items():
                            if result.get("metadata", {}).get(key) != value:
                                match = False
                                break
                        if match:
                            results.append(result)
                    else:
                        results.append(result)
            
            return results
        except Exception as e:
            print(f"Error querying FAISS: {e}")
            return []
    
    def persist(self):
        """Save FAISS index."""
        from pathlib import Path
        
        try:
            persist_dir = Path(self.config.vector_store.persist_directory)
            persist_dir.mkdir(parents=True, exist_ok=True)
            
            # Save index
            faiss.write_index(self.index, str(persist_dir / "index.faiss"))
            
            # Save metadata
            with open(persist_dir / "metadata.pkl", 'wb') as f:
                pickle.dump(self.chunk_data, f)
            
            print(f"✓ FAISS index persisted to {persist_dir}")
        except Exception as e:
            print(f"Error persisting FAISS: {e}")


class VectorStoreFactory:
    """Factory for creating vector stores."""
    
    @staticmethod
    def create(config) -> VectorStore:
        """Create vector store based on config."""
        backend = config.vector_store.backend
        
        if backend == "chroma":
            return ChromaVectorStore(config)
        elif backend == "faiss":
            return FAISSVectorStore(config)
        else:
            raise ValueError(f"Unknown vector store backend: {backend}")
