import pdfplumber
from pathlib import Path


# Raised when the PDF cannot be processed.
class PDFExtractionError(Exception):
    pass


# Extracts plain text from a PDF file using pdfplumber.
def extract_text_from_pdf(file_path: Path) -> str:
    try:
        text_content = []

        with pdfplumber.open(file_path) as pdf:
            if len(pdf.pages) == 0:
                raise PDFExtractionError("PDF contains no pages.")

            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text_content.append(page_text)

        full_text = "\n".join(text_content).strip()

        if not full_text:
            raise PDFExtractionError("PDF text extraction returned empty content.")

        return full_text

    except Exception as e:
        raise PDFExtractionError(f"Failed to extract PDF text: {str(e)}")

