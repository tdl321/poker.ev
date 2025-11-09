#!/usr/bin/env python3
"""
Re-index poker knowledge base into Pinecone

This script:
1. Clears existing poker-knowledge index
2. Loads all markdown files from poker_ev/rag/knowledge_base/
3. Splits documents into chunks with optimal size
4. Vectorizes and uploads to Pinecone
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

load_dotenv()

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore

try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings

from pinecone import Pinecone, ServerlessSpec

def clear_index(pc, index_name):
    """Clear all vectors from index"""
    print(f"\n🗑️  Clearing index: {index_name}")
    try:
        index = pc.Index(index_name)

        # Delete all vectors by deleting all IDs
        stats = index.describe_index_stats()
        vector_count = stats.get('total_vector_count', 0)

        if vector_count > 0:
            print(f"   Found {vector_count} existing vectors")
            # Delete all in default namespace
            index.delete(delete_all=True, namespace='')
            print(f"   ✅ Cleared all vectors")
        else:
            print(f"   Index already empty")

    except Exception as e:
        print(f"   ⚠️  Error clearing index: {e}")

def main():
    print("=" * 80)
    print("POKER KNOWLEDGE BASE INDEXING")
    print("=" * 80)

    # Get Pinecone API key
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        print("❌ PINECONE_API_KEY not found in environment")
        sys.exit(1)

    # Configuration
    index_name = "poker-knowledge"
    knowledge_base_dir = project_root / "poker_ev" / "rag" / "knowledge_base"

    print(f"\n📁 Knowledge base directory: {knowledge_base_dir}")

    if not knowledge_base_dir.exists():
        print(f"❌ Directory not found: {knowledge_base_dir}")
        sys.exit(1)

    # Count markdown files
    md_files = list(knowledge_base_dir.glob("*.md"))
    print(f"   Found {len(md_files)} markdown files")
    for f in sorted(md_files):
        size_kb = f.stat().st_size / 1024
        print(f"   - {f.name} ({size_kb:.1f} KB)")

    # Initialize Pinecone
    print(f"\n🔌 Connecting to Pinecone...")
    pc = Pinecone(api_key=api_key)

    # Check if index exists
    existing_indexes = pc.list_indexes()
    index_names = existing_indexes.names() if hasattr(existing_indexes, 'names') else \
                  [idx['name'] for idx in existing_indexes]

    if index_name not in index_names:
        print(f"\n📝 Creating new index: {index_name}")
        pc.create_index(
            name=index_name,
            dimension=384,  # all-MiniLM-L6-v2 dimension
            metric='cosine',
            spec=ServerlessSpec(cloud='aws', region='us-east-1')
        )
        print(f"   ✅ Index created")
    else:
        print(f"\n✅ Index exists: {index_name}")
        # Clear existing data for fresh indexing
        clear_index(pc, index_name)

    # Load documents
    print(f"\n📖 Loading documents...")
    loader = DirectoryLoader(
        str(knowledge_base_dir),
        glob="*.md",
        loader_cls=TextLoader,
        loader_kwargs={'encoding': 'utf-8'},
        show_progress=True
    )
    documents = loader.load()
    print(f"   Loaded {len(documents)} documents")

    # Add metadata from filename
    for doc in documents:
        filename = Path(doc.metadata['source']).stem
        # Convert filename to readable category
        category = filename.replace('_', ' ').title()
        doc.metadata['category'] = category
        doc.metadata['source_file'] = filename
        print(f"   - {category} ({len(doc.page_content)} chars)")

    # Split documents into chunks
    print(f"\n✂️  Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,  # Increased from 500 for better context
        chunk_overlap=150,  # Increased overlap for continuity
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len
    )
    split_docs = text_splitter.split_documents(documents)
    print(f"   Created {len(split_docs)} chunks")

    # Show chunk distribution
    from collections import Counter
    category_counts = Counter(doc.metadata['category'] for doc in split_docs)
    print(f"\n   Chunk distribution by category:")
    for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   - {category}: {count} chunks")

    # Initialize embeddings
    print(f"\n🧠 Initializing embedding model...")
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'}
    )
    print(f"   ✅ Model loaded: all-MiniLM-L6-v2")

    # Create vector store and upload
    print(f"\n⬆️  Uploading to Pinecone...")
    print(f"   This may take a few minutes...")

    try:
        vector_store = PineconeVectorStore.from_documents(
            documents=split_docs,
            embedding=embeddings,
            index_name=index_name,
            namespace='',
            text_key='content'
        )
        print(f"   ✅ Upload complete!")
    except Exception as e:
        print(f"   ❌ Upload failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Verify indexing
    print(f"\n🔍 Verifying index...")
    index = pc.Index(index_name)
    stats = index.describe_index_stats()
    total_vectors = stats.get('total_vector_count', 0)

    print(f"\n" + "=" * 80)
    print("INDEXING COMPLETE")
    print("=" * 80)
    print(f"✅ Total vectors indexed: {total_vectors}")
    print(f"✅ Original documents: {len(documents)}")
    print(f"✅ Chunks created: {len(split_docs)}")
    print(f"✅ Index name: {index_name}")

    # Test query
    print(f"\n🧪 Testing search...")
    test_query = "What are the strongest starting hands?"
    results = vector_store.similarity_search(test_query, k=3)
    print(f"\nQuery: '{test_query}'")
    print(f"Found {len(results)} results:\n")
    for i, doc in enumerate(results, 1):
        category = doc.metadata.get('category', 'Unknown')
        preview = doc.page_content[:100].replace('\n', ' ')
        print(f"{i}. [{category}] {preview}...")

    print(f"\n" + "=" * 80)
    print("🎉 Knowledge base successfully indexed!")
    print("=" * 80)

if __name__ == "__main__":
    main()
