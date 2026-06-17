import io
import traceback
import pdfplumber
import PyPDF2


def extract_resume_text(pdf_file):
    try:
        file_bytes = pdf_file.read()
        if not file_bytes:
            return ""

        # Try pdfplumber first
        text = _extract_with_pdfplumber(file_bytes)

        # Fall back to PyPDF2 if pdfplumber got nothing
        if not text or len(text.strip()) < 50:
            print("pdfplumber got little/no text, trying PyPDF2...")
            text = _extract_with_pypdf2(file_bytes)

        return _clean_text(text)

    except Exception as e:
        print(f"PDF Extraction Error: {type(e).__name__}: {e}")
        traceback.print_exc()
        return ""


def _extract_with_pdfplumber(file_bytes):
    try:
        resume_text = ""
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            print(f"pdfplumber: PDF has {len(pdf.pages)} page(s)")
            for page_num, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    resume_text += page_text + "\n"
                    print(f"Page {page_num + 1}: {len(page_text)} chars")
        return resume_text
    except Exception as e:
        print(f"pdfplumber failed: {e}")
        return ""


def _extract_with_pypdf2(file_bytes):
    try:
        resume_text = ""
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        print(f"PyPDF2: PDF has {len(pdf_reader.pages)} page(s)")
        for page_num, page in enumerate(pdf_reader.pages):
            try:
                page_text = page.extract_text()
                if page_text:
                    resume_text += page_text + "\n"
                    print(f"Page {page_num + 1}: {len(page_text)} chars")
            except Exception as page_err:
                print(f"Error on page {page_num + 1}: {page_err}")
        return resume_text
    except Exception as e:
        print(f"PyPDF2 failed: {e}")
        return ""


def _clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.strip() for line in text.split("\n")]
    lines = [line for line in lines if line]
    return "\n".join(lines).strip()