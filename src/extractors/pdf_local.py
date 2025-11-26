"""
pdf_local.py
------------
Hybrid text extraction for PDFs.

Rules:
- Digital pages (with text layer): use pdfplumber.
- Scanned/image pages: run OCR (Tesseract/docTR fallback).
- Region JSONs define page regions.
- If a later page has no JSON, reuse the last defined regions (including those before the start page).
- Unicode-safe JSON filename handling for Windows/Linux interoperability.
"""

import os
import json
import unicodedata
import pdfplumber
from datetime import datetime
from src.utils.text_cleaning import process_extracted_text


MIN_WORDS_FOR_TEXT_LAYER = 20  # threshold for considering text layer presence


def load_regions(region_file):
    """Load predefined region rectangles from JSON file with Unicode-safe path handling."""
    norm_path = unicodedata.normalize("NFC", region_file)
    if not os.path.exists(norm_path):
        print(f"[WARN] Region file not found: {norm_path}")
        return []
    with open(norm_path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_text_from_pdf(pdf_path, language="cyrillic",
                          start_page=1, end_page=None, region_file=None):
    """
    Extract text from PDF.
    - Digital pages → pdfplumber (JSON regions respected)
    - Scanned pages → OCR fallback (no regions used)
    - If later pages have no JSON, reuse the last defined regions.
    - If processing starts after the last JSON page, reuse that last available JSON.
    """
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    start_time = datetime.now()
    page_texts = []

    # --- Load and map regions by page ---
    all_regions = load_regions(region_file) if region_file else []
    regions_by_page = {}
    for r in all_regions:
        p = r.get("page")
        if p:
            regions_by_page.setdefault(p, []).append(r)

    from src.utils.ocr_preprocessor import ocr_fallback_for_pdf_page

    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        if end_page is None or end_page > total_pages:
            end_page = total_pages

        last_regions = None

        for i in range(start_page - 1, end_page):
            page = pdf.pages[i]
            page_num = i + 1
            print(f"\n--- Processing page {page_num} ---")

            # --- Detect if the page has selectable text ---
            words = page.extract_words(x_tolerance=3, y_tolerance=4) or []
            if len(words) < MIN_WORDS_FOR_TEXT_LAYER:
                print(f"[OCR] Page {page_num} appears scanned → running OCR...")
                ocr_text = ocr_fallback_for_pdf_page(
                    page, page_num, os.path.basename(pdf_path), lang="rus+eng"
                )
                if ocr_text.strip():
                    page_texts.append(ocr_text.strip())
                else:
                    print(f"[OCR] Page {page_num}: skipped (low OCR confidence or empty).")
                continue

            # --- Determine which regions to use ---
            if page_num in regions_by_page:
                current_regions = regions_by_page[page_num]
                last_regions = current_regions
                print(f"[Text] Using {len(current_regions)} region(s) for page {page_num}")
            else:
                # Try the nearest earlier JSON-defined page
                prev_pages = [p for p in regions_by_page.keys() if p < page_num]
                if prev_pages:
                    nearest_prev = max(prev_pages)
                    current_regions = regions_by_page[nearest_prev]
                    last_regions = current_regions
                    print(f"[Text] Reusing {len(current_regions)} region(s) from JSON of page {nearest_prev}")
                elif last_regions:
                    current_regions = last_regions
                    print(f"[Text] Reusing {len(current_regions)} region(s) from previous JSON")
                else:
                    current_regions = []
                    print(f"[Text] No JSON regions defined → processing full page {page_num}")

            # --- Extract text accordingly ---
            region_texts = []
            if current_regions:
                for reg in current_regions:
                    bbox = (reg["x0"], reg["y0"], reg["x1"], reg["y1"])
                    if bbox[0] == bbox[2] or bbox[1] == bbox[3]:
                        print(f"[WARN] Skipping region with zero area: {bbox}")
                        continue
                    cropped = page.crop(bbox)
                    text = cropped.extract_text(layout=True) or ""
                    if text.strip():
                        region_texts.append(text.strip())
                    else:
                        print(f"[WARN] Empty region {reg.get('order', '?')} on page {page_num}")
                combined_text = "\n\n".join(region_texts)
            else:
                combined_text = page.extract_text(layout=True) or ""

            page_texts.append(combined_text.strip())

    # --- Combine and clean ---
    full_text = "\n\n".join(page_texts)
    processed = process_extracted_text(full_text, language=language)

    elapsed = (datetime.now() - start_time).total_seconds()
    print(f"\n[INFO] Completed extraction from {end_page - start_page + 1} pages in {elapsed:.1f}s")

    return {
        "pdf_name": os.path.basename(pdf_path),
        "page_count": end_page - start_page + 1,
        "elapsed_sec": elapsed,
        "processed_text": processed
    }
