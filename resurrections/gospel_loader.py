#!/usr/bin/env python3
"""
Gospel Text Loader and Indexer for Resurrection System
Loads biblical texts and provides intelligent search and retrieval
"""

import os
import json
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class GospelPassage:
    """Represents a single Gospel passage"""
    book: str
    chapter: int
    verses: str
    text: str
    category: str  # canonical, teachings, daily_life, etc.

    def __str__(self):
        return f"{self.book.title()} {self.chapter}:{self.verses} - {self.text[:100]}..."

class GospelLoader:
    """Loads and indexes Gospel texts for efficient retrieval"""

    def __init__(self, data_dir: str = "data/jesus_christ"):
        self.data_dir = Path(data_dir)
        self.passages: List[GospelPassage] = []
        self.index: Dict[str, List[int]] = {}  # word -> passage indices
        self.topics: Dict[str, List[int]] = {
            "love": [],
            "faith": [],
            "prayer": [],
            "forgiveness": [],
            "kingdom": [],
            "disciples": [],
            "healing": [],
            "parables": [],
            "daily_life": [],
            "teaching": []
        }

    def load_all_texts(self):
        """Load all Gospel texts from the data directory"""
        logger.info(f"Loading Gospel texts from {self.data_dir}")

        # Load canonical gospels
        canonical_dir = self.data_dir / "canonical"
        if canonical_dir.exists():
            for gospel_file in canonical_dir.glob("*.txt"):
                self._load_gospel_file(gospel_file, "canonical")

        # Load teachings
        teachings_dir = self.data_dir / "teachings"
        if teachings_dir.exists():
            for teaching_file in teachings_dir.glob("*.txt"):
                self._load_gospel_file(teaching_file, "teachings")

        # Load daily life
        daily_life_dir = self.data_dir / "daily_life"
        if daily_life_dir.exists():
            for life_file in daily_life_dir.glob("*.txt"):
                self._load_gospel_file(life_file, "daily_life")

        # Build search index
        self._build_index()

        logger.info(f"Loaded {len(self.passages)} passages")

    def _load_gospel_file(self, filepath: Path, category: str):
        """Load a single Gospel text file"""
        book = filepath.stem

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Split into logical passages (by double newlines or chapter markers)
            sections = re.split(r'\n\n+|CHAPTER \d+', content)

            for section in sections:
                if not section.strip():
                    continue

                # Extract chapter if present
                chapter_match = re.search(r'(\d+)[:\-→]', section[:50])
                chapter = int(chapter_match.group(1)) if chapter_match else 1

                # Clean the text
                text = re.sub(r'^\s*\d+→\s*', '', section, flags=re.MULTILINE)
                text = ' '.join(text.split())

                if len(text) > 20:  # Skip very short fragments
                    passage = GospelPassage(
                        book=book,
                        chapter=chapter,
                        verses="",  # Could extract if needed
                        text=text,
                        category=category
                    )
                    self.passages.append(passage)

        except Exception as e:
            logger.error(f"Error loading {filepath}: {e}")

    def _build_index(self):
        """Build word and topic indices for fast searching"""
        for i, passage in enumerate(self.passages):
            # Build word index
            words = set(re.findall(r'\b\w+\b', passage.text.lower()))
            for word in words:
                if word not in self.index:
                    self.index[word] = []
                self.index[word].append(i)

            # Categorize by topics
            text_lower = passage.text.lower()
            for topic, indices in self.topics.items():
                if self._matches_topic(text_lower, topic):
                    indices.append(i)

    def _matches_topic(self, text: str, topic: str) -> bool:
        """Check if text matches a topic"""
        topic_keywords = {
            "love": ["love", "loved", "loveth", "charity", "compassion"],
            "faith": ["faith", "believe", "belief", "trust"],
            "prayer": ["pray", "prayer", "prayed", "praying"],
            "forgiveness": ["forgive", "forgiven", "forgiveness", "mercy"],
            "kingdom": ["kingdom", "heaven", "eternal"],
            "disciples": ["disciples", "apostles", "peter", "john", "james"],
            "healing": ["heal", "healed", "healing", "whole", "sick"],
            "parables": ["parable", "sower", "seed", "vineyard"],
            "daily_life": ["eat", "walked", "sat", "house", "village"],
            "teaching": ["teach", "taught", "teaching", "rabbi", "master"]
        }

        keywords = topic_keywords.get(topic, [topic])
        return any(keyword in text for keyword in keywords)

    def search(self, query: str, limit: int = 5) -> List[GospelPassage]:
        """Search for relevant passages"""
        query_words = set(re.findall(r'\b\w+\b', query.lower()))

        # Find passages containing query words
        passage_scores: Dict[int, int] = {}
        for word in query_words:
            if word in self.index:
                for idx in self.index[word]:
                    passage_scores[idx] = passage_scores.get(idx, 0) + 1

        # Sort by relevance
        sorted_indices = sorted(passage_scores.keys(),
                               key=lambda x: passage_scores[x],
                               reverse=True)

        # Return top results
        results = []
        for idx in sorted_indices[:limit]:
            results.append(self.passages[idx])

        return results

    def get_by_topic(self, topic: str, limit: int = 5) -> List[GospelPassage]:
        """Get passages related to a specific topic"""
        if topic not in self.topics:
            return []

        indices = self.topics[topic][:limit]
        return [self.passages[i] for i in indices]

    def get_random_teaching(self) -> Optional[GospelPassage]:
        """Get a random teaching passage"""
        import random
        teaching_passages = [p for p in self.passages if p.category == "teachings"]
        if teaching_passages:
            return random.choice(teaching_passages)
        return None

    def get_conversational_examples(self) -> List[str]:
        """Get examples of Jesus's conversational style"""
        examples = []
        for passage in self.passages:
            if "?" in passage.text or "thou" in passage.text.lower():
                # Extract dialogue-like portions
                sentences = re.split(r'[.!?]', passage.text)
                for sentence in sentences:
                    if len(sentence) > 20 and len(sentence) < 200:
                        if any(word in sentence.lower() for word in
                               ["said", "saith", "answered", "asked"]):
                            examples.append(sentence.strip())

        return examples[:10]  # Return top 10 examples