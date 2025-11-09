#!/usr/bin/env python3
"""
Test Pinecone connection and document loading
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_pinecone_connection():
    """Test Pinecone API connection"""
    print("=" * 60)
    print("Testing Pinecone Connection")
    print("=" * 60)
    print()

    # Check API key
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        print("❌ PINECONE_API_KEY not set in .env file")
        print()
        print("Steps to fix:")
        print("1. Get your API key from https://www.pinecone.io/")
        print("2. Add to .env file:")
        print("   PINECONE_API_KEY=your-api-key-here")
        return False

    print(f"✅ API key found: {api_key[:10]}...")
    print()

    # Test Pinecone import
    try:
        from pinecone import Pinecone
        print("✅ Pinecone library installed")
    except ImportError as e:
        print(f"❌ Pinecone import failed: {e}")
        print("   Run: pip install pinecone")
        return False

    # Test connection
    try:
        pc = Pinecone(api_key=api_key)
        print("✅ Connected to Pinecone")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

    # List indexes
    try:
        indexes = pc.list_indexes()
        if hasattr(indexes, 'names'):
            index_list = indexes.names()
        else:
            index_list = [idx['name'] for idx in indexes]

        print(f"✅ Found {len(index_list)} existing index(es)")
        for idx_name in index_list:
            print(f"   - {idx_name}")
    except Exception as e:
        print(f"⚠️  Could not list indexes: {e}")

    print()
    return True


def test_document_loading():
    """Test loading poker documents into Pinecone"""
    print("=" * 60)
    print("Testing Document Loading")
    print("=" * 60)
    print()

    try:
        from poker_ev.rag.pinecone_store import PineconePokerStore
        from poker_ev.rag.document_loader import PokerDocumentLoader

        # Initialize store
        print("Initializing Pinecone store...")
        store = PineconePokerStore()
        print()

        # Check if index has documents
        stats = store.get_stats()
        total_vectors = stats.get('total_vectors', 0)

        if total_vectors > 0:
            print(f"✅ Index already has {total_vectors} documents loaded")
            print()

            # Test search
            print("Testing search...")
            results = store.search("What are pocket aces?", k=2)
            print(f"Found {len(results)} results")
            if results:
                print(f"\nTop result (score: {results[0]['score']:.3f}):")
                print(f"{results[0]['content'][:200]}...")
            return True

        # Load documents
        print("Loading poker knowledge base...")
        loader = PokerDocumentLoader()
        documents = loader.load_all_documents()
        print(f"Loaded {len(documents)} document chunks")
        print()

        # Convert to format for Pinecone
        docs_for_store = []
        for doc in documents:
            docs_for_store.append({
                'id': f"{doc.metadata['filename']}_{doc.metadata['chunk_id']}",
                'content': doc.content,
                'metadata': doc.metadata
            })

        # Add to Pinecone
        print("Uploading to Pinecone (this may take 30-60 seconds)...")
        count = store.add_documents(docs_for_store)
        print(f"✅ Successfully uploaded {count} documents")
        print()

        # Verify with search
        print("Verifying with test search...")
        results = store.search("What are pocket aces?", k=2)
        print(f"✅ Found {len(results)} results")

        if results:
            print(f"\nTop result (score: {results[0]['score']:.3f}):")
            print(f"{results[0]['content'][:200]}...")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Test connection
    connection_ok = test_pinecone_connection()
    print()

    if not connection_ok:
        print("❌ Connection test failed. Fix the issues above and try again.")
        sys.exit(1)

    # Test document loading
    loading_ok = test_document_loading()
    print()

    if loading_ok:
        print("=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        print()
        print("You're ready to use the poker advisor!")
        print("Run: python3 main.py")
    else:
        print("=" * 60)
        print("❌ Document loading failed")
        print("=" * 60)
        sys.exit(1)
