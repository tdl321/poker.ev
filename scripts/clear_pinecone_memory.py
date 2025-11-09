#!/usr/bin/env python3
"""
Clear Pinecone Memory Database

Deletes all hands, decisions, patterns, and sessions from Pinecone vector database.

Usage:
    python scripts/clear_pinecone_memory.py [--type hand|decision|pattern|session|all]

Options:
    --type TYPE     Type of memory to clear (default: all)
                    - hand: Delete only hand history
                    - decision: Delete only decisions (pre/post)
                    - pattern: Delete only patterns
                    - session: Delete only chat sessions
                    - all: Delete everything
    --dry-run       Show what would be deleted without actually deleting
    --yes           Skip confirmation prompt
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv()

from pinecone import Pinecone
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def confirm_deletion(memory_type: str) -> bool:
    """Ask user to confirm deletion"""
    print(f"\n⚠️  WARNING: You are about to delete ALL {memory_type.upper()} data from Pinecone!")
    print("This action CANNOT be undone.")
    response = input("\nType 'DELETE' to confirm: ")
    return response.strip() == 'DELETE'


def clear_pinecone_by_type(pc: Pinecone, index_name: str, memory_type: str, dry_run: bool = False):
    """
    Clear Pinecone vectors by type

    Args:
        pc: Pinecone client
        index_name: Name of the index
        memory_type: Type to delete (hand, decision, pattern, session, all)
        dry_run: If True, only show what would be deleted
    """
    try:
        # Connect to index
        index = pc.Index(index_name)

        # Get index stats
        stats = index.describe_index_stats()
        total_vectors = stats.get('total_vector_count', 0)

        print(f"\n📊 Current index stats:")
        print(f"   Total vectors: {total_vectors}")
        print(f"   Index: {index_name}")

        if total_vectors == 0:
            print("\n✅ Index is already empty!")
            return

        # Determine what to delete based on type
        if memory_type == 'all':
            if dry_run:
                print(f"\n🔍 DRY RUN: Would delete ALL {total_vectors} vectors from index")
            else:
                print(f"\n🗑️  Deleting ALL {total_vectors} vectors...")
                # Delete all vectors in the default namespace
                index.delete(delete_all=True)
                print("✅ All vectors deleted successfully!")

        elif memory_type == 'hand':
            # Delete only hand records (filter by metadata type='hand')
            if dry_run:
                print(f"\n🔍 DRY RUN: Would delete all vectors with type='hand'")
            else:
                print(f"\n🗑️  Deleting hand records...")
                # Use delete with filter
                index.delete(filter={"type": {"$eq": "hand"}})
                print("✅ Hand records deleted successfully!")

        elif memory_type == 'decision':
            # Delete both pre_decision and post_decision records
            if dry_run:
                print(f"\n🔍 DRY RUN: Would delete all vectors with type='pre_decision' or type='post_decision'")
            else:
                print(f"\n🗑️  Deleting decision records (pre and post)...")
                # Delete pre-decisions
                index.delete(filter={"type": {"$eq": "pre_decision"}})
                # Delete post-decisions
                index.delete(filter={"type": {"$eq": "post_decision"}})
                print("✅ Decision records deleted successfully!")

        elif memory_type == 'pattern':
            if dry_run:
                print(f"\n🔍 DRY RUN: Would delete all vectors with type='pattern'")
            else:
                print(f"\n🗑️  Deleting pattern records...")
                index.delete(filter={"type": {"$eq": "pattern"}})
                print("✅ Pattern records deleted successfully!")

        elif memory_type == 'session':
            if dry_run:
                print(f"\n🔍 DRY RUN: Would delete all vectors with type='session'")
            else:
                print(f"\n🗑️  Deleting session records...")
                index.delete(filter={"type": {"$eq": "session"}})
                print("✅ Session records deleted successfully!")

        # Show updated stats
        import time
        print("\n⏳ Waiting for index to update...")
        time.sleep(2)

        stats_after = index.describe_index_stats()
        total_after = stats_after.get('total_vector_count', 0)

        print(f"\n📊 Updated index stats:")
        print(f"   Total vectors: {total_after}")
        print(f"   Deleted: {total_vectors - total_after}")

    except Exception as e:
        logger.error(f"Error clearing Pinecone: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Clear Pinecone memory database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Delete all data (with confirmation)
  python scripts/clear_pinecone_memory.py --type all

  # Delete only hands
  python scripts/clear_pinecone_memory.py --type hand

  # Delete only decisions
  python scripts/clear_pinecone_memory.py --type decision

  # Dry run (see what would be deleted)
  python scripts/clear_pinecone_memory.py --type all --dry-run

  # Skip confirmation
  python scripts/clear_pinecone_memory.py --type all --yes
        """
    )

    parser.add_argument(
        '--type',
        choices=['hand', 'decision', 'pattern', 'session', 'all'],
        default='all',
        help='Type of memory to clear (default: all)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be deleted without actually deleting'
    )

    parser.add_argument(
        '--yes',
        action='store_true',
        help='Skip confirmation prompt'
    )

    parser.add_argument(
        '--index',
        default='poker-memory',
        help='Pinecone index name (default: poker-memory)'
    )

    args = parser.parse_args()

    # Get API key
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        print("❌ ERROR: PINECONE_API_KEY not found in environment")
        print("\nTo fix this:")
        print("1. Create a .env file in the project root")
        print("2. Add: PINECONE_API_KEY=your-api-key-here")
        print("3. Get your API key from https://www.pinecone.io/")
        sys.exit(1)

    print("=" * 70)
    print("PINECONE MEMORY CLEANER")
    print("=" * 70)
    print(f"\nAPI Key: {api_key[:15]}...")
    print(f"Index: {args.index}")
    print(f"Type: {args.type}")
    print(f"Dry Run: {args.dry_run}")

    # Initialize Pinecone
    try:
        pc = Pinecone(api_key=api_key)
        print("✅ Connected to Pinecone")
    except Exception as e:
        print(f"❌ Failed to connect to Pinecone: {e}")
        sys.exit(1)

    # Check if index exists
    try:
        existing_indexes = pc.list_indexes()
        index_names = [idx.name for idx in existing_indexes]

        if args.index not in index_names:
            print(f"❌ Index '{args.index}' does not exist")
            print(f"\nAvailable indexes: {', '.join(index_names) if index_names else 'None'}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error listing indexes: {e}")
        sys.exit(1)

    # Confirm deletion (unless --yes or --dry-run)
    if not args.dry_run and not args.yes:
        if not confirm_deletion(args.type):
            print("\n❌ Deletion cancelled by user")
            sys.exit(0)

    # Perform deletion
    success = clear_pinecone_by_type(
        pc=pc,
        index_name=args.index,
        memory_type=args.type,
        dry_run=args.dry_run
    )

    if success:
        if args.dry_run:
            print("\n✅ Dry run completed successfully!")
            print("   Run without --dry-run to actually delete the data")
        else:
            print("\n✅ Deletion completed successfully!")
    else:
        print("\n❌ Deletion failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
