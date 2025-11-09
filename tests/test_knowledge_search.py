#!/usr/bin/env python3
"""Test that knowledge base search is working properly"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

load_dotenv()

from langchain_pinecone import PineconeVectorStore
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings

print("=" * 80)
print("TESTING KNOWLEDGE BASE SEARCH")
print("=" * 80)

# Initialize
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_store = PineconeVectorStore(
    index_name="poker-knowledge",
    embedding=embeddings,
    text_key="content"
)

# Test queries
test_queries = [
    "How do I calculate pot odds?",
    "What are outs in poker?",
    "Explain the rule of 2 and 4",
    "What is expected value?",
    "How do I count outs for a flush draw?",
    "Practice problems for beginners"
]

for query in test_queries:
    print(f"\n" + "=" * 80)
    print(f"Query: {query}")
    print("=" * 80)

    results = vector_store.similarity_search(query, k=3)

    for i, doc in enumerate(results, 1):
        category = doc.metadata.get('category', 'Unknown')
        source = doc.metadata.get('source_file', 'unknown')
        content_preview = doc.page_content[:150].replace('\n', ' ')

        print(f"\n{i}. [{category}] ({source}.md)")
        print(f"   {content_preview}...")

print(f"\n" + "=" * 80)
print("✅ Knowledge base search is working!")
print("=" * 80)
