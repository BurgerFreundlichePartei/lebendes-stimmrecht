#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract red-marked spelling "errors" from KDP HTML previews.
Designed for Asterios Raptis' publishing workflow.
"""

import re
import sys
import os
from pathlib import Path
from bs4 import BeautifulSoup


def extract_red_spans(html_content: str) -> list[str]:
    """
    Extracts all unique text snippets marked as red (potential spelling errors)
    from KDP-generated HTML.

    Supports:
      - <span style="color:red">...</span>
      - <span class="spelling-error">...</span>
      - <font color="red">...</font>

    Returns sorted list of unique, stripped strings.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    errors = set()

    # 1. style="color:red"
    for span in soup.find_all('span', style=re.compile(r'color\s*:\s*red', re.IGNORECASE)):
        text = span.get_text().strip()
        if text:
            errors.add(text)

    # 2. common error classes
    for cls in ('spelling-error', 'error', 'misspelled'):
        for span in soup.find_all('span', class_=cls):
            text = span.get_text().strip()
            if text:
                errors.add(text)

    # 3. legacy <font color="red">
    for font in soup.find_all('font', color=re.compile(r'^\s*red\s*$', re.IGNORECASE)):
        text = font.get_text().strip()
        if text:
            errors.add(text)

    return sorted(errors)


def main():
    if len(sys.argv) != 2:
        print("Usage: extract-kdp-errors <input.html>", file=sys.stderr)
        sys.exit(1)

    input_path = Path(sys.argv[1])
    if not input_path.is_file():
        print(f"Error: File not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    errors = extract_red_spans(content)
    output_path = input_path.with_name(input_path.stem + "_kdp_errors.txt")

    with open(output_path, 'w', encoding='utf-8') as f:
        for word in errors:
            f.write(word + '\n')

    print(f"✅ Extracted {len(errors)} unique red-marked terms.")
    print(f"📄 Saved to: {output_path}")


if __name__ == "__main__":
    main()
