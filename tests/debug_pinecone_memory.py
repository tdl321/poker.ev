#!/usr/bin/env python3
"""Check what's in the poker-memory index"""
import os
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

# Initialize Pinecone
api_key = os.getenv("PINECONE_API_KEY")
index_name = "poker-memory"

pc = Pinecone(api_key=api_key)

# Check if index exists
existing_indexes = pc.list_indexes()
index_names = [idx.name for idx in existing_indexes]

if index_name not in index_names:
    print(f"Index '{index_name}' does not exist")
    exit(0)

index = pc.Index(index_name)

# Get index stats
stats = index.describe_index_stats()
print("=" * 60)
print("POKER-MEMORY INDEX STATS")
print("=" * 60)
print(f"Index name: {index_name}")
print(f"Total vectors: {stats.get('total_vector_count', 0)}")
print(f"Dimension: {stats.get('dimension', 0)}")
print(f"Namespaces: {stats.get('namespaces', {})}")

# Query for some sample vectors
print("\n" + "=" * 60)
print("SAMPLE VECTORS (First 10)")
print("=" * 60)

# Create a dummy query vector to fetch some results
import numpy as np
dummy_vector = np.random.rand(384).tolist()

results = index.query(
    vector=dummy_vector,
    top_k=10,
    include_metadata=True
)

for i, match in enumerate(results.get('matches', []), 1):
    print(f"\n{i}. ID: {match.get('id')}")
    print(f"   Score: {match.get('score', 0):.4f}")
    metadata = match.get('metadata', {})
    print(f"   Type: {metadata.get('type', 'unknown')}")
    if metadata.get('your_cards'):
        print(f"   Cards: {metadata.get('your_cards')}")
    if metadata.get('board'):
        print(f"   Board: {metadata.get('board')}")
    if metadata.get('description'):
        desc = metadata.get('description', '')
        print(f"   Description: {desc[:100]}...")
