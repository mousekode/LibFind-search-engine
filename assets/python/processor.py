import os
import json
from pathlib import Path
import re

# Try to import PyPDF2, if not available print a helpful message and raise
try:
    from PyPDF2 import PdfReader
except Exception as e:
    PdfReader = None
    _IMPORT_ERROR = e

def _read_pdf_text(file_path, max_pages=5):
    """
    Read text from up to max_pages of the PDF (to capture title/abstract).
    Returns a single string.
    """
    if PdfReader is None:
        raise RuntimeError(
            "PyPDF2 is required to process PDFs. Install with `pip install PyPDF2`. "
            f"Import error: {_IMPORT_ERROR}"
        )

    text_chunks = []
    try:
        reader = PdfReader(str(file_path))
        # Try to handle encrypted PDFs
        if getattr(reader, "is_encrypted", False):
            try:
                reader.decrypt("")  # try empty password
            except Exception:
                pass  # leave as-is; reading pages may still fail and be caught below

        num_pages = min(len(reader.pages), max_pages)
        for i in range(num_pages):
            try:
                page = reader.pages[i]
                page_text = page.extract_text() or ""
                text_chunks.append(page_text)
            except Exception:
                continue
    except Exception as e:
        raise RuntimeError(f"Error reading PDF '{file_path.name}': {e}")

    return "\n".join(text_chunks)


def _extract_title_from_pdf(file_path):
    """Try metadata title, fall back to first non-empty line of first page."""
    if PdfReader is None:
        raise RuntimeError(
            "PyPDF2 is required to process PDFs. Install with `pip install PyPDF2`."
        )

    try:
        reader = PdfReader(str(file_path))
        meta = getattr(reader, "metadata", None) or getattr(reader, "documentInfo", None)
        # PyPDF2 metadata keys may vary; attempt common ones
        if meta:
            # metadata.title may be available as meta.title or meta.get('/Title')
            title = None
            if hasattr(meta, "title") and meta.title:
                title = meta.title
            else:
                # meta could be a dictionary-like
                for key in ("/Title", "Title"):
                    if key in meta and meta[key]:
                        title = meta[key]
                        break
            if title:
                return str(title).strip()

        # Fallback: extract first non-empty line from first page text
        first_page_text = _read_pdf_text(file_path, max_pages=1)
        for line in first_page_text.splitlines():
            line = line.strip()
            if line:
                # Heuristic: ignore common heading like "Abstract" if it appears first
                if re.match(r'^(abstract\b)', line, re.I):
                    continue
                return line[:200]  # cap length for title
    except Exception:
        pass

    # Final fallback: filename without extension
    return file_path.stem

def _extract_abstract_from_text(text, max_length=1000):
    """
    Find the 'abstrak' (Indonesian) section first, falling back to 'abstract' (English).
    If found, return a cleaned paragraph. Otherwise return the first max_length characters of text.
    """
    if not text:
        return ""

    # Normalize whitespace
    normalized = re.sub(r'\r\n|\r', '\n', text)

    # Prefer Indonesian 'abstrak', then English 'abstract'
    for heading_pattern in (r'\babstrak\b[:\s\-]*\n?', r'\babstract\b[:\s\-]*\n?'):
        m = re.search(heading_pattern, normalized, re.I)
        if m:
            start = m.end()
            tail = normalized[start:start + max_length * 2]  # read a bit more to find paragraph break
            paragraphs = re.split(r'\n{2,}|\n(?=[A-Z][^\n]{0,100}\n)', tail)
            if paragraphs:
                abstract = paragraphs[0].strip()
                # Remove any leading ':' or '-' or whitespace
                abstract = re.sub(r'^[\s\:\-]+', '', abstract)
                # Truncate to max_length
                return abstract[:max_length].strip()

    # No explicit abstract found: fallback to first max_length chars of text
    compact = re.sub(r'\s+', ' ', normalized).strip()
    return compact[:max_length]

# New sanitization helpers
def _sanitize_text(s):
    """Replace colons with periods in a string."""
    if not isinstance(s, str):
        return s
    return s.replace(":", ".")

def _sanitize_filename(filename):
    """Removes characters that cause 404 errors in URLs."""
    # Replace colons, slashes, and other risky characters with underscores
    return re.sub(r'[:*?"<>|]', '_', filename)

def _sanitize_documents(documents):
    """Return a shallow copy of documents with semicolons replaced in all string values."""
    sanitized = []
    for doc in documents:
        new_doc = {}
        for k, v in doc.items():
            new_doc[k] = _sanitize_text(v) if isinstance(v, str) else v
        sanitized.append(new_doc)
    return sanitized

def process_documents(document_folder="/document"):
    """
    Reads all PDF documents from a folder and converts them to JSON format
    matching the DOCUMENTS structure in searchApp.py

    For each PDF:
      - id: incremental integer
      - title: from PDF filename (stem)
      - snippet: abstract section if found, otherwise first chars of content
    """
    documents = []
    doc_id = 1

    # Get all files from the document folder
    document_path = Path(document_folder)

    if not document_path.exists():
        print(f"Error: Folder '{document_folder}' does not exist")
        return documents

    # Process each file (PDFs only)
    for file_path in sorted(document_path.iterdir()):
        if file_path.is_file() and file_path.suffix.lower() == ".pdf":
            try:
                # Extract text for abstract/snippet (look at first few pages)
                try:
                    text = _read_pdf_text(file_path, max_pages=5)
                except RuntimeError as e:
                    print(f"✗ Error reading PDF {file_path.name}: {e}")
                    continue

                # Title is taken from filename (no metadata)
                title = file_path.stem
                title = _sanitize_text(title)

                # Extract abstract from text or fallback to first chars
                snippet = _extract_abstract_from_text(text, max_length=500)
                if not snippet:
                    # final fallback: use start of full text
                    snippet = (text[:500] if text else "")
                snippet = _sanitize_text(snippet)
                filename = file_path.name
                web_path = f"assets/python/document/{filename}"

                doc = {
                    "id": doc_id,
                    "title": title,
                    "snippet": snippet,
                    "doc_path": web_path
                }

                documents.append(doc)
                doc_id += 1
                print(f"✓ Processed: {file_path.name}")

            except Exception as e:
                print(f"✗ Error processing {file_path.name}: {str(e)}")
                continue

    return documents

def save_documents_json(documents, output_file="assets/python/processed.json"):
    """
    Saves the processed documents to a JSON file
    """
    try:
        sanitized = _sanitize_documents(documents)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(sanitized, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Saved {len(documents)} documents to {output_file}")
    except Exception as e:
        print(f"✗ Error saving JSON: {str(e)}")

if __name__ == "__main__":
    # Process documents
    script_dir = Path(__file__).parent
    document_dir = script_dir / "document"
    docs = process_documents(str(document_dir))

    # Save to JSON
    if docs:
        save_documents_json(docs)
        print(json.dumps(_sanitize_documents(docs)[:2], indent=2, ensure_ascii=False))  # Preview first 2 docs
    else:
        print("No documents found to process")
# ...existing code...