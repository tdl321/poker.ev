"""
Ollama LLM Client for poker.ev

Provides interface to local Ollama models for poker advice.
"""

import requests
import json
from typing import List, Dict, Generator, Optional
import logging

logger = logging.getLogger(__name__)


class OllamaClient:
    """
    Client for interacting with local Ollama LLM API

    Ollama must be running locally: http://localhost:11434
    Install: curl -fsSL https://ollama.com/install.sh | sh
    Pull model: ollama pull phi3:mini
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "phi3:mini",
        temperature: float = 0.7,
        timeout: int = 120
    ):
        """
        Initialize Ollama client

        Args:
            base_url: Ollama API base URL
            model: Model name (e.g., "phi3:mini", "qwen2.5-coder:7b")
            temperature: Sampling temperature (0.0-1.0)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.temperature = temperature
        self.timeout = timeout

    def is_available(self) -> bool:
        """
        Check if Ollama is running and accessible

        Returns:
            True if Ollama is available, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")
            return False

    def list_models(self) -> List[Dict]:
        """
        List available models

        Returns:
            List of model dictionaries
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('models', [])
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Send chat messages and get response

        Args:
            messages: List of message dicts with 'role' and 'content'
                     Example: [{"role": "user", "content": "Hello"}]
            temperature: Override default temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Response text from model

        Raises:
            Exception: If API call fails
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature if temperature is not None else self.temperature,
            }
        }

        if max_tokens:
            payload["options"]["num_predict"] = max_tokens

        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            return data['message']['content']

        except requests.exceptions.Timeout:
            raise Exception("Ollama request timed out. The model might be too slow or not running.")
        except requests.exceptions.ConnectionError:
            raise Exception(
                "Cannot connect to Ollama. Make sure Ollama is running:\n"
                "  Installation: curl -fsSL https://ollama.com/install.sh | sh\n"
                "  Start: ollama serve\n"
                "  Pull model: ollama pull phi3:mini"
            )
        except Exception as e:
            raise Exception(f"Ollama API error: {e}")

    def stream_chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Generator[str, None, None]:
        """
        Stream chat response word by word

        Args:
            messages: List of message dicts
            temperature: Override default temperature
            max_tokens: Maximum tokens to generate

        Yields:
            Response text chunks as they arrive

        Raises:
            Exception: If API call fails
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": temperature if temperature is not None else self.temperature,
            }
        }

        if max_tokens:
            payload["options"]["num_predict"] = max_tokens

        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.timeout,
                stream=True
            )
            response.raise_for_status()

            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        if 'message' in data:
                            content = data['message'].get('content', '')
                            if content:
                                yield content
                    except json.JSONDecodeError:
                        continue

        except requests.exceptions.Timeout:
            raise Exception("Ollama request timed out")
        except requests.exceptions.ConnectionError:
            raise Exception("Cannot connect to Ollama. Is it running?")
        except Exception as e:
            raise Exception(f"Ollama streaming error: {e}")

    def embed(self, text: str) -> List[float]:
        """
        Generate embeddings for text (for RAG)

        Args:
            text: Text to embed

        Returns:
            List of embedding values

        Raises:
            Exception: If API call fails
        """
        payload = {
            "model": self.model,
            "prompt": text
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/embeddings",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            return data['embedding']

        except Exception as e:
            logger.error(f"Embedding error: {e}")
            raise Exception(f"Failed to generate embeddings: {e}")

    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate text from a prompt (legacy API)

        Args:
            prompt: Text prompt
            **kwargs: Additional options

        Returns:
            Generated text
        """
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, **kwargs)


# Example usage
if __name__ == "__main__":
    # Test Ollama connection
    client = OllamaClient(model="phi3:mini")

    if not client.is_available():
        print("❌ Ollama is not running!")
        print("\nTo start Ollama:")
        print("  1. Install: curl -fsSL https://ollama.com/install.sh | sh")
        print("  2. Start server: ollama serve")
        print("  3. Pull model: ollama pull phi3:mini")
    else:
        print("✅ Ollama is running!")
        print(f"\nAvailable models:")
        for model in client.list_models():
            print(f"  - {model.get('name', 'Unknown')}")

        # Test chat
        print("\n🧪 Testing chat...")
        try:
            response = client.chat([
                {"role": "system", "content": "You are a helpful poker advisor."},
                {"role": "user", "content": "What are pot odds?"}
            ])
            print(f"\n💬 Response: {response[:200]}...")
        except Exception as e:
            print(f"❌ Error: {e}")
