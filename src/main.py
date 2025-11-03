"""
main.py
-------
Entry point for pdf-text-service.

Applies a single region JSON (based on start page) to all pages
in the user-specified range if multiple pages are selected.
"""

import argparse
import os
import json
from src.extractors.pdf_local import extract_text_from_pdf


DEFAULT_REGION_DIR = "/mnt/c/projects/pdf-text-service-windows/regions"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Extract and clean text from a PDF using optional region JSONs."
    )
    parser.add_argument("--pdf", required=True, help="Path to the PDF file.")
    parser.add_argument("--start", type=int, default=None, help="Start page (if omitted, prompt).")
    parser.add_argument("--end", type=int, default=None, help="End page (if omitted, prompt).")
    parser.add_argument("--language", choices=["english", "cyrillic"], default="cyrillic",
                        help="Language filter for text cleaning (default: cyrillic).")
    parser.add_argument("--output", required=False, help="Optional output path for cleaned text.")
    return parser.parse_args()


def prompt_for_pages():
    """Interactive page range input."""
    while True:
        try:
            start_page = int(input("Enter start page: ").strip())
            break
        except ValueError:
            print("Please enter a valid number.")
    end_input = input("Enter end page (press Enter for same page): ").strip()
    end_page = int(end_input) if end_input.isdigit() else start_page
    return start_page, end_page


def find_region_file(pdf_path, page_num):
    """Return the JSON path matching the PDF base name and page number."""
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    pattern = f"{pdf_name}_page{page_num}.json"
    candidate = os.path.join(DEFAULT_REGION_DIR, pattern)
    return candidate if os.path.exists(candidate) else None


def replicate_regions_across_pages(region_path, start_page, end_page):
    """Load regions once and replicate for all pages in range."""
    with open(region_path, "r", encoding="utf-8") as f:
        regions = json.load(f)

    # Flatten nested structures if needed
    if isinstance(regions, list) and regions and "regions" in regions[0]:
        flattened = []
        for reg in regions[0]["regions"]:
            flattened.append(reg)
        regions = flattened

    replicated = []
    for page in range(start_page, end_page + 1):
        for reg in regions:
            rcopy = reg.copy()
            rcopy["page"] = page
            replicated.append(rcopy)

    temp_path = f"/tmp/temp_regions_{start_page}_{end_page}.json"
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(replicated, f, ensure_ascii=False, indent=2)
    return temp_path


def main():
    args = parse_args()
    pdf_path = os.path.abspath(args.pdf)
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    start_page, end_page = (
        prompt_for_pages()
        if args.start is None or args.end is None
        else (args.start, args.end)
    )

    print(f"\nPDF: {pdf_path}")
    print(f"Pages: {start_page}–{end_page}")
    print(f"Language: {args.language}")

    region_file = find_region_file(pdf_path, start_page)
    if region_file:
        if end_page > start_page:
            print(f"Using region {region_file} for all pages {start_page}–{end_page}")
            region_file = replicate_regions_across_pages(region_file, start_page, end_page)
        else:
            print(f"Using region file: {region_file}")
    else:
        print("No region JSON found. Proceeding without it.")

    result = extract_text_from_pdf(
        pdf_path=pdf_path,
        start_page=start_page,
        end_page=end_page,
        region_file=region_file,
        language=args.language
    )

    output_dir = "./outputs/cleaned_text"
    os.makedirs(output_dir, exist_ok=True)
    output_name = f"{os.path.splitext(os.path.basename(pdf_path))[0]}_page{start_page}_to_{end_page}.txt"
    output_path = os.path.join(output_dir, output_name)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result["processed_text"].strip() + "\n\n")

    print(f"\nText saved to: {os.path.abspath(output_path)}")


if __name__ == "__main__":
    main()
