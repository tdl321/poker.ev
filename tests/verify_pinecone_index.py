"""
Quick script to verify Pinecone index has poker knowledge data
"""
import os
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_community.embeddings import SentenceTransformerEmbeddings

load_dotenv()

# Initialize Pinecone
api_key = os.getenv("PINECONE_API_KEY")
index_name = "poker-knowledge"

pc = Pinecone(api_key=api_key)
index = pc.Index(index_name)

# Get index stats
stats = index.describe_index_stats()
print("=" * 60)
print("PINECONE INDEX STATS")
print("=" * 60)
print(f"Index name: {index_name}")
print(f"Total vectors: {stats.get('total_vector_count', 0)}")
print(f"Dimension: {stats.get('dimension', 0)}")
print(f"Namespaces: {stats.get('namespaces', {})}")

# Test search with LangChain
print("\n" + "=" * 60)
print("TESTING SEARCH")
print("=" * 60)

embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
vector_store = PineconeVectorStore(
    index_name=index_name,
    embedding=embeddings,
    text_key="content"  # Match the field name in Pinecone metadata
)

# Search for poker strategy
query = "strongest starting hands in poker"
results = vector_store.similarity_search(query, k=3)

print(f"\nQuery: '{query}'")
print(f"Found {len(results)} results:\n")

for i, doc in enumerate(results, 1):
    print(f"Result {i}:")
    print(f"  Category: {doc.metadata.get('category', 'Unknown')}")
    print(f"  Content: {doc.page_content[:150]}...")
    print()

print("=" * 60)
print("✅ Pinecone index verified!")
print("=" * 60)
