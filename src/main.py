import os
import sys
from src.extractors.pdf_local import extract_text_from_pdf

PDFS_DIR = "/mnt/c/projects/pdf-text-service-windows/pdfs"
REGIONS_DIR = "/mnt/c/projects/pdf-text-service-windows/regions"


def main():
    print("=== PDF Text Service ===")

    # ---------------------------------------------------------
    # 1. Get PDF filename either from CLI or user input
    # ---------------------------------------------------------
    if len(sys.argv) > 1:
        pdf_name = sys.argv[1].strip()
        print(f"Using file from CLI: {pdf_name}")
    else:
        pdf_name = input("Enter PDF file name (with or without path): ").strip()
        if not pdf_name:
            print("Error: No PDF file name provided.")
            return

    # If user typed only a filename, build full path
    if not os.path.isabs(pdf_name):
        pdf_path = os.path.join(PDFS_DIR, pdf_name)
    else:
        pdf_path = pdf_name

    if not os.path.isfile(pdf_path):
        print(f"Error: PDF not found: {pdf_path}")
        return

    # ---------------------------------------------------------
    # 2. Ask for page range
    # ---------------------------------------------------------
    try:
        start_page = int(input("Enter start page: ").strip())
    except ValueError:
        print("Error: Start page must be an integer.")
        return

    end_page_input = input("Enter end page (press Enter for same page): ").strip()
    if end_page_input == "":
        end_page = start_page
    else:
        try:
            end_page = int(end_page_input)
        except ValueError:
            print("Error: End page must be an integer.")
            return

    # ---------------------------------------------------------
    # 3. Determine region base name (strip .pdf)
    # ---------------------------------------------------------
    pdf_base = os.path.splitext(os.path.basename(pdf_path))[0]

    region_file_input = os.path.join(
        REGIONS_DIR,
        f"{pdf_base}_page{start_page}.json"
    )

    print()
    print(f"PDF: {pdf_path}")
    print(f"Pages: {start_page}–{end_page}")
    print(f"Using region file: {region_file_input}")
    print()

    # ---------------------------------------------------------
    # 4. Run extraction
    # ---------------------------------------------------------
    result = extract_text_from_pdf(
        pdf_path=pdf_path,
        start_page=start_page,
        end_page=end_page,
        region_file=region_file_input,
        language="cyrillic"
    )

    # ---------------------------------------------------------
    # 5. Save output
    # ---------------------------------------------------------
    output_name = f"{pdf_base}_p{start_page}-{end_page}.txt"
    output_path = os.path.join("outputs", output_name)

    os.makedirs("outputs", exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result["processed_text"])

    print(f"Saved extracted text to: {output_path}")


if __name__ == "__main__":
    main()
