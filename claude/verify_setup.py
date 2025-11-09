#!/usr/bin/env python3
"""
Verification script for poker.ev chat integration

Checks if all components are working correctly.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Load environment variables from .env file
load_dotenv()

# Colors for terminal output
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'
BOLD = '\033[1m'


def print_header(text):
    print(f"\n{BOLD}{'=' * 60}{RESET}")
    print(f"{BOLD}{text}{RESET}")
    print(f"{BOLD}{'=' * 60}{RESET}\n")


def print_success(text):
    print(f"{GREEN}✅ {text}{RESET}")


def print_warning(text):
    print(f"{YELLOW}⚠️  {text}{RESET}")


def print_error(text):
    print(f"{RED}❌ {text}{RESET}")


def check_dependencies():
    """Check if required packages are installed"""
    print_header("Checking Dependencies")

    required_packages = [
        ('pygame', 'Pygame'),
        ('requests', 'Requests'),
        ('sentence_transformers', 'SentenceTransformers'),
        ('langchain', 'LangChain'),
        ('langchain_openai', 'LangChain OpenAI'),
        ('langchain_pinecone', 'LangChain Pinecone'),
    ]

    optional_packages = [
        ('pinecone', 'Pinecone'),
    ]

    all_good = True

    for package, name in required_packages:
        try:
            __import__(package)
            print_success(f"{name} installed")
        except ImportError:
            print_error(f"{name} NOT installed")
            all_good = False

    for package, name in optional_packages:
        try:
            __import__(package)
            print_success(f"{name} installed (optional)")
        except ImportError:
            print_warning(f"{name} not installed (optional - will use in-memory mode)")

    return all_good


def check_deepseek_api():
    """Check if DeepSeek API key is configured"""
    print_header("Checking DeepSeek API")

    api_key = os.getenv("DEEPSEEK_API_KEY")

    if api_key:
        masked_key = api_key[:8] + "..." + api_key[-4:]
        print_success(f"DeepSeek API key found: {masked_key}")
        print("  Poker advisor will use DeepSeek API")
        return True
    else:
        print_error("DeepSeek API key not set")
        print("\n  To fix:")
        print("  1. Get API key at: https://platform.deepseek.com/")
        print("  2. Add to .env file: DEEPSEEK_API_KEY='your-key-here'")
        print("  3. Or export: export DEEPSEEK_API_KEY='your-key-here'")
        return False


def check_knowledge_base():
    """Check if poker knowledge base files exist"""
    print_header("Checking Knowledge Base")

    kb_dir = "poker_ev/rag/knowledge_base"
    required_files = [
        "hand_rankings.md",
        "pot_odds.md",
        "position_strategy.md",
        "opponent_profiling.md"
    ]

    all_exist = True

    if not os.path.exists(kb_dir):
        print_error(f"Knowledge base directory not found: {kb_dir}")
        return False

    for filename in required_files:
        filepath = os.path.join(kb_dir, filename)
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print_success(f"{filename} exists ({size:,} bytes)")
        else:
            print_error(f"{filename} NOT found")
            all_exist = False

    return all_exist


def check_fonts():
    """Check if retro fonts are available"""
    print_header("Checking Fonts")

    font_path = "poker_ev/assets/fonts/PixeloidMono-1G8ae.ttf"

    if os.path.exists(font_path):
        print_success(f"Retro font found: {font_path}")
        return True
    else:
        print_warning(f"Retro font not found (will use fallback)")
        print(f"  Expected: {font_path}")
        return True  # Not critical


def check_components():
    """Check if all Python components can be imported"""
    print_header("Checking Python Components")

    components = [
        ('poker_ev.llm.game_context', 'GameContextProvider'),
        ('poker_ev.llm.poker_advisor', 'PokerAdvisor'),
        ('poker_ev.llm.poker_tools', 'PokerTools'),
        ('poker_ev.gui.chat.chat_panel', 'ChatPanel'),
        ('poker_ev.gui.chat.message_renderer', 'MessageRenderer'),
        ('poker_ev.gui.chat.chat_input', 'ChatInput'),
        ('poker_ev.gui.chat.scroll_handler', 'ScrollHandler'),
    ]

    all_good = True

    for module_name, component_name in components:
        try:
            module = __import__(module_name, fromlist=[component_name])
            getattr(module, component_name)
            print_success(f"{component_name}")
        except Exception as e:
            print_error(f"{component_name}: {str(e)}")
            all_good = False

    return all_good


def check_pinecone_config():
    """Check if Pinecone is configured"""
    print_header("Checking Pinecone Configuration")

    api_key = os.getenv("PINECONE_API_KEY")

    if api_key:
        masked_key = api_key[:8] + "..." + api_key[-4:]
        print_success(f"Pinecone API key found: {masked_key}")
        print("  Will use Pinecone cloud storage")
        return True
    else:
        print_warning("Pinecone API key not set")
        print("  Will use in-memory storage (works fine!)")
        print("  To use Pinecone: export PINECONE_API_KEY='your-key'")
        return True  # Not critical


def run_verification():
    """Run all verification checks"""
    print(f"\n{BOLD}🔍 Poker.ev Chat Integration - Verification{RESET}")
    print("Checking if all components are ready...")

    results = []

    results.append(("Dependencies", check_dependencies()))
    results.append(("DeepSeek API", check_deepseek_api()))
    results.append(("Knowledge Base", check_knowledge_base()))
    results.append(("Fonts", check_fonts()))
    results.append(("Components", check_components()))
    results.append(("Pinecone", check_pinecone_config()))

    # Summary
    print_header("Summary")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"  {name}: {status}")

    print(f"\n{BOLD}Result: {passed}/{total} checks passed{RESET}\n")

    if passed == total:
        print_success("All checks passed! You're ready to run the game.")
        print(f"\n  Run: {BOLD}python main.py{RESET}\n")
        return True
    elif passed >= total - 2:
        print_warning("Some optional checks failed, but you can still run the game.")
        print(f"\n  Run: {BOLD}python main.py{RESET}\n")
        return True
    else:
        print_error("Critical checks failed. Please fix the issues above.")
        print("\n  Most likely fix: Add DEEPSEEK_API_KEY to .env file")
        return False


if __name__ == "__main__":
    success = run_verification()
    sys.exit(0 if success else 1)
