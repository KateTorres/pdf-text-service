"""
batch_processor.py
------------------
Batch utility for processing all JSON region files from Windows project.
"""

import os
import re
from src.extractors.pdf_local import extract_text_from_pdf


REGION_DIR = "/mnt/c/projects/pdf-text-service-windows/regions"
PDF_DIR = "/mnt/c/projects/pdf-text-service-windows/pdfs"
OUTPUT_DIR = "./outputs/cleaned_text"


def find_region_files():
    if not os.path.exists(REGION_DIR):
        raise FileNotFoundError(f"Region directory not found: {REGION_DIR}")
    region_files = [f for f in os.listdir(REGION_DIR) if f.endswith(".json")]
    grouped = {}
    pattern = re.compile(r"(.+)_page(\d+)\.json", re.IGNORECASE)
    for filename in region_files:
        match = pattern.match(filename)
        if not match:
            continue
        pdf_name, page_num = match.groups()
        page_num = int(page_num)
        grouped.setdefault(pdf_name, []).append((page_num, filename))
    for pdf_name in grouped:
        grouped[pdf_name].sort(key=lambda x: x[0])
    return grouped


def process_all(language="cyrillic"):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    grouped = find_region_files()
    if not grouped:
        print("No JSON region files found.")
        return
    for pdf_name, entries in grouped.items():
        pdf_path = os.path.join(PDF_DIR, f"{pdf_name}.pdf")
        if not os.path.exists(pdf_path):
            print(f"[WARN] PDF not found for {pdf_name}, skipping.")
            continue
        print(f"=== Processing {pdf_name}.pdf ===")
        combined_text = []
        for page_num, json_filename in entries:
            region_file = os.path.join(REGION_DIR, json_filename)
            result = extract_text_from_pdf(
                pdf_path=pdf_path,
                start_page=page_num,
                end_page=page_num,
                region_file=region_file,
                language=language,
            )
            combined_text.append(result["processed_text"])
        output_path = os.path.join(OUTPUT_DIR, f"{pdf_name}_all_pages.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n\n".join(combined_text).strip() + "\n")
        print(f"[DONE] Saved: {output_path}")


if __name__ == "__main__":
    process_all()
