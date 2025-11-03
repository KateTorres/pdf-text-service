"""
pdf_local.py
------------
Adaptive layout-aware text extraction for PDFs using pdfplumber.
Now includes diagnostic prints to verify multi-region text aggregation.
"""

import os
import json
import pdfplumber
from datetime import datetime
from itertools import groupby
from statistics import mean
from src.utils.text_cleaning import process_extracted_text


MIN_CHARS_TO_KEEP_PAGE = 50


def load_regions(region_file):
    """Load predefined region rectangles from JSON file."""
    if not os.path.exists(region_file):
        print(f"Warning: region file not found at {region_file}")
        return []

    with open(region_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Flatten nested JSON structures
    if isinstance(data, list) and data and isinstance(data[0], dict) and "regions" in data[0]:
        flattened = []
        for page_entry in data:
            page_num = page_entry.get("page")
            for reg in page_entry.get("regions", []):
                reg["page"] = page_num
                flattened.append(reg)
        data = flattened

    return data


def deduplicate_words(words):
    unique = []
    seen = set()
    for w in words:
        key = (round(w["x0"], 1), round(w["top"], 1), w["text"])
        if key not in seen:
            seen.add(key)
            unique.append(w)
    return unique


def cluster_columns(words, page_width, base_tolerance_ratio=0.1):
    if not words:
        return []
    tolerance = page_width * base_tolerance_ratio
    words_sorted = sorted(words, key=lambda w: w["x0"])
    columns = []
    for w in words_sorted:
        placed = False
        for col in columns:
            avg_x = mean(cw["x0"] for cw in col)
            if abs(w["x0"] - avg_x) < tolerance:
                col.append(w)
                placed = True
                break
        if not placed:
            columns.append([w])
    columns.sort(key=lambda c: mean(cw["x0"] for cw in c))
    return columns


def lines_from(col_words):
    if not col_words:
        return []
    col_words_sorted = sorted(col_words, key=lambda w: (round(w["top"], 1), w["x0"]))
    lines = []
    for _, group in groupby(col_words_sorted, key=lambda w: round(w["top"], 1)):
        line = " ".join(w["text"] for w in group)
        lines.append(line)
    return lines


def group_paragraphs(lines):
    """Group consecutive non-empty lines into paragraphs."""
    grouped = []
    buffer = []
    for line in lines:
        if not line.strip():
            if buffer:
                grouped.append(" ".join(buffer))
                buffer = []
        else:
            buffer.append(line.strip())
    if buffer:
        grouped.append(" ".join(buffer))
    return grouped


def extract_text_from_pdf(pdf_path, language="english", start_page=1,
                          end_page=None, region_file=None):
    """Extract text from a local PDF using pdfplumber, optionally constrained to regions."""
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    start_time = datetime.now()
    page_texts = []
    regions = load_regions(region_file) if region_file else []

    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        if end_page is None or end_page > total_pages:
            end_page = total_pages

        for i in range(start_page - 1, end_page):
            page = pdf.pages[i]
            page_num = i + 1
            print(f"\n--- Processing page {page_num} ---")

            if regions:
                page_regions = [r for r in regions if r.get("page") == page_num]
                if page_regions:
                    page_regions.sort(key=lambda r: r.get("order", 10**9))
                    print(f"Using {len(page_regions)} region(s) for page {page_num}")
                    region_texts = []
                    for reg in page_regions:
                        bbox = (reg["x0"], reg["y0"], reg["x1"], reg["y1"])
                        region_words = page.within_bbox(bbox).extract_words(
                            x_tolerance=3, y_tolerance=3
                        )
                        region_words = deduplicate_words(region_words)
                        lines = lines_from(region_words)
                        grouped = group_paragraphs(lines)
                        region_block = "\n\n".join(grouped)
                        print(f"\n[DEBUG] Region {reg.get('order')} extracted {len(region_block)} chars")
                        region_texts.append(region_block)

                    combined_text = "\n\n".join(region_texts)
                    print("\n[DEBUG] Combined text from all regions (first 500 chars):")
                    print(combined_text[:500])
                    page_texts.append(combined_text)
                    continue

            # Fallback mode
            words = page.extract_words(x_tolerance=3, y_tolerance=3) or []
            words = deduplicate_words(words)
            char_count = sum(len(w["text"]) for w in words)
            if len(page.images) > 0 and char_count < MIN_CHARS_TO_KEEP_PAGE:
                print(f"Skipping page {page_num}: image-heavy.")
                continue
            if not words:
                print(f"Skipping page {page_num}: no text.")
                continue

            columns = cluster_columns(words, page.width)
            page_lines = []
            for col_words in columns:
                col_lines = lines_from(col_words)
                grouped = group_paragraphs(col_lines)
                page_lines.extend(grouped)
                page_lines.append("")
            page_texts.append("\n\n".join(page_lines).strip())

    full_text = "\n\n".join(page_texts)
    print("\n[DEBUG] Raw combined text before cleaning (first 800 chars):")
    print(full_text[:800])

    processed = process_extracted_text(full_text, language=language)
    elapsed = (datetime.now() - start_time).total_seconds()
    page_count = end_page - start_page + 1

    return {
        "pdf_name": os.path.basename(pdf_path),
        "page_count": page_count,
        "elapsed_sec": elapsed,
        "processed_text": processed
    }
