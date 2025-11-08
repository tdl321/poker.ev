"""
Document Loader for poker.ev RAG system

Loads and processes poker strategy documents.
"""

import os
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class Document:
    """
    Represents a document chunk for RAG
    """
    content: str
    metadata: Dict[str, str]
    embedding: List[float] = None

    def __repr__(self):
        return f"Document(content={self.content[:50]}..., metadata={self.metadata})"


class PokerDocumentLoader:
    """
    Loads poker strategy documents from knowledge base

    Reads markdown files and splits them into chunks for vector storage.
    """

    def __init__(
        self,
        knowledge_base_dir: str = None,
        chunk_size: int = 500,
        chunk_overlap: int = 100
    ):
        """
        Initialize document loader

        Args:
            knowledge_base_dir: Path to knowledge base directory
            chunk_size: Maximum size of each chunk (in characters)
            chunk_overlap: Overlap between chunks
        """
        if knowledge_base_dir is None:
            # Default to poker_ev/rag/knowledge_base
            current_dir = Path(__file__).parent
            knowledge_base_dir = current_dir / "knowledge_base"

        self.knowledge_base_dir = Path(knowledge_base_dir)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def load_markdown_file(self, file_path: Path) -> List[Document]:
        """
        Load a single markdown file and split into chunks

        Args:
            file_path: Path to markdown file

        Returns:
            List of Document objects
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract metadata from filename
            filename = file_path.stem
            category = filename.replace('_', ' ').title()

            # Split into chunks
            chunks = self._split_markdown(content)

            # Create Document objects
            documents = []
            for i, chunk in enumerate(chunks):
                doc = Document(
                    content=chunk,
                    metadata={
                        'source': str(file_path),
                        'category': category,
                        'filename': file_path.name,
                        'chunk_id': i,
                        'total_chunks': len(chunks)
                    }
                )
                documents.append(doc)

            logger.info(f"Loaded {len(documents)} chunks from {file_path.name}")
            return documents

        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            return []

    def _split_markdown(self, text: str) -> List[str]:
        """
        Split markdown text into chunks

        Tries to split on:
        1. Headers (##, ###)
        2. Paragraphs (double newlines)
        3. Character limit

        Args:
            text: Markdown text

        Returns:
            List of text chunks
        """
        chunks = []
        current_chunk = ""

        # Split by lines
        lines = text.split('\n')

        for line in lines:
            # Check if adding this line exceeds chunk size
            if len(current_chunk) + len(line) + 1 > self.chunk_size:
                # If current chunk is not empty, save it
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())

                # Start new chunk
                # Include overlap from previous chunk
                if chunks and self.chunk_overlap > 0:
                    overlap_text = current_chunk[-self.chunk_overlap:]
                    current_chunk = overlap_text + '\n' + line
                else:
                    current_chunk = line
            else:
                # Add line to current chunk
                if current_chunk:
                    current_chunk += '\n' + line
                else:
                    current_chunk = line

        # Add final chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks

    def load_all_documents(self) -> List[Document]:
        """
        Load all markdown files from knowledge base

        Returns:
            List of all Document objects
        """
        if not self.knowledge_base_dir.exists():
            logger.error(f"Knowledge base directory not found: {self.knowledge_base_dir}")
            return []

        all_documents = []

        # Find all .md files
        md_files = list(self.knowledge_base_dir.glob("*.md"))

        if not md_files:
            logger.warning(f"No markdown files found in {self.knowledge_base_dir}")
            return []

        logger.info(f"Found {len(md_files)} markdown files")

        # Load each file
        for md_file in md_files:
            documents = self.load_markdown_file(md_file)
            all_documents.extend(documents)

        logger.info(f"Loaded total of {len(all_documents)} document chunks")
        return all_documents

    def get_document_by_category(self, category: str) -> List[Document]:
        """
        Get documents filtered by category

        Args:
            category: Category name (e.g., "Hand Rankings")

        Returns:
            List of matching documents
        """
        all_docs = self.load_all_documents()
        return [doc for doc in all_docs if doc.metadata['category'].lower() == category.lower()]


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    loader = PokerDocumentLoader()
    documents = loader.load_all_documents()

    print(f"\n✅ Loaded {len(documents)} document chunks")
    print(f"\nCategories:")
    categories = set(doc.metadata['category'] for doc in documents)
    for category in sorted(categories):
        count = sum(1 for doc in documents if doc.metadata['category'] == category)
        print(f"  • {category}: {count} chunks")

    # Show example document
    if documents:
        print(f"\n📄 Example document chunk:")
        print(f"Category: {documents[0].metadata['category']}")
        print(f"Source: {documents[0].metadata['filename']}")
        print(f"Content preview: {documents[0].content[:200]}...")
