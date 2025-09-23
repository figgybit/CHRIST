#!/usr/bin/env python3
"""
Conversational Resurrection Demo - Natural dialogue with historical figures.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from resurrections.jesus_conversational import JesusConversational
from resurrections.resurrection import ResurrectionBot


def conversational_demo():
    """Have a natural conversation with Jesus."""

    print("\n" + "=" * 70)
    print("           Conversation with Jesus of Nazareth")
    print("=" * 70)
    print("\nSetting: You're sitting with Jesus by the Sea of Galilee,")
    print("watching fishermen mend their nets as the sun sets.\n")

    # Initialize
    jesus = JesusConversational()
    jesus.load_consciousness()
    bot = ResurrectionBot(jesus)

    print("-" * 70)
    print("\n[Jesus turns to you with a warm smile]\n")

    # Natural conversation examples
    conversations = [
        {
            "context": "You ask about his daily life",
            "question": "Rabbi, what's a typical day like for you and the disciples?",
            "follow_up": "Do you miss your carpentry work?"
        },
        {
            "context": "You ask about his friends",
            "question": "Tell me about Peter. What's he really like?",
            "follow_up": "Does he know you call him 'the rock'?"
        },
        {
            "context": "You seek practical advice",
            "question": "Master, I'm struggling with anxiety about the future. My family, my work... What should I do?",
            "follow_up": "But how do I stop worrying?"
        },
        {
            "context": "You ask about his childhood",
            "question": "What was it like growing up in Nazareth?",
            "follow_up": "Did you always know you were different?"
        }
    ]

    # Demo a few natural exchanges
    print("Some example conversations:\n")
    print("-" * 40)

    for i, conv in enumerate(conversations[:2], 1):
        print(f"\n[{conv['context']}]\n")
        print(f"You: {conv['question']}")

        response = bot.converse(conv['question'])
        print(f"\nJesus: {response}\n")

        if conv.get('follow_up'):
            print(f"You: {conv['follow_up']}")
            follow_up_response = bot.converse(conv['follow_up'])
            print(f"\nJesus: {follow_up_response}")

        if i < 2:
            input("\n[Press Enter to continue...]")
        print("-" * 40)

    # Interactive conversation
    print("\n" + "=" * 70)
    print("Now it's your turn to talk with Jesus")
    print("(Type 'goodbye' to end the conversation)")
    print("=" * 70)
    print()

    print("[Jesus looks at you thoughtfully]\n")
    print('Jesus: "What\'s on your heart, friend?"\n')

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ['goodbye', 'farewell', 'exit']:
            farewell = bot.converse("I must go now. Please give me a blessing for my journey.")
            print(f"\n[Jesus stands and places his hand on your shoulder]\n")
            print(f"Jesus: {farewell}")
            print("\n[He walks along the shore, and you watch until he disappears in the evening mist]")
            break

        elif user_input.lower().startswith('tell me about '):
            topic = user_input[13:].strip()
            if any(name in topic.lower() for name in ['peter', 'john', 'james', 'mary', 'martha', 'judas']):
                response = jesus.discuss_companion(topic)
            else:
                response = jesus.tell_about_daily_life(topic)
            print(f"\nJesus: {response}\n")

        elif 'childhood' in user_input.lower() or 'growing up' in user_input.lower():
            response = jesus.share_childhood_memory()
            print(f"\n[Jesus' eyes grow distant with memory]\n")
            print(f"Jesus: {response}\n")

        elif 'advice' in user_input.lower() or 'help' in user_input.lower() or 'struggle' in user_input.lower():
            response = jesus.give_practical_advice(user_input)
            print(f"\n[Jesus leans forward, speaking gently]\n")
            print(f"Jesus: {response}\n")

        elif user_input:
            response = bot.converse(user_input)
            print(f"\nJesus: {response}\n")

    # Save conversation
    bot.save_conversation("conversation_with_jesus.json")
    print("\n[Conversation saved to conversation_with_jesus.json]")


def quick_test():
    """Quick test of conversational responses."""
    print("Testing conversational Jesus responses...")

    jesus = JesusConversational()
    jesus.load_consciousness()

    test_questions = [
        "Hello Jesus, how are you feeling today?",
        "Tell me about fishing with Peter.",
        "I'm afraid of death. What should I do?",
        "What was your favorite meal?",
        "Why do you eat with tax collectors?"
    ]

    for q in test_questions[:2]:
        print(f"\nQ: {q}")
        response = jesus.speak(q)
        print(f"A: {response[:200]}...")
        print("-" * 40)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--test', action='store_true', help='Quick test mode')
    args = parser.parse_args()

    if args.test:
        quick_test()
    else:
        conversational_demo()