# PDF Text Service (Linux)

This repository performs **region-based text extraction** from PDFs using `pdfplumber`.  
It uses region JSONs created with [**pdf-text-service-windows**](https://github.com/yourusername/pdf-text-service-windows) 

---

## Overview

- Reads PDFs and region JSONs  
- Extracts text from the specified areas  
- Cleans and normalizes the output  
- Supports Cyrillic and English text 

Output text files are stored under `outputs/cleaned_text/`.

---

## Usage

```bash
./run.sh test1.pdf
You’ll be prompted for:

Start and end pages

Language (default: Cyrillic) but will be update with a menu later.

If multiple pages are selected, the same region layout (from the first page’s JSON)
is automatically applied to all pages in the range.

## Connection Between Repositories

Windows repo (pdf-text-service-windows) defines where to read text.
Linux repo (pdf-text-service) defines how to read and process it.
Together, they form a complete cross-platform toolchain for manual-region PDF extraction and analysis.

Example Workflow (Windows → Linux)

In Windows:
Use copy_coordinates.py to create test1_page5.json inside the regions/ folder.

In Linux:
Run: ./run.sh test1.pdf

The output file:
outputs/cleaned_text/test1_page5_to_5.txt contains text extracted only from your defined regions.

## Requirements

Linux or WSL2
Python 3.11+
pdfplumber pillow

## Future Development

REST API (FastAPI) wrapper for remote extraction requests
OCR fallback for scanned PDFs
Improved paragraph reconstruction and text flow modeling
Docker container for cloud deployment

# To Do list
## Text flow smoothness and character accuracy
to accomodate scanned or degraded PDFs
complex font encodings (Cyrillics, ligatures, etc.)
poor paragraph reconstruction

## Upgrade 1: Hybrid OCR fallback
## Upgrade 2: Language model–assisted postprocessing
- Once REST is deployed, hook in a lightweight text-fluency model to reconstruct smoother paragraphs or fix spacing.
- Send extracted text in batches and ask the model to merge broken lines and fix spacing without rewriting content.
## Upgrade 3: Layout learning

## Long-term, use JSON rectangles to train a small ML model that predicts reading order and column segmentation automatically.

## Containerize
Add a Dockerfile:

## Deploy 
- AWS for realistic REST hosting

## Test
- measure OCR accuracy 
- build a “layout quality” metric,
- test language models for formatting reconstruction