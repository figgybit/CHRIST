#!/usr/bin/env python3
"""
Simplified Jesus Resurrection - Actually Responsive to Queries
"""

import os
import sys
import random
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class SimpleJesus:
    """Simple, conversational Jesus that actually responds to queries"""

    def __init__(self):
        self.data_dir = Path("resurrections/data/jesus_christ")
        self.gospel_content = {}
        self.load_texts()

    def load_texts(self):
        """Load all Gospel texts into memory"""
        for txt_file in self.data_dir.glob("**/*.txt"):
            try:
                with open(txt_file, 'r', encoding='utf-8') as f:
                    self.gospel_content[txt_file.name] = f.read()
            except:
                pass

    def find_relevant_text(self, query: str) -> Optional[str]:
        """Find text relevant to the query"""
        query_lower = query.lower()
        relevant_lines = []

        # Search all texts for mentions
        for filename, content in self.gospel_content.items():
            lines = content.split('\n')
            for line in lines:
                line_clean = line.strip()
                if not line_clean or len(line_clean) < 20:
                    continue

                # Check if query terms appear in the line
                if any(word in line.lower() for word in query_lower.split()):
                    # Clean up the line
                    import re
                    line_clean = re.sub(r'^\d+→\s*', '', line_clean)
                    if len(line_clean) > 20 and len(line_clean) < 300:
                        relevant_lines.append(line_clean)

        return relevant_lines[0] if relevant_lines else None

    def respond(self, query: str) -> str:
        """Generate a response to the query"""
        query_lower = query.lower()

        # Specific responses for common questions
        if "thomas" in query_lower:
            # We know Thomas is mentioned as one of the twelve
            responses = [
                "Thomas, called Didymus, one of the twelve. He was with us through all our journeys.",
                "Thomas - he who would later say 'My Lord and my God!' A faithful companion, though he doubted.",
                "You ask of Thomas? He was one of my chosen twelve, who walked with me daily.",
            ]
            # Try to find actual text about Thomas
            relevant = self.find_relevant_text("Thomas")
            if relevant and "Thomas" in relevant:
                return relevant
            return random.choice(responses)

        elif "who are you" in query_lower:
            return "I am the way, the truth, and the life."

        elif "disciples" in query_lower or "twelve" in query_lower:
            # Find text about disciples
            relevant = self.find_relevant_text("disciples twelve apostles")
            if relevant:
                return relevant
            return "The twelve were with me always - fishermen, a tax collector, men from many walks of life."

        elif "daily" in query_lower or "day" in query_lower:
            relevant = self.find_relevant_text("daily walked taught")
            if relevant:
                return relevant
            return "We walked from village to village, teaching in synagogues, healing the sick, eating with sinners."

        elif "love" in query_lower:
            relevant = self.find_relevant_text("love one another")
            if relevant:
                return relevant
            return "Love one another as I have loved you. This is my commandment."

        elif "pray" in query_lower:
            relevant = self.find_relevant_text("pray prayer father")
            if relevant:
                return relevant
            return "When you pray, pray thus: Our Father who art in heaven..."

        elif "afraid" in query_lower or "fear" in query_lower:
            return "Fear not, for I am with you. Peace I leave with you."

        elif "help" in query_lower or "heal" in query_lower:
            return "Your faith has made you whole. Go in peace."

        elif "?" in query:
            # Questions often answered with questions
            if "why" in query_lower:
                return "Why do you ask this? What does your heart tell you?"
            elif "how" in query_lower:
                return "How do you read the scriptures? What is written?"
            elif "what" in query_lower:
                return "What do you seek?"
            else:
                return "Do you believe?"

        else:
            # Try to find relevant text
            relevant = self.find_relevant_text(query)
            if relevant:
                return relevant

            # Default responses
            responses = [
                "Come and see.",
                "Follow me.",
                "Peace be with you.",
                "Your faith has saved you.",
                "The kingdom of God is at hand.",
            ]
            return random.choice(responses)

class SimpleJesusBot:
    """Simple interactive bot"""

    def __init__(self):
        print("Loading Gospel texts...")
        self.jesus = SimpleJesus()

    def run(self):
        """Run interactive conversation"""
        print("\n🕊️ Jesus: Peace be with you. What would you ask of me?\n")

        while True:
            try:
                user_input = input("You: ").strip()

                if user_input.lower() in ['quit', 'exit', 'goodbye']:
                    print("\n🕊️ Jesus: Go in peace, and may God's love be with you always.")
                    break

                if not user_input:
                    continue

                response = self.jesus.respond(user_input)
                print(f"\n🕊️ Jesus: {response}\n")

            except KeyboardInterrupt:
                print("\n\n🕊️ Jesus: Peace be with you.")
                break

if __name__ == "__main__":
    bot = SimpleJesusBot()
    bot.run()