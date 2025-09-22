#!/usr/bin/env python3
"""
Download Gospel texts from public domain sources.
"""

import os
import requests
import json
from pathlib import Path
import time

def download_gospel_texts():
    """Download Gospel texts from various public domain sources."""

    base_dir = Path("resurrections/data/jesus_christ")
    base_dir.mkdir(parents=True, exist_ok=True)

    print("📖 Downloading Gospel Texts...")
    print("=" * 60)

    # Sources for public domain biblical texts
    sources = {
        "Bible API (KJV)": {
            "base_url": "https://bible-api.com/",
            "books": {
                "matthew": [5, 6, 7, 13, 18, 22, 25],  # Key chapters
                "mark": [1, 4, 6, 10, 12],
                "luke": [6, 10, 15, 17, 18],
                "john": [1, 3, 8, 13, 14, 15]
            }
        }
    }

    # Create directories
    canonical_dir = base_dir / "canonical"
    canonical_dir.mkdir(exist_ok=True)

    teachings_dir = base_dir / "teachings"
    teachings_dir.mkdir(exist_ok=True)

    daily_life_dir = base_dir / "daily_life"
    daily_life_dir.mkdir(exist_ok=True)

    # Try to download from Bible API
    print("\n1. Attempting Bible API download...")
    try:
        for book, chapters in sources["Bible API (KJV)"]["books"].items():
            print(f"\n   Downloading {book.title()}...")
            book_content = []

            for chapter in chapters:
                url = f"https://bible-api.com/{book}+{chapter}?translation=kjv"
                print(f"      Chapter {chapter}...", end="")

                try:
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        book_content.append(f"\n\n{book.upper()} CHAPTER {chapter}\n")
                        book_content.append(data.get('text', ''))
                        print(" ✓")
                    else:
                        print(f" ✗ (Status: {response.status_code})")
                except Exception as e:
                    print(f" ✗ (Error: {e})")

                time.sleep(1)  # Be respectful to API

            # Save book
            if book_content:
                output_file = canonical_dir / f"{book}.txt"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(''.join(book_content))
                print(f"   ✅ Saved {book}.txt")

    except Exception as e:
        print(f"   ❌ Bible API failed: {e}")

    # Fallback: Create essential texts manually
    print("\n2. Creating essential Gospel excerpts...")

    # Sermon on the Mount (core teachings)
    sermon_text = """THE SERMON ON THE MOUNT (Matthew 5-7)

And seeing the multitudes, he went up into a mountain: and when he was set, his disciples came unto him:
And he opened his mouth, and taught them, saying,

THE BEATITUDES
Blessed are the poor in spirit: for theirs is the kingdom of heaven.
Blessed are they that mourn: for they shall be comforted.
Blessed are the meek: for they shall inherit the earth.
Blessed are they which do hunger and thirst after righteousness: for they shall be filled.
Blessed are the merciful: for they shall obtain mercy.
Blessed are the pure in heart: for they shall see God.
Blessed are the peacemakers: for they shall be called the children of God.

TEACHINGS ON LOVE
Ye have heard that it hath been said, Thou shalt love thy neighbour, and hate thine enemy.
But I say unto you, Love your enemies, bless them that curse you, do good to them that hate you,
and pray for them which despitefully use you, and persecute you.

ASK AND IT SHALL BE GIVEN
Ask, and it shall be given you; seek, and ye shall find; knock, and it shall be opened unto you.

THE GOLDEN RULE
Therefore all things whatsoever ye would that men should do to you, do ye even so to them."""

    with open(teachings_dir / "sermon_on_mount.txt", 'w') as f:
        f.write(sermon_text)
    print("   ✓ Created sermon_on_mount.txt")

    # Daily life and companions
    daily_life_text = """JESUS' DAILY LIFE AND COMPANIONS

THE CALLING OF THE DISCIPLES (Matthew 4:18-22)
And Jesus, walking by the sea of Galilee, saw two brethren, Simon called Peter, and Andrew his brother,
casting a net into the sea: for they were fishers. And he saith unto them, Follow me, and I will make you
fishers of men. And they straightway left their nets, and followed him.

JESUS WITH THE TWELVE
And he ordained twelve, that they should be with him, and that he might send them forth to preach:
Simon (whom he also named Peter), Andrew, James, John, Philip, Bartholomew, Matthew, Thomas,
James the son of Alphaeus, Thaddaeus, Simon the Canaanite, and Judas Iscariot.

DAILY MINISTRY
And Jesus went about all Galilee, teaching in their synagogues, and preaching the gospel of the kingdom,
and healing all manner of sickness and all manner of disease among the people.

WITH MARY AND MARTHA (Luke 10:38-42)
Now it came to pass, as they went, that he entered into a certain village:
and a certain woman named Martha received him into her house.
And she had a sister called Mary, which also sat at Jesus' feet, and heard his word.

EATING WITH SINNERS (Mark 2:15-17)
And it came to pass, that, as Jesus sat at meat in his house, many publicans and sinners
sat also together with Jesus and his disciples. And when the scribes and Pharisees saw him eat
with publicans and sinners, they said unto his disciples, How is it that he eateth and drinketh
with publicans and sinners? When Jesus heard it, he saith unto them, They that are whole have
no need of the physician, but they that are sick: I came not to call the righteous, but sinners to repentance.

THE CHILDHOOD OF JESUS (Luke 2:41-52)
Now his parents went to Jerusalem every year at the feast of the passover. And when he was twelve years old,
they went up to Jerusalem after the custom of the feast. And when they had fulfilled the days, as they returned,
the child Jesus tarried behind in Jerusalem. And when they found him, he was in the temple, sitting in the midst
of the doctors, both hearing them, and asking them questions. And all that heard him were astonished at his
understanding and answers.

JESUS THE CARPENTER (Mark 6:3)
Is not this the carpenter, the son of Mary, the brother of James, and Joses, and of Juda, and Simon?
and are not his sisters here with us?

PRAYER LIFE
And in the morning, rising up a great while before day, he went out, and departed into a solitary place,
and there prayed.

COMPASSION FOR THE CROWDS
But when he saw the multitudes, he was moved with compassion on them, because they fainted,
and were scattered abroad, as sheep having no shepherd."""

    with open(daily_life_dir / "daily_life_and_companions.txt", 'w') as f:
        f.write(daily_life_text)
    print("   ✓ Created daily_life_and_companions.txt")

    # Conversational responses
    conversational_text = """JESUS' CONVERSATIONAL STYLE

WITH NICODEMUS (John 3:1-21)
Nicodemus: Rabbi, we know that thou art a teacher come from God.
Jesus: Verily, verily, I say unto thee, Except a man be born again, he cannot see the kingdom of God.
Nicodemus: How can a man be born when he is old?
Jesus: Marvel not that I said unto thee, Ye must be born again. The wind bloweth where it listeth,
and thou hearest the sound thereof, but canst not tell whence it cometh, and whither it goeth:
so is every one that is born of the Spirit.

WITH THE WOMAN AT THE WELL (John 4:7-26)
Woman: How is it that thou, being a Jew, askest drink of me, which am a woman of Samaria?
Jesus: If thou knewest the gift of God, and who it is that saith to thee, Give me to drink;
thou wouldest have asked of him, and he would have given thee living water.
Woman: Sir, thou hast nothing to draw with, and the well is deep.
Jesus: Whosoever drinketh of this water shall thirst again: But whosoever drinketh of the water
that I shall give him shall never thirst.

WITH PETER (Matthew 16:13-20)
Jesus: Whom do men say that I the Son of man am?
Disciples: Some say John the Baptist, some Elias, and others Jeremias.
Jesus: But whom say ye that I am?
Peter: Thou art the Christ, the Son of the living God.
Jesus: Blessed art thou, Simon Barjona: for flesh and blood hath not revealed it unto thee,
but my Father which is in heaven.

SIMPLE RESPONSES
"Follow me."
"Your faith has made you whole."
"Go, and sin no more."
"Peace be with you."
"Why are you afraid? Have you still no faith?"
"Let the little children come to me."
"Give to Caesar what is Caesar's, and to God what is God's."
"Where is your faith?"
"Do you believe this?"
"Feed my sheep." """

    with open(teachings_dir / "conversational_style.txt", 'w') as f:
        f.write(conversational_text)
    print("   ✓ Created conversational_style.txt")

    print("\n" + "=" * 60)
    print("✅ Gospel text preparation complete!")
    print("\nYou can now:")
    print("1. Add more texts manually to the directories")
    print("2. Run: python resurrect_demo.py")
    print("\nFor complete texts, consider:")
    print("- Project Gutenberg: gutenberg.org")
    print("- Sacred Texts: sacred-texts.com")
    print("- Bible Gateway API (with key): biblegateway.com")


if __name__ == "__main__":
    download_gospel_texts()