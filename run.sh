#!/bin/bash
# ------------------------------------------------------------
# run.sh
# ------------------------------------------------------------
# Minimal launcher for pdf-text-service
# ------------------------------------------------------------

# Ensure we're in the project root
cd "$(dirname "$0")" || exit 1

# Configuration
WIN_BASE="/mnt/c/projects/pdf-text-service-windows"
PDF_DIR="${WIN_BASE}/pdfs"
REGION_DIR="${WIN_BASE}/regions"
OUTPUT_DIR="./outputs/cleaned_text"

# Arguments
PDF_NAME="${1%.*}"
PDF_FILE="${PDF_NAME}.pdf"
PDF_PATH="${PDF_DIR}/${PDF_FILE}"

# Validation
if [ ! -f "$PDF_PATH" ]; then
  echo "Error: PDF not found at $PDF_PATH"
  exit 1
fi

# Run main.py (it handles prompts and region detection)
python3 -m src.main --pdf "$PDF_PATH"
