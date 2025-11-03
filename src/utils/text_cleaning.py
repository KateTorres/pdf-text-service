"""
text_cleaning.py (diagnostic version)
------------------------------------
Temporary pass-through implementation to test extraction output
without any cleaning, filtering, or restructuring.
"""

import unicodedata


def process_extracted_text(text: str, language: str = "english") -> str:
    """
    Minimal processing:
      - normalize Unicode to NFC (safe for Cyrillic/Latin mix)
      - strip leading/trailing whitespace
    No cleaning, no punctuation removal, no casing changes.
    """
    if not text:
        return ""

    # Normalize to NFC form to ensure consistent Unicode
    text = unicodedata.normalize("NFC", text)

    # Trim outer whitespace, but otherwise keep everything
    return text.strip()
