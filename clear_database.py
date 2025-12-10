"""Delete all embeddings from the vector database."""
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import chromadb
from pathlib import Path

# Connect to database
db_path = "./vector_store"
client = chromadb.PersistentClient(path=db_path)

print("=" * 70)
print("CLEARING VECTOR DATABASE")
print("=" * 70)

try:
    # Get collection
    collection = client.get_collection(name="frontend_code")
    
    # Check current count
    count = collection.count()
    print(f"\nCurrent embeddings in database: {count}")
    
    if count == 0:
        print("✓ Database is already empty!")
    else:
        # Delete the collection
        client.delete_collection(name="frontend_code")
        print(f"✓ Deleted collection 'frontend_code' with {count} embeddings")
        
        # Recreate empty collection
        client.create_collection(
            name="frontend_code",
            metadata={"hnsw:space": "cosine"}
        )
        print("✓ Created new empty collection 'frontend_code'")
        
        # Verify
        new_collection = client.get_collection(name="frontend_code")
        new_count = new_collection.count()
        print(f"\nVerification: Database now has {new_count} embeddings")
        print("\n✓ All embeddings successfully deleted!")

except Exception as e:
    print(f"\nError: {e}")
    print("\nNote: If collection doesn't exist, database is already empty.")

print("=" * 70)
