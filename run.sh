#!/bin/bash
# PDF Text Service launcher (Linux)
# Runs the main Python extraction script with a user-specified PDF file

set -e

echo "=== PDF Text Service ==="
read -p "Enter PDF file name (with extension): " PDF_FILE

python3 -m src.main "$PDF_FILE"
