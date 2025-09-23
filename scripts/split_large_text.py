#!/usr/bin/env python3
"""
Split large texts into manageable chapters/sections for better indexing
Especially useful for books like Pistis Sophia, Gospel of Thomas, etc.
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple

def detect_structure(text: str) -> str:
    """Detect the structure type of the text"""

    # Check for various chapter patterns
    patterns = {
        'numbered_chapters': r'CHAPTER\s+\d+|Chapter\s+\d+|CHAPTER\s+[IVXLC]+',
        'book_divisions': r'BOOK\s+[IVXLC]+|FIRST\s+BOOK|SECOND\s+BOOK|THIRD\s+BOOK',
        'verse_structure': r'^\d+:\d+\s+',  # Biblical verse format
        'section_headers': r'^[A-Z][A-Z\s]+[A-Z]$',  # ALL CAPS headers
        'numbered_sections': r'^\d+\.\s+',
        'saying_structure': r'\(\d+\)',  # Like Gospel of Thomas (1), (2), etc
    }

    for pattern_name, pattern in patterns.items():
        if len(re.findall(pattern, text, re.MULTILINE)) > 3:
            return pattern_name

    return 'paragraph_based'

def split_by_chapters(text: str) -> List[Tuple[str, str]]:
    """Split text by chapter markers"""

    # Multiple chapter patterns to try
    chapter_patterns = [
        r'(CHAPTER\s+[IVXLCDM]+)',  # Roman numerals
        r'(CHAPTER\s+\d+)',          # Numbers
        r'(Chapter\s+\d+)',          # Lowercase
        r'(\n\s*\d+\.\s+[A-Z])',     # Numbered sections
    ]

    sections = []

    for pattern in chapter_patterns:
        matches = list(re.finditer(pattern, text, re.IGNORECASE))
        if len(matches) > 2:  # Found chapter structure
            for i, match in enumerate(matches):
                start = match.start()
                end = matches[i + 1].start() if i + 1 < len(matches) else len(text)

                chapter_text = text[start:end].strip()
                if len(chapter_text) > 100:  # Minimum content
                    chapter_title = match.group(1).strip()
                    sections.append((chapter_title, chapter_text))

            if sections:
                return sections

    return []

def split_by_sayings(text: str) -> List[Tuple[str, str]]:
    """Split text by saying numbers (like Gospel of Thomas)"""

    # Pattern for (1), (2), etc
    pattern = r'\((\d+)\)'
    matches = list(re.finditer(pattern, text))

    sections = []
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)

        saying_text = text[start:end].strip()
        if len(saying_text) > 50:
            saying_num = match.group(1)
            sections.append((f"Saying {saying_num}", saying_text))

    return sections

def split_by_paragraphs(text: str, max_chunk_size: int = 2000) -> List[Tuple[str, str]]:
    """Split text by paragraphs, combining small ones"""

    paragraphs = text.split('\n\n')
    sections = []
    current_section = []
    current_size = 0
    section_num = 1

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        para_size = len(para)

        if current_size + para_size > max_chunk_size and current_section:
            # Save current section
            combined = '\n\n'.join(current_section)
            sections.append((f"Section {section_num}", combined))
            section_num += 1
            current_section = [para]
            current_size = para_size
        else:
            current_section.append(para)
            current_size += para_size

    # Don't forget the last section
    if current_section:
        combined = '\n\n'.join(current_section)
        sections.append((f"Section {section_num}", combined))

    return sections

def split_text(text: str, filename: str) -> List[Tuple[str, str]]:
    """Main function to split text intelligently"""

    print(f"📖 Analyzing text structure...")

    structure = detect_structure(text)
    print(f"  Detected structure: {structure}")

    # Clean up text first
    text = re.sub(r'\n{3,}', '\n\n', text)  # Reduce excessive newlines
    text = re.sub(r' {2,}', ' ', text)      # Reduce multiple spaces

    # Try different splitting methods
    if 'chapter' in structure.lower() or 'CHAPTER' in text[:1000]:
        sections = split_by_chapters(text)
        if sections:
            print(f"  Split into {len(sections)} chapters")
            return sections

    if 'saying' in structure.lower() or '(1)' in text[:500]:
        sections = split_by_sayings(text)
        if sections:
            print(f"  Split into {len(sections)} sayings")
            return sections

    # Default to paragraph-based splitting
    sections = split_by_paragraphs(text)
    print(f"  Split into {len(sections)} sections")
    return sections

def save_sections(sections: List[Tuple[str, str]], output_dir: Path, base_name: str):
    """Save sections as individual files"""

    output_dir.mkdir(parents=True, exist_ok=True)

    for i, (title, content) in enumerate(sections):
        # Clean title for filename
        clean_title = re.sub(r'[^\w\s-]', '', title.lower())
        clean_title = re.sub(r'[-\s]+', '_', clean_title)

        filename = f"{base_name}_{i+1:03d}_{clean_title}.txt"
        filepath = output_dir / filename

        # Add title to content
        full_content = f"{title.upper()}\n\n{content}"

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(full_content)

    print(f"✅ Saved {len(sections)} files to {output_dir}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python split_large_text.py <input_file> [output_dir]")
        print("\nThis will split large texts into chapters/sections for better indexing")
        print("\nExample:")
        print("  python split_large_text.py pistis_sophia.txt")
        print("  python split_large_text.py pistis_sophia.txt resurrections/bundles/jesus_christ/inbox/")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    if not input_file.exists():
        print(f"Error: {input_file} not found")
        sys.exit(1)

    # Determine output directory
    if len(sys.argv) > 2:
        output_dir = Path(sys.argv[2])
    else:
        # Default to creating a directory named after the file
        output_dir = Path(f"{input_file.stem}_split")

    # Read the input file
    print(f"📚 Reading {input_file}...")
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()

    print(f"  Size: {len(text):,} characters")

    # Split the text
    sections = split_text(text, input_file.name)

    if not sections:
        print("❌ Could not split the text")
        sys.exit(1)

    # Save sections
    base_name = input_file.stem
    save_sections(sections, output_dir, base_name)

    # Show summary
    total_chars = sum(len(content) for _, content in sections)
    avg_size = total_chars // len(sections)

    print(f"\n📊 Summary:")
    print(f"  Original size: {len(text):,} chars")
    print(f"  Sections: {len(sections)}")
    print(f"  Average section: {avg_size:,} chars")
    print(f"\n✨ Ready for indexing!")

    # If output is in inbox, show next steps
    if 'inbox' in str(output_dir):
        bundle_name = output_dir.parts[-3] if len(output_dir.parts) > 3 else 'bundle'
        print(f"\nNext steps:")
        print(f"  ./christ")
        print(f"  load {bundle_name}")
        print(f"  inbox")

if __name__ == "__main__":
    main()