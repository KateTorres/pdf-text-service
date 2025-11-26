"""
text_cleaning.py
----------------
Utility that cleans text extracted from PDFs.
Supports both Cyrillic and Latin (English) content.
Removes bullet points and long dot sequences.
"""

import re
import unicodedata


def clean_line(line: str) -> str:
    line = line.replace("*", "").replace("", "").replace("•", "")
    line = re.sub(r'\.{3,}', '', line)
    return line.strip()


def normalize_hyphenated_words(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r'[\u2010-\u2015]', '-', text)
    return re.sub(r'(\b\w+)-\s*\n\s*([а-яёa-z]\w+)', r'\1\2', text, flags=re.IGNORECASE)


def process_extracted_text(text: str, language: str = "cyrillic") -> str:
    text = normalize_hyphenated_words(text)
    lines = text.split("\n")
    processed_lines, paragraph = [], []
    for line in lines:
        line = clean_line(line)
        if not line:
            if paragraph:
                processed_lines.append(" ".join(paragraph))
                paragraph = []
            continue
        paragraph.append(line)
    if paragraph:
        processed_lines.append(" ".join(paragraph))
    return "\n\n".join(processed_lines)
