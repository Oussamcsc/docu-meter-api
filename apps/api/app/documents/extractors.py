from dataclasses import dataclass
from io import BytesIO


@dataclass(frozen=True)
class ExtractedDocument:
    text: str
    characters: int
    mime_type: str


def extract_txt_text(content: bytes) -> ExtractedDocument:
    text = content.decode("utf-8").strip()
    return ExtractedDocument(
        text=text,
        characters=len(text),
        mime_type="text/plain",
    )


def extract_pdf_text(content: bytes) -> ExtractedDocument:
    try:
        import fitz
    except ImportError as exc:
        raise RuntimeError("PDF extraction requires PyMuPDF to be installed") from exc

    pages: list[str] = []
    with fitz.open(stream=BytesIO(content), filetype="pdf") as pdf:
        for page in pdf:
            pages.append(page.get_text())

    text = "\n".join(pages).strip()
    return ExtractedDocument(
        text=text,
        characters=len(text),
        mime_type="application/pdf",
    )
