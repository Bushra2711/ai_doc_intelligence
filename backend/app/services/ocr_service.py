from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Windows installation path used by the official Tesseract installer.
# pytesseract can also use Tesseract from PATH when it is configured.
TESSERACT_EXE = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")


class OCRError(Exception):
    """Base error raised by OCR operations."""


class OCRDependencyError(OCRError):
    """Raised when the Python OCR dependencies or Tesseract executable are unavailable."""


def _load_ocr_dependencies():
    try:
        import pytesseract
        from PIL import Image
    except ImportError as exc:
        raise OCRDependencyError(
            "OCR dependencies are not installed. Install pytesseract and Pillow."
        ) from exc

    # Prefer the standard Windows installation path when it exists. This avoids
    # requiring users to manually configure the Windows PATH variable.
    if TESSERACT_EXE.is_file():
        pytesseract.pytesseract.tesseract_cmd = str(TESSERACT_EXE)

    try:
        pytesseract.get_tesseract_version()
    except Exception as exc:
        raise OCRDependencyError(
            "Tesseract OCR is not installed or is not available on PATH."
        ) from exc

    return pytesseract, Image


def ocr_image(image_path: Path) -> str:
    """Extract text from an image file using Tesseract OCR."""
    pytesseract, Image = _load_ocr_dependencies()

    try:
        with Image.open(image_path) as image:
            image = image.convert("RGB")
            return pytesseract.image_to_string(image).strip()
    except Exception as exc:
        logger.exception("OCR failed for image %s", image_path)
        raise OCRError(f"Failed to OCR image: {image_path.name}") from exc


def ocr_pdf(pdf_path: Path, dpi: int = 200) -> str:
    """Render PDF pages and OCR them, intended for scanned/image-only PDFs."""
    pytesseract, _ = _load_ocr_dependencies()

    try:
        import pymupdf
    except ImportError as exc:
        raise OCRDependencyError("PyMuPDF is required for PDF OCR.") from exc

    try:
        pages: list[str] = []
        with pymupdf.open(str(pdf_path)) as pdf:
            for page_number, page in enumerate(pdf, start=1):
                pixmap = page.get_pixmap(dpi=dpi, alpha=False)
                image = pixmap.pil_image()
                text = pytesseract.image_to_string(image).strip()
                if text:
                    pages.append(f"[Page {page_number}]\n{text}")

        return "\n\n".join(pages).strip()
    except Exception as exc:
        logger.exception("OCR failed for PDF %s", pdf_path)
        raise OCRError(f"Failed to OCR PDF: {pdf_path.name}") from exc
