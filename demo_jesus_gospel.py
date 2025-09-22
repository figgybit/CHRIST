#!/usr/bin/env python3
"""
Interactive Demo: Converse with Jesus Christ (Gospel-Based)
This demo uses actual Gospel texts to provide biblically-grounded responses
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from resurrections.jesus_gospel_based import ConversationalJesusBot

def print_header():
    """Print welcome header"""
    print("\n" + "="*60)
    print("         CONVERSE WITH JESUS CHRIST")
    print("    (Grounded in the Gospel Texts)")
    print("="*60)
    print("\nThis resurrection speaks as Jesus did in the Gospels:")
    print("- Simple, direct speech")
    print("- Parables and everyday examples")
    print("- Questions that make you think")
    print("- Compassion and wisdom")
    print("\nType 'quit' or 'goodbye' to end the conversation")
    print("="*60 + "\n")

def main():
    """Run the interactive demo"""
    print_header()

    # Initialize the bot
    print("Loading Gospel texts...")
    bot = ConversationalJesusBot()

    # Greet the user
    greeting = bot.greet()
    print(f"\n🕊️ Jesus: {greeting}\n")

    # Conversation loop
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()

            # Check for exit
            if user_input.lower() in ['quit', 'exit', 'goodbye', 'bye']:
                farewell = bot.farewell()
                print(f"\n🕊️ Jesus: {farewell}")
                break

            # Skip empty input
            if not user_input:
                continue

            # Get and display response
            response = bot.respond(user_input)
            print(f"\n🕊️ Jesus: {response}\n")

        except KeyboardInterrupt:
            print("\n\n" + bot.farewell())
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            print("Let's continue our conversation...\n")

    print("\n" + "="*60)
    print("May peace be with you always.")
    print("="*60 + "\n")

if __name__ == "__main__":
    # Check if data exists
    data_path = Path("resurrections/data/jesus_christ")
    if not data_path.exists():
        print("\n⚠️  Gospel texts not found!")
        print("Please run 'python download_gospels.py' first to download the Gospel texts.")
        print("This will provide the biblical foundation for responses.\n")
        sys.exit(1)

    # Check if any gospel files exist
    gospel_files = list(data_path.glob("**/*.txt"))
    if not gospel_files:
        print("\n⚠️  No Gospel text files found in data directory!")
        print("Please run 'python download_gospels.py' to download the texts.\n")
        sys.exit(1)

    print(f"\n✓ Found {len(gospel_files)} Gospel text files")
    main()