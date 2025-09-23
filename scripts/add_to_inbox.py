#!/usr/bin/env python3
"""
Add texts to a resurrection bundle's inbox
Usage: python add_to_inbox.py <bundle_name> <url_or_file>
"""

import sys
import os
from pathlib import Path
import requests
import re

def download_text(url: str, output_path: str):
    """Download text from URL"""
    print(f"📥 Downloading from {url}...")

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        # Clean the text (remove excessive whitespace, etc)
        text = response.text

        # Basic cleaning
        text = re.sub(r'\n{3,}', '\n\n', text)  # Reduce multiple newlines
        text = re.sub(r' {2,}', ' ', text)  # Reduce multiple spaces

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)

        print(f"✓ Saved to {output_path}")
        return True

    except Exception as e:
        print(f"✗ Download failed: {e}")
        return False

def main():
    if len(sys.argv) < 3:
        print("Usage: python add_to_inbox.py <bundle_name> <url_or_file> [output_name]")
        print("\nExamples:")
        print("  python add_to_inbox.py jesus_christ https://example.com/text.txt")
        print("  python add_to_inbox.py jesus_christ /path/to/local/file.txt")
        print("  python add_to_inbox.py jesus_christ https://example.com/text.txt pistis_sophia.txt")
        sys.exit(1)

    bundle_name = sys.argv[1]
    source = sys.argv[2]

    # Determine output filename
    if len(sys.argv) > 3:
        output_name = sys.argv[3]
    else:
        # Extract filename from URL or use basename
        if source.startswith('http'):
            output_name = Path(source.split('/')[-1]).stem + '.txt'
            # Clean up common archive.org naming
            output_name = output_name.replace('_djvu', '')
        else:
            output_name = Path(source).name

    # Create inbox path
    inbox_path = Path(f"resurrections/bundles/{bundle_name}/inbox")
    inbox_path.mkdir(parents=True, exist_ok=True)

    output_file = inbox_path / output_name

    # Download or copy file
    if source.startswith('http'):
        success = download_text(source, output_file)
    else:
        # Copy local file
        try:
            with open(source, 'r', encoding='utf-8') as f:
                content = f.read()
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Copied to {output_file}")
            success = True
        except Exception as e:
            print(f"✗ Copy failed: {e}")
            success = False

    if success:
        print(f"\n✅ Text added to {bundle_name}'s inbox")
        print("\nTo process it:")
        print("  ./christ")
        print(f"  load {bundle_name}")
        print("  inbox")
        print("\nOr directly:")
        print(f"  ./christ")
        print(f"  inbox {bundle_name}")

if __name__ == "__main__":
    main()