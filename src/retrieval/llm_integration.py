"""
LLM integration for RAG system and intelligent responses.
"""

import os
import json
from typing import List, Dict, Any, Optional, Generator
from datetime import datetime
import asyncio

# OpenAI integration
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Anthropic integration
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

# Local LLM support (Ollama)
try:
    import requests
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False


class LLMProvider:
    """
    Unified interface for different LLM providers.
    """

    def __init__(
        self,
        provider: str = "openai",
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ):
        """
        Initialize LLM provider.

        Args:
            provider: LLM provider (openai, anthropic, ollama, mock)
            model: Model name
            api_key: API key for the provider
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
        """
        self.provider = provider.lower()
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Set default models
        if model is None:
            model = {
                'openai': 'gpt-3.5-turbo',
                'anthropic': 'claude-3-haiku-20240307',
                'ollama': 'llama2',
                'mock': 'mock-model'
            }.get(provider, 'mock-model')

        self.model = model

        # Initialize provider clients
        if provider == 'openai' and OPENAI_AVAILABLE:
            self.client = openai.OpenAI(
                api_key=api_key or os.getenv('OPENAI_API_KEY')
            )
        elif provider == 'anthropic' and ANTHROPIC_AVAILABLE:
            self.client = anthropic.Anthropic(
                api_key=api_key or os.getenv('ANTHROPIC_API_KEY')
            )
        elif provider == 'ollama':
            self.ollama_base_url = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
        else:
            # Mock provider for testing
            self.client = None

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        stream: bool = False
    ) -> str:
        """
        Generate text using the LLM.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            stream: Whether to stream the response

        Returns:
            Generated text
        """
        if self.provider == 'openai' and OPENAI_AVAILABLE:
            return self._generate_openai(prompt, system_prompt, stream)
        elif self.provider == 'anthropic' and ANTHROPIC_AVAILABLE:
            return self._generate_anthropic(prompt, system_prompt, stream)
        elif self.provider == 'ollama':
            return self._generate_ollama(prompt, system_prompt, stream)
        else:
            return self._generate_mock(prompt, system_prompt)

    def _generate_openai(self, prompt: str, system_prompt: Optional[str], stream: bool) -> str:
        """Generate using OpenAI."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stream=stream
        )

        if stream:
            return response  # Return generator
        else:
            return response.choices[0].message.content

    def _generate_anthropic(self, prompt: str, system_prompt: Optional[str], stream: bool) -> str:
        """Generate using Anthropic."""
        kwargs = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": [{"role": "user", "content": prompt}]
        }

        if system_prompt:
            kwargs["system"] = system_prompt

        response = self.client.messages.create(**kwargs)
        return response.content[0].text

    def _generate_ollama(self, prompt: str, system_prompt: Optional[str], stream: bool) -> str:
        """Generate using Ollama local LLM."""
        url = f"{self.ollama_base_url}/api/generate"

        data = {
            "model": self.model,
            "prompt": prompt,
            "temperature": self.temperature,
            "stream": False
        }

        if system_prompt:
            data["system"] = system_prompt

        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            return f"Error calling Ollama: {str(e)}"

    def _generate_mock(self, prompt: str, system_prompt: Optional[str]) -> str:
        """Mock generation for testing."""
        return f"Mock response to: {prompt[:50]}..."

    def embed(self, text: str) -> List[float]:
        """
        Generate embeddings for text.
        """
        if self.provider == 'openai' and OPENAI_AVAILABLE:
            response = self.client.embeddings.create(
                input=text,
                model="text-embedding-ada-002"
            )
            return response.data[0].embedding
        else:
            # Return mock embedding
            import hashlib
            hash_obj = hashlib.sha256(text.encode())
            # Generate deterministic "embedding" from hash
            return [float(b) / 255.0 for b in hash_obj.digest()[:384]]


class RAGSystem:
    """
    Retrieval-Augmented Generation system.
    """

    def __init__(
        self,
        vector_store,
        llm_provider: LLMProvider,
        system_context: Optional[str] = None
    ):
        """
        Initialize RAG system.

        Args:
            vector_store: Vector store for retrieval
            llm_provider: LLM provider for generation
            system_context: System context about the user
        """
        self.vector_store = vector_store
        self.llm = llm_provider
        self.system_context = system_context or "You are a helpful AI assistant with access to personal memories and data."

    def query(
        self,
        question: str,
        k: int = 5,
        use_context: bool = True,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Answer a question using RAG.

        Args:
            question: User question
            k: Number of documents to retrieve
            use_context: Whether to use retrieved context
            metadata_filter: Optional metadata filter for retrieval

        Returns:
            Response with answer and sources
        """
        # Retrieve relevant documents
        if use_context:
            retrieved_docs = self.vector_store.search(
                query=question,
                k=k,
                filter=metadata_filter
            )
        else:
            retrieved_docs = []

        # Build context
        context = self._build_context(retrieved_docs)

        # Generate answer
        answer = self._generate_answer(question, context)

        return {
            'answer': answer,
            'sources': retrieved_docs,
            'context_used': context,
            'timestamp': datetime.now().isoformat()
        }

    def _build_context(self, documents: List[Dict[str, Any]]) -> str:
        """
        Build context from retrieved documents.
        """
        if not documents:
            return ""

        context_parts = ["Based on the following information:\n"]

        for i, doc in enumerate(documents, 1):
            metadata = doc.get('metadata', {})
            timestamp = metadata.get('timestamp', 'unknown time')
            source = metadata.get('source', 'unknown source')

            context_parts.append(f"\n[{i}] From {source} at {timestamp}:")
            context_parts.append(doc['document'][:500])  # Limit length

        return "\n".join(context_parts)

    def _generate_answer(self, question: str, context: str) -> str:
        """
        Generate answer using LLM.
        """
        if context:
            prompt = f"""Context:
{context}

Question: {question}

Please provide a comprehensive answer based on the context above. If the context doesn't contain relevant information, say so."""
        else:
            prompt = question

        system_prompt = f"""{self.system_context}

Guidelines:
- Be accurate and cite sources when available
- If you're not sure, say so
- Be concise but thorough
- Respect privacy and confidentiality"""

        return self.llm.generate(prompt, system_prompt)

    def reflect(
        self,
        time_period: Optional[Dict[str, str]] = None,
        focus_areas: Optional[List[str]] = None
    ) -> str:
        """
        Generate reflective insights.

        Args:
            time_period: Time range for reflection
            focus_areas: Areas to focus on

        Returns:
            Reflective insights
        """
        # Build reflection query
        query_parts = ["Generate insights about"]

        if time_period:
            query_parts.append(f"the period from {time_period.get('start', 'beginning')} to {time_period.get('end', 'now')}")

        if focus_areas:
            query_parts.append(f"focusing on {', '.join(focus_areas)}")

        query = " ".join(query_parts)

        # Retrieve relevant memories
        retrieved = self.vector_store.search(query, k=10)

        # Generate reflection
        context = self._build_context(retrieved)

        prompt = f"""Based on these memories and experiences:
{context}

Please provide a thoughtful reflection covering:
1. Key themes and patterns
2. Important moments or turning points
3. Growth and changes observed
4. Lessons learned
5. Recommendations for the future

Focus areas: {focus_areas or ['general life experiences']}"""

        return self.llm.generate(prompt, "You are a thoughtful life coach providing insights based on personal experiences.")

    def chat(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        persona: Optional[str] = None
    ) -> str:
        """
        Chat with consciousness simulation.

        Args:
            message: User message
            conversation_history: Previous messages
            persona: Persona to use

        Returns:
            Response
        """
        # Retrieve relevant context
        retrieved = self.vector_store.search(message, k=3)
        context = self._build_context(retrieved)

        # Build conversation prompt
        prompt_parts = []

        if conversation_history:
            for msg in conversation_history[-5:]:  # Last 5 messages
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                prompt_parts.append(f"{role.capitalize()}: {content}")

        prompt_parts.append(f"User: {message}")

        if context:
            prompt_parts.insert(0, f"Relevant memories:\n{context}\n")

        prompt = "\n".join(prompt_parts)

        # Set persona
        if persona:
            system = f"You are responding as '{persona}' persona based on the user's consciousness data. {self.system_context}"
        else:
            system = self.system_context

        return self.llm.generate(prompt, system)


class PromptTemplates:
    """
    Collection of prompt templates for different use cases.
    """

    @staticmethod
    def question_answer(question: str, context: str) -> str:
        """Template for Q&A."""
        return f"""Context: {context}

Question: {question}

Instructions: Answer the question based solely on the context provided. If the context doesn't contain the answer, say "I don't have enough information to answer that."

Answer:"""

    @staticmethod
    def summarization(text: str, style: str = "concise") -> str:
        """Template for summarization."""
        styles = {
            "concise": "Provide a brief, concise summary in 2-3 sentences.",
            "detailed": "Provide a comprehensive summary covering all main points.",
            "bullet": "Provide a bullet-point summary of key points."
        }

        return f"""Text to summarize:
{text}

{styles.get(style, styles['concise'])}

Summary:"""

    @staticmethod
    def reflection(memories: str, timeframe: str) -> str:
        """Template for reflection."""
        return f"""Memories from {timeframe}:
{memories}

Based on these memories, provide a reflective analysis covering:
1. Dominant themes and patterns
2. Emotional journey
3. Key relationships and interactions
4. Personal growth observed
5. Lessons and insights

Reflection:"""

    @staticmethod
    def personality_simulation(context: str, traits: List[str], message: str) -> str:
        """Template for personality simulation."""
        traits_str = ", ".join(traits)
        return f"""Personal context:
{context}

Personality traits: {traits_str}

Respond to the following message in a way that reflects these personality traits and personal history:

Message: {message}

Response:"""