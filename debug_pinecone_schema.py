"""
Debug script to inspect actual Pinecone vector metadata/schema
"""
import os
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

# Initialize Pinecone
api_key = os.getenv("PINECONE_API_KEY")
index_name = "poker-knowledge"

pc = Pinecone(api_key=api_key)
index = pc.Index(index_name)

# Fetch a few sample vectors to inspect schema
print("=" * 60)
print("FETCHING SAMPLE VECTORS")
print("=" * 60)

# Query to get some vectors (using a dummy embedding)
dummy_query = [0.1] * 384  # Match dimension
results = index.query(
    vector=dummy_query,
    top_k=3,
    include_metadata=True
)

print(f"\nFound {len(results['matches'])} vectors\n")

for i, match in enumerate(results['matches'], 1):
    print(f"Vector {i}:")
    print(f"  ID: {match['id']}")
    print(f"  Score: {match.get('score', 'N/A')}")
    print(f"  Metadata keys: {list(match.get('metadata', {}).keys())}")
    print(f"  Metadata: {match.get('metadata', {})}")
    print()

print("=" * 60)
