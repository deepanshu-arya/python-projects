import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import os

UPLOAD_DIR = "ocr_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def read_image_text(image_path: str) -> str:
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text

def read_pdf_text(pdf_path: str) -> str:
    pages = convert_from_path(pdf_path)
    full_text = ""

    for page in pages:
        text = pytesseract.image_to_string(page)
        full_text += text + "\n"

    return full_text
