#!/usr/bin/env python3
"""
Fix Pinecone index dimension mismatch

Deletes the existing poker-knowledge index and recreates it with dimension 384
"""

import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

# Load environment variables
load_dotenv()

api_key = os.getenv("PINECONE_API_KEY")
if not api_key:
    print("❌ PINECONE_API_KEY not set in .env file")
    exit(1)

print("Connecting to Pinecone...")
pc = Pinecone(api_key=api_key)

index_name = "poker-knowledge"

# Check if index exists
existing_indexes = pc.list_indexes()
if hasattr(existing_indexes, 'names'):
    index_names = existing_indexes.names()
else:
    index_names = [idx['name'] for idx in existing_indexes]

if index_name in index_names:
    print(f"🗑️  Deleting existing '{index_name}' index (dimension mismatch)...")
    pc.delete_index(index_name)
    print("✅ Index deleted")

# Create new index with correct dimension
print(f"📝 Creating '{index_name}' index with dimension 384...")
pc.create_index(
    name=index_name,
    dimension=384,  # Matches all-MiniLM-L6-v2 embeddings
    metric='cosine',
    spec=ServerlessSpec(
        cloud='aws',
        region='us-east-1'
    )
)
print("✅ Index created successfully!")
print()
print("Now run: python3 test_pinecone.py")
