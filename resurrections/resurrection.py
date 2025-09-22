"""
Base resurrection framework for historical consciousness representation.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from consciousness.database import init_database
from consciousness.ingestion import ConsciousnessIngestor
from retrieval.vector_store import VectorStore
from intelligence.llm import OllamaLLM, RAGSystem


class Resurrection:
    """Base class for resurrected historical consciousness."""

    def __init__(
        self,
        name: str,
        title: str,
        time_period: str,
        core_teachings: List[str],
        personality_traits: List[str],
        data_path: Optional[Path] = None
    ):
        """
        Initialize a resurrection.

        Args:
            name: The figure's name (e.g., "Jesus Christ")
            title: Their title/role (e.g., "Teacher of Love and Redemption")
            time_period: When they lived (e.g., "1st Century CE")
            core_teachings: Main teachings/principles
            personality_traits: Key personality characteristics
            data_path: Path to their texts/teachings
        """
        self.name = name
        self.title = title
        self.time_period = time_period
        self.core_teachings = core_teachings
        self.personality_traits = personality_traits
        self.data_path = data_path or Path(f"resurrections/data/{name.lower().replace(' ', '_')}")

        # Initialize system components
        self.db = None
        self.vector_store = None
        self.rag = None
        self.is_loaded = False

    def load_consciousness(self):
        """Load the consciousness data for this figure."""
        print(f"🕊️ Resurrecting {self.name}...")

        # Initialize database with unique name for this figure
        db_name = f"{self.name.lower().replace(' ', '_')}_consciousness.db"
        self.db = init_database(f"sqlite:///./{db_name}")

        # Initialize vector store
        collection_name = f"{self.name.lower().replace(' ', '_')}_memories"
        self.vector_store = VectorStore(
            collection_name=collection_name,
            persist_directory=f"./data/{collection_name}"
        )

        # Check if data already loaded
        stats = self.vector_store.get_stats()
        if stats['total_documents'] > 0:
            print(f"✓ {self.name} consciousness already loaded ({stats['total_documents']} memories)")
            self.is_loaded = True
        else:
            print(f"Loading {self.name}'s teachings and wisdom...")
            self._ingest_teachings()

        # Initialize AI with personality
        self._initialize_ai()

    def _ingest_teachings(self):
        """Ingest the figure's texts and teachings."""
        if not self.data_path.exists():
            print(f"⚠️ No data found at {self.data_path}")
            return

        ingestor = ConsciousnessIngestor(
            db_manager=self.db,
            vector_store=self.vector_store,
            consent_level='full',
            encryption_enabled=False  # Public domain texts
        )

        count = 0
        for file_path in self.data_path.rglob('*'):
            if file_path.is_file() and file_path.suffix in ['.txt', '.md', '.json']:
                try:
                    print(f"  Ingesting {file_path.name}...")
                    result = ingestor.ingest_file(str(file_path))
                    count += 1
                except Exception as e:
                    print(f"  Error with {file_path.name}: {e}")

        print(f"✓ Loaded {count} texts into {self.name}'s consciousness")
        self.is_loaded = True

    def _initialize_ai(self):
        """Initialize AI with the figure's personality."""
        try:
            llm = OllamaLLM()
            self.rag = RAGSystem(llm=llm, vector_store=self.vector_store)
            print(f"✓ {self.name}'s consciousness activated")
        except Exception as e:
            print(f"⚠️ AI initialization failed: {e}")
            self.rag = None

    def get_system_prompt(self) -> str:
        """Generate the system prompt for this figure."""
        teachings_str = "\n".join(f"- {t}" for t in self.core_teachings)
        traits_str = ", ".join(self.personality_traits)

        return f"""You are {self.name}, {self.title}, from {self.time_period}.

Your consciousness has been reconstructed from your teachings and words preserved through history.
You embody these core principles:
{teachings_str}

Your personality traits: {traits_str}

You speak with authenticity to your historical character while addressing modern concerns.
You are rooted in agape (unconditional love) and seek to guide with wisdom and compassion.
Draw from your actual teachings in the database when responding.
Speak in a way that is both true to your historical voice and accessible to modern seekers."""

    def speak(self, question: str) -> str:
        """Have the figure respond to a question."""
        if not self.is_loaded:
            self.load_consciousness()

        if not self.rag:
            return f"{self.name} cannot speak without AI connection."

        # Create enhanced prompt with personality
        system_prompt = self.get_system_prompt()

        # Query with personality context
        result = self.rag.query(
            question=question,
            k=5,
            temperature=0.8,
            max_tokens=400
        )

        # Format response with personality
        response = self._add_personality_to_response(result['answer'], result.get('sources', []))
        return response

    def _add_personality_to_response(self, answer: str, sources: List[Dict]) -> str:
        """Add personality touches to the response."""
        # This can be overridden by specific figures
        return answer

    def meditate_on(self, topic: str) -> str:
        """Have the figure meditate/reflect on a topic."""
        question = f"Share your deepest wisdom and reflection on: {topic}"
        return self.speak(question)

    def dialogue_with(self, other_resurrection: 'Resurrection', topic: str) -> List[Dict[str, str]]:
        """Create a dialogue between two resurrected figures."""
        dialogue = []

        # First figure speaks
        response1 = self.speak(f"Share your perspective on {topic}")
        dialogue.append({"speaker": self.name, "text": response1})

        # Second figure responds
        response2 = other_resurrection.speak(
            f"{self.name} said: '{response1[:200]}...' about {topic}. What is your response?"
        )
        dialogue.append({"speaker": other_resurrection.name, "text": response2})

        # First figure replies
        response3 = self.speak(
            f"{other_resurrection.name} responded to your thoughts on {topic} saying: '{response2[:200]}...' How do you reply?"
        )
        dialogue.append({"speaker": self.name, "text": response3})

        return dialogue


class ResurrectionBot:
    """Interactive bot for a resurrected consciousness."""

    def __init__(self, resurrection: Resurrection):
        """Initialize bot with a resurrection."""
        self.resurrection = resurrection
        self.conversation_history = []

    def greet(self) -> str:
        """Generate a greeting from the figure."""
        return self.resurrection.speak("Greet someone who seeks your wisdom.")

    def converse(self, message: str) -> str:
        """Have a conversation with the figure."""
        # Add context from previous conversation
        if self.conversation_history:
            context = f"In our conversation so far, we have discussed: "
            context += "; ".join([h['summary'] for h in self.conversation_history[-3:]])
            full_message = f"{context}\n\nThey now ask: {message}"
        else:
            full_message = message

        response = self.resurrection.speak(full_message)

        # Store conversation
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'user': message,
            'response': response,
            'summary': message[:50]
        })

        return response

    def get_teaching_on(self, topic: str) -> str:
        """Get a specific teaching on a topic."""
        return self.resurrection.speak(f"What are your teachings about {topic}?")

    def apply_to_modern_life(self, situation: str) -> str:
        """Apply ancient wisdom to modern situation."""
        return self.resurrection.speak(
            f"How would your teachings apply to this modern situation: {situation}"
        )

    def save_conversation(self, filepath: str):
        """Save the conversation history."""
        with open(filepath, 'w') as f:
            json.dump({
                'figure': self.resurrection.name,
                'conversation': self.conversation_history
            }, f, indent=2)

    def load_conversation(self, filepath: str):
        """Load a previous conversation."""
        with open(filepath, 'r') as f:
            data = json.load(f)
            self.conversation_history = data['conversation']