from __future__ import annotations

import argparse
import hashlib
import os
import re
from pathlib import Path

from core.chroma_store import ChromaStore


def _sha1(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()


def _chunk_text(text: str, *, max_chars: int = 1200, overlap: int = 120) -> list[tuple[str, str]]:
    sections = _split_sections(text)
    out: list[tuple[str, str]] = []
    for section, section_text in sections:
        out.extend((section, chunk) for chunk in _chunk_section(section_text, max_chars=max_chars, overlap=overlap))
    return out


def _chunk_section(text: str, *, max_chars: int, overlap: int) -> list[str]:
    text = " ".join(text.split())
    if not text:
        return []
    chunks: list[str] = []
    i = 0
    while i < len(text):
        j = min(i + max_chars, len(text))
        chunk = text[i:j].strip()
        if chunk:
            chunks.append(chunk)
        if j == len(text):
            break
        i = max(j - overlap, i + 1)
    return chunks


def _split_sections(text: str) -> list[tuple[str, str]]:
    lines = text.splitlines()
    sections: list[tuple[str, list[str]]] = []
    current_title = "General"
    current_lines: list[str] = []
    heading_re = re.compile(r"^([A-Z][A-Za-z0-9 /&(),:+-]{2,80})$")
    for line in lines:
        stripped = line.strip()
        if heading_re.match(stripped) and len(stripped.split()) <= 10:
            if current_lines:
                sections.append((current_title, current_lines))
            current_title = stripped
            current_lines = []
        else:
            current_lines.append(line)
    if current_lines:
        sections.append((current_title, current_lines))
    if not sections:
        return [("General", text)]
    return [(title, "\n".join(body)) for title, body in sections]


def extract_pdf_text(pdf_path: Path) -> list[tuple[int, str]]:
    try:
        import fitz  # type: ignore
    except Exception as e:
        raise RuntimeError("PyMuPDF is required to ingest PDF files. Install PyMuPDF or ingest TXT/MD instead.") from e

    doc = fitz.open(pdf_path)
    out: list[tuple[int, str]] = []
    for page_idx in range(doc.page_count):
        page = doc.load_page(page_idx)
        out.append((page_idx + 1, page.get_text("text")))
    doc.close()
    return out


def ingest_file(store: ChromaStore, path: Path) -> int:
    if path.suffix.lower() == ".pdf":
        pages = extract_pdf_text(path)
        added = 0
        for page_num, text in pages:
            for idx, (section, chunk) in enumerate(_chunk_text(text)):
                chunk_id = f"{path.stem}_p{page_num:03d}_{idx:03d}_{_sha1(chunk)[:8]}"
                store.add_texts(
                    ids=[chunk_id],
                    texts=[chunk],
                    metadatas=[
                        {
                            "doc_id": path.stem,
                            "chunk_id": chunk_id,
                            "source_title": path.name,
                            "section": section,
                            "page": page_num,
                            "path": str(path),
                            "source_type": "guideline",
                        }
                    ],
                )
                added += 1
        return added

    text = path.read_text(encoding="utf-8", errors="ignore")
    section_chunks = _chunk_text(text)
    ids = [f"{path.stem}_{i:03d}_{_sha1(c)[:8]}" for i, (_, c) in enumerate(section_chunks)]
    metas = [
        {
            "doc_id": path.stem,
            "chunk_id": ids[i],
            "source_title": path.name,
            "section": section_chunks[i][0],
            "path": str(path),
            "source_type": "pubmed_style" if "abstract" in text[:500].lower() else "guideline",
        }
        for i in range(len(section_chunks))
    ]
    chunks = [chunk for _, chunk in section_chunks]
    if chunks:
        store.add_texts(ids=ids, texts=chunks, metadatas=metas)
    return len(section_chunks)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", required=True, help="PDF or TXT/MD file to ingest")
    args = ap.parse_args()

    p = Path(args.path)
    if not p.exists():
        raise SystemExit(f"File not found: {p}")

    store = ChromaStore()
    before = store.count()
    added = ingest_file(store, p)
    after = store.count()

    print(f"collection={store.collection_name} before={before} added={added} after={after}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
