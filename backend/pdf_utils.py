import io

def extract_pdf_text(pdf_bytes: bytes) -> str:
    """
    Extract text from a PDF file given as bytes.
    Uses pdfplumber for best results (no Visual Studio needed on Windows).
    Falls back to pypdf if pdfplumber is not installed.
    """
    # Method 1: pdfplumber (best quality, works on Windows without Visual Studio)
    try:
        import pdfplumber
        text = ""
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        if text.strip():
            return text.strip()
    except ImportError:
        pass
    except Exception:
        pass

    # Method 2: pypdf (fallback)
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(pdf_bytes))
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        if text.strip():
            return text.strip()
    except ImportError:
        return "(PDF library not installed. Run: pip install pdfplumber)"
    except Exception as e:
        return f"(Error reading PDF: {str(e)})"

    return "(Could not extract text from PDF. Make sure it is not a scanned image-only PDF.)"