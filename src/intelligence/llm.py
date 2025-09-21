"""
LLM integration with Ollama for local AI capabilities.
"""

import os
import json
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime


class OllamaLLM:
    """Ollama integration for local LLM inference."""

    def __init__(
        self,
        model_name: str = None,
        base_url: str = "http://localhost:11434",
        timeout: int = 30
    ):
        """
        Initialize Ollama LLM.

        Args:
            model_name: Name of the Ollama model to use
            base_url: Ollama server URL
            timeout: Request timeout in seconds
        """
        self.base_url = base_url
        self.timeout = timeout

        # Auto-detect model if not specified
        if model_name is None:
            model_name = self._detect_best_model()

        self.model_name = model_name
        self._verify_connection()

    def _verify_connection(self):
        """Verify Ollama server is running."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            if response.status_code != 200:
                raise ConnectionError(f"Ollama server returned status {response.status_code}")
        except requests.exceptions.RequestException as e:
            raise ConnectionError(
                f"Cannot connect to Ollama at {self.base_url}. "
                "Make sure Ollama is running: 'ollama serve'"
            ) from e

    def _detect_best_model(self) -> str:
        """Auto-detect the best available model."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            models = response.json()

            if not models or 'models' not in models:
                raise ValueError("No models found in Ollama")

            model_list = models['models']

            # Preference order for consciousness/philosophy tasks
            preferred_models = [
                'llama2', 'mistral', 'neural-chat', 'gemma',
                'phi', 'vicuna', 'alpaca', 'wizardlm'
            ]

            # Find best available model
            for preferred in preferred_models:
                for model in model_list:
                    if preferred in model['name'].lower():
                        print(f"Auto-detected Ollama model: {model['name']}")
                        return model['name']

            # Fallback to first available model
            first_model = model_list[0]['name']
            print(f"Using first available Ollama model: {first_model}")
            return first_model

        except Exception as e:
            print(f"Error detecting models: {e}")
            # Default fallback
            return "gemma3:1b"

    def generate(
        self,
        prompt: str,
        context: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
        stream: bool = False
    ) -> str:
        """
        Generate text using Ollama.

        Args:
            prompt: The prompt to send to the model
            context: Optional context for the conversation
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response

        Returns:
            Generated text response
        """
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }

        if context:
            payload["context"] = context

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()
            return result.get("response", "")

        except requests.exceptions.Timeout:
            return "Error: Request timed out. The model may be loading or the response is taking too long."
        except requests.exceptions.RequestException as e:
            return f"Error calling Ollama: {str(e)}"

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """
        Chat with Ollama using message history.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Generated response
        """
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()
            return result.get("message", {}).get("content", "")

        except Exception as e:
            return f"Error in chat: {str(e)}"

    def get_embeddings(self, text: str) -> List[float]:
        """
        Get embeddings for text using Ollama.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        payload = {
            "model": self.model_name,
            "prompt": text
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/embeddings",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()
            return result.get("embedding", [])

        except Exception as e:
            print(f"Error getting embeddings: {str(e)}")
            return []


class RAGSystem:
    """Retrieval-Augmented Generation system using Ollama."""

    def __init__(
        self,
        llm: Optional[OllamaLLM] = None,
        vector_store: Optional[Any] = None
    ):
        """
        Initialize RAG system.

        Args:
            llm: OllamaLLM instance
            vector_store: Vector store for retrieval
        """
        self.llm = llm or OllamaLLM()
        self.vector_store = vector_store

    def query(
        self,
        question: str,
        k: int = 5,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> Dict[str, Any]:
        """
        Answer a question using RAG.

        Args:
            question: The question to answer
            k: Number of documents to retrieve
            temperature: LLM sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Dict with answer and sources
        """
        # Retrieve relevant documents
        if self.vector_store:
            results = self.vector_store.search(question, k=k)

            # Build context from retrieved documents
            context_parts = []
            sources = []

            for i, result in enumerate(results, 1):
                doc = result.get('document', '')
                source = result.get('metadata', {}).get('source', 'unknown')

                context_parts.append(f"[Document {i}]:\n{doc}\n")
                sources.append({
                    'source': source,
                    'score': result.get('score', 0),
                    'preview': doc[:200] + '...' if len(doc) > 200 else doc
                })

            context = "\n".join(context_parts)

            # Create RAG prompt
            prompt = f"""You are an AI assistant helping to answer questions about consciousness, philosophy, and personal memories based on the provided documents.

Context from relevant documents:
{context}

Question: {question}

Please provide a thoughtful answer based on the context above. If the context doesn't contain enough information, say so. Be specific and reference the documents when possible.

Answer:"""

        else:
            # No vector store, just answer directly
            prompt = question
            sources = []

        # Generate answer
        answer = self.llm.generate(
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )

        return {
            'question': question,
            'answer': answer,
            'sources': sources,
            'model': self.llm.model_name
        }

    def chat(
        self,
        message: str,
        history: List[Dict[str, str]] = None,
        use_context: bool = True,
        k: int = 3
    ) -> Dict[str, Any]:
        """
        Chat with RAG-enhanced responses.

        Args:
            message: User message
            history: Conversation history
            use_context: Whether to use vector store context
            k: Number of documents to retrieve

        Returns:
            Response with answer and metadata
        """
        history = history or []

        # Retrieve context if requested
        context_info = ""
        sources = []

        if use_context and self.vector_store:
            results = self.vector_store.search(message, k=k)

            if results:
                context_parts = []
                for result in results:
                    doc = result.get('document', '')[:300]  # Limit context length
                    context_parts.append(doc)
                    sources.append(result.get('metadata', {}))

                context_info = "\n\n".join(context_parts)

        # Build messages
        messages = history.copy()

        if context_info:
            # Add context as system message
            messages.insert(0, {
                "role": "system",
                "content": f"You are a helpful AI assistant with access to personal consciousness data. Use this context to answer questions:\n\n{context_info}"
            })

        messages.append({"role": "user", "content": message})

        # Get response
        response = self.llm.chat(messages)

        return {
            'response': response,
            'sources': sources,
            'model': self.llm.model_name
        }


def test_ollama():
    """Test Ollama connection and capabilities."""
    print("Testing Ollama integration...")

    try:
        # Initialize Ollama
        llm = OllamaLLM()
        print(f"✅ Connected to Ollama using model: {llm.model_name}")

        # Test generation
        response = llm.generate(
            "What is consciousness?",
            max_tokens=100
        )
        print(f"\n📝 Test response:\n{response[:200]}...")

        # Test available models
        response = requests.get("http://localhost:11434/api/tags")
        models = response.json()
        print(f"\n📦 Available models:")
        for model in models.get('models', []):
            size_gb = model['size'] / (1024**3)
            print(f"  - {model['name']}: {size_gb:.1f} GB")

        return True

    except Exception as e:
        print(f"❌ Ollama test failed: {e}")
        return False


if __name__ == "__main__":
    test_ollama()