#!/usr/bin/env python3
"""
Simple Jesus Demo - Actually Responds to Your Questions!
"""

from resurrections.jesus_simple import SimpleJesusBot

def main():
    print("\n" + "="*60)
    print("      CONVERSE WITH JESUS - SIMPLE & RESPONSIVE")
    print("="*60)
    print("\nThis version actually responds to what you ask!")
    print("Try asking about:")
    print("  - Thomas or other apostles")
    print("  - Daily life with disciples")
    print("  - Love, prayer, fear")
    print("  - Any question you have")
    print("\nType 'goodbye' to exit")
    print("="*60)

    bot = SimpleJesusBot()
    bot.run()

if __name__ == "__main__":
    main()