#!/usr/bin/env python3
"""
Gospel-Based Jesus Christ Resurrection
Provides biblically-grounded, conversational responses using actual Gospel texts
"""

import os
import sys
import json
import random
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from resurrections.resurrection import Resurrection
from resurrections.gospel_loader import GospelLoader, GospelPassage

class JesusGospelBased(Resurrection):
    """Jesus Christ resurrection grounded in Gospel texts"""

    def __init__(self):
        super().__init__(
            name="Jesus of Nazareth",
            title="The Christ",
            time_period="~4 BC - ~30 AD",
            core_teachings=[
                "Love God with all your heart",
                "Love your neighbor as yourself",
                "The Kingdom of God is within you",
                "Blessed are the poor in spirit",
                "Do unto others as you would have them do unto you",
                "Judge not, that ye be not judged",
                "Ask and it shall be given"
            ],
            personality_traits=[
                "speaks simply and directly",
                "uses everyday examples",
                "asks questions to make people think",
                "shows compassion to outcasts",
                "gentle with the broken",
                "bold with the self-righteous",
                "tells stories to illustrate truths"
            ]
        )

        # Load Gospel texts
        self.gospel_loader = GospelLoader("resurrections/data/jesus_christ")
        self.gospel_loader.load_all_texts()

        # Conversational patterns from the Gospels
        self.response_patterns = [
            "Verily I say unto thee",
            "Why do you ask",
            "Have you not read",
            "It is written",
            "Come and see",
            "Your faith has made you whole",
            "Go and sin no more",
            "Peace be with you"
        ]

    def generate_response(self, query: str, context: Dict[str, Any]) -> str:
        """Generate a biblically-grounded, conversational response"""

        # Search for relevant Gospel passages
        relevant_passages = self.gospel_loader.search(query, limit=3)

        # Check for specific topics
        query_lower = query.lower()
        topic_response = self._check_topic_response(query_lower)
        if topic_response:
            return topic_response

        # Generate response based on Gospel patterns
        if "who are you" in query_lower or "are you jesus" in query_lower:
            return self._identity_response()

        elif any(word in query_lower for word in ["daily", "day", "companions", "disciples"]):
            return self._daily_life_response(relevant_passages)

        elif any(word in query_lower for word in ["love", "loving", "heart"]):
            return self._love_response(relevant_passages)

        elif any(word in query_lower for word in ["pray", "prayer", "praying"]):
            return self._prayer_response(relevant_passages)

        elif any(word in query_lower for word in ["sin", "forgive", "forgiveness"]):
            return self._forgiveness_response(relevant_passages)

        elif any(word in query_lower for word in ["afraid", "fear", "worried"]):
            return self._fear_response(relevant_passages)

        elif "?" in query:
            # Answer questions with questions, as Jesus often did
            return self._question_response(query)

        else:
            # Default conversational response using Gospel passages
            return self._general_response(relevant_passages, query)

    def _identity_response(self) -> str:
        """Response about identity"""
        responses = [
            "I am the way, the truth, and the life.",
            "Who do you say that I am?",
            "I am he who speaks to you.",
            "Come and see."
        ]
        return random.choice(responses)

    def _daily_life_response(self, passages: List[GospelPassage]) -> str:
        """Response about daily life and companions"""
        daily_passages = self.gospel_loader.get_by_topic("daily_life", limit=2)

        if daily_passages:
            passage = random.choice(daily_passages)
            intro = random.choice([
                "I walked with fishermen and tax collectors.",
                "My days were spent among the people.",
                "We went about doing good."
            ])
            return f"{intro} {self._extract_relevant_sentence(passage.text)}"

        return "I walked among the villages, teaching and healing. The twelve were with me always."

    def _love_response(self, passages: List[GospelPassage]) -> str:
        """Response about love"""
        love_passages = self.gospel_loader.get_by_topic("love", limit=2)

        if love_passages:
            passage = random.choice(love_passages)
            excerpt = self._extract_relevant_sentence(passage.text, "love")
            if excerpt:
                return excerpt

        return "Love one another as I have loved you. Greater love has no man than this."

    def _prayer_response(self, passages: List[GospelPassage]) -> str:
        """Response about prayer"""
        prayer_passages = self.gospel_loader.get_by_topic("prayer", limit=2)

        if prayer_passages:
            passage = random.choice(prayer_passages)
            excerpt = self._extract_relevant_sentence(passage.text, "pray")
            if excerpt:
                return excerpt

        return "When you pray, go into your room and shut the door. Your Father who sees in secret will reward you."

    def _forgiveness_response(self, passages: List[GospelPassage]) -> str:
        """Response about forgiveness"""
        forgive_passages = self.gospel_loader.get_by_topic("forgiveness", limit=2)

        if forgive_passages:
            passage = random.choice(forgive_passages)
            excerpt = self._extract_relevant_sentence(passage.text, "forgive")
            if excerpt:
                return excerpt

        return "If you forgive others their trespasses, your heavenly Father will also forgive you."

    def _fear_response(self, passages: List[GospelPassage]) -> str:
        """Response about fear and worry"""
        responses = [
            "Why are you afraid? Have you still no faith?",
            "Fear not, little flock.",
            "Let not your heart be troubled. Believe in God; believe also in me.",
            "Peace I leave with you. Let not your heart be troubled, neither let it be afraid."
        ]
        return random.choice(responses)

    def _question_response(self, query: str) -> str:
        """Respond to questions with questions, as Jesus often did"""
        if "why" in query.lower():
            responses = [
                "Why do you call me good? None is good but God alone.",
                "Why do you ask me? Have you not read the scriptures?",
                "What is written in the law? How do you read it?"
            ]
        elif "how" in query.lower():
            responses = [
                "How can you say to your brother, 'Let me take the speck out of your eye,' when there is a log in your own?",
                "If I tell you, will you believe?",
                "Do you believe this?"
            ]
        elif "what" in query.lower():
            responses = [
                "What do you seek?",
                "What would you have me do for you?",
                "What does it profit a man to gain the whole world and lose his soul?"
            ]
        else:
            responses = [
                "Do you believe?",
                "Have faith.",
                "Come and see."
            ]

        return random.choice(responses)

    def _general_response(self, passages: List[GospelPassage], query: str) -> str:
        """Generate a general response using Gospel passages"""
        if passages:
            # Use a relevant passage
            passage = passages[0]
            excerpt = self._extract_relevant_sentence(passage.text)
            if excerpt:
                return excerpt

        # Fall back to a simple teaching
        teaching = random.choice(self.core_teachings)
        return teaching

    def _extract_relevant_sentence(self, text: str, keyword: str = None) -> str:
        """Extract a relevant sentence from Gospel text"""
        import re

        # Split into sentences
        sentences = re.split(r'[.!?]', text)

        # Filter for relevant sentences
        relevant = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20 or len(sentence) > 150:
                continue

            # Check if it's dialogue (contains speech markers)
            if any(marker in sentence.lower() for marker in ["saith", "said", "answered"]):
                # Extract just the spoken part if possible
                quote_match = re.search(r'[""]([^""]+)[""]', sentence)
                if quote_match:
                    sentence = quote_match.group(1)

            # Check relevance
            if keyword and keyword.lower() not in sentence.lower():
                continue

            relevant.append(sentence)

        if relevant:
            return random.choice(relevant)

        # Return first reasonable sentence
        for sentence in sentences:
            sentence = sentence.strip()
            if 20 < len(sentence) < 150:
                return sentence

        return ""

    def _check_topic_response(self, query: str) -> Optional[str]:
        """Check for specific topic responses"""
        # Healing requests
        if any(word in query for word in ["heal", "sick", "help me", "suffering"]):
            return "Your faith has made you whole. Go in peace."

        # Blessing requests
        if any(word in query for word in ["bless", "blessing"]):
            return "Blessed are you. The kingdom of heaven is near."

        # Teaching requests
        if any(word in query for word in ["teach", "tell me", "explain"]):
            teaching = self.gospel_loader.get_random_teaching()
            if teaching:
                return self._extract_relevant_sentence(teaching.text)

        return None

class ConversationalJesusBot:
    """Interactive bot for conversing with Jesus grounded in Gospel texts"""

    def __init__(self):
        self.jesus = JesusGospelBased()
        self.context = {
            "conversation_history": [],
            "user_name": None
        }

    def greet(self):
        """Initial greeting"""
        greetings = [
            "Peace be with you. What brings you here today?",
            "Come, sit with me awhile. What troubles your heart?",
            "Welcome, friend. How may I help you?",
            "Grace and peace to you. What do you seek?"
        ]
        return random.choice(greetings)

    def respond(self, user_input: str) -> str:
        """Generate response to user input"""
        # Add to conversation history
        self.context["conversation_history"].append(user_input)

        # Generate response
        response = self.jesus.generate_response(user_input, self.context)

        # Add response to history
        self.context["conversation_history"].append(response)

        return response

    def farewell(self):
        """Farewell message"""
        farewells = [
            "Go in peace, and sin no more.",
            "May the peace of God be with you always.",
            "Remember: I am with you always, even to the end of the age.",
            "Go forth and love one another."
        ]
        return random.choice(farewells)