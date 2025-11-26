"""
ocr_preprocessor.py
-------------------
Preprocessing, layout detection, and OCR fusion for scanned or rotated PDFs.
"""

import os
import cv2
import pytesseract
import numpy as np
import unicodedata
from PIL import Image

try:
    from doctr.io import DocumentFile
    from doctr.models import ocr_predictor
    DOCTR_AVAILABLE = True
except ImportError:
    DOCTR_AVAILABLE = False


def preprocess_image(input_path, output_path=None):
    img = cv2.imread(input_path)
    if img is None:
        raise FileNotFoundError(f"Cannot read image: {input_path}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    coords = np.column_stack(np.where(gray > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = gray.shape[:2]
    M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
    gray = cv2.warpAffine(gray, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                 cv2.THRESH_BINARY, 31, 2)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    if output_path:
        cv2.imwrite(output_path, gray)
    return gray


def run_tesseract(gray_img, languages="rus+eng"):
    config = "--psm 6"
    return pytesseract.image_to_string(gray_img, lang=languages, config=config).strip()


def run_doctr(gray_img):
    if not DOCTR_AVAILABLE:
        return None, 0.0
    temp_path = "/tmp/temp_page.png"
    cv2.imwrite(temp_path, gray_img)
    model = ocr_predictor(pretrained=True)
    doc = DocumentFile.from_images([temp_path])
    result = model(doc)
    rendered = result.render()
    conf = result.export().get("pages", [{}])[0].get("confidence", 0.0)
    return rendered, conf


def hybrid_ocr(input_path, languages="rus+eng"):
    gray = preprocess_image(input_path)
    text_tess = run_tesseract(gray, languages)
    text_doctr, conf_doctr = run_doctr(gray)
    text = text_doctr if DOCTR_AVAILABLE and conf_doctr > 0.6 else text_tess
    return unicodedata.normalize("NFC", text)


def ocr_fallback_for_pdf_page(pdf_page, page_num, pdf_name):
    img_path = f"/tmp/{pdf_name}_page{page_num}.png"
    pix = pdf_page.to_image(resolution=300)
    pix.original.save(img_path)
    text = hybrid_ocr(img_path)
    os.remove(img_path)
    return text
