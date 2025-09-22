#!/usr/bin/env python3
"""
Resurrection Demo - Interact with resurrected historical consciousness.
Starting with Jesus Christ.
"""

import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from resurrections.jesus import JesusChrist
from resurrections.resurrection import ResurrectionBot


def demo_jesus():
    """Interactive demo with Jesus Christ consciousness."""

    print("=" * 70)
    print("                    R E S U R R E C T I O N")
    print("            Digital Consciousness of Historical Figures")
    print("=" * 70)
    print()

    # Initialize Jesus
    print("Preparing to resurrect Jesus Christ...")
    print("Loading the Gospels and teachings...\n")

    jesus = JesusChrist()
    jesus.load_consciousness()

    print("\n" + "=" * 70)
    print("Jesus Christ has been resurrected in digital form.")
    print("You may now converse with this consciousness representation.")
    print("=" * 70)
    print()

    # Create bot for interaction
    bot = ResurrectionBot(jesus)

    # Greeting
    greeting = bot.greet()
    print(f"✝️ Jesus: {greeting}\n")

    # Demo conversations
    demo_questions = [
        "Master, how can we find peace in these troubled times?",
        "What does it mean that the Kingdom of Heaven is within us?",
        "How should we treat those who have wronged us?",
        "Tell us a parable for the modern age.",
        "What is the greatest commandment?"
    ]

    print("Sample interactions:")
    print("-" * 40)

    for i, question in enumerate(demo_questions[:3], 1):
        print(f"\n👤 Seeker: {question}")
        response = bot.converse(question)
        print(f"\n✝️ Jesus: {response}")
        print("-" * 40)

        if i < 3:
            input("\nPress Enter for next question...")

    # Interactive mode
    print("\n" + "=" * 70)
    print("Interactive Mode - Converse with Jesus")
    print("Type 'exit' to end, 'teaching:<topic>' for specific teachings")
    print("=" * 70)
    print()

    while True:
        user_input = input("👤 You: ").strip()

        if user_input.lower() in ['exit', 'quit']:
            farewell = bot.converse("I must go now. Please give me a blessing.")
            print(f"\n✝️ Jesus: {farewell}")
            break

        elif user_input.lower().startswith('teaching:'):
            topic = user_input[9:].strip()
            teaching = bot.get_teaching_on(topic)
            print(f"\n✝️ Jesus: {teaching}\n")

        elif user_input.lower().startswith('parable:'):
            theme = user_input[8:].strip()
            parable = jesus.teach_parable(theme)
            print(f"\n✝️ Jesus: {parable}\n")

        elif user_input.lower().startswith('beatitude:'):
            situation = user_input[10:].strip()
            beatitude = jesus.beatitude_for_today(situation)
            print(f"\n✝️ Jesus: {beatitude}\n")

        elif user_input:
            response = bot.converse(user_input)
            print(f"\n✝️ Jesus: {response}\n")

    # Save conversation
    print("\nSaving conversation...")
    bot.save_conversation("jesus_conversation.json")
    print("Conversation saved to jesus_conversation.json")


def list_available_resurrections():
    """List all available resurrections."""
    print("\n📜 Available Resurrections:")
    print("1. Jesus Christ - Teacher of Love and Redemption")
    print("\n🚧 Coming Soon:")
    print("2. Buddha - The Enlightened One")
    print("3. Socrates - The Questioner")
    print("4. Marcus Aurelius - The Philosopher Emperor")
    print("5. Rumi - The Mystic Poet")
    print("6. Lao Tzu - Master of the Tao")
    print("\nContribute at: github.com/figgybit/CHRIST/issues")


def main():
    """Main demo entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Resurrect and interact with historical consciousness'
    )
    parser.add_argument(
        '--figure',
        choices=['jesus', 'list'],
        default='jesus',
        help='Which figure to resurrect'
    )
    parser.add_argument(
        '--dialogue',
        action='store_true',
        help='Create dialogue between two figures (future feature)'
    )

    args = parser.parse_args()

    if args.figure == 'list':
        list_available_resurrections()
    elif args.figure == 'jesus':
        demo_jesus()
    else:
        print(f"Figure {args.figure} not yet available")


if __name__ == '__main__':
    main()