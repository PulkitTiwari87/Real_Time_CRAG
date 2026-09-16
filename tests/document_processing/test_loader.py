import pytest

from document_processing.loader import PDFLoader, TextLoader, clean_text


def _build_minimal_pdf(text: str) -> bytes:
    """Hand-build a minimal single-page PDF with a real text content stream.

    Avoids adding a PDF-authoring dependency (e.g. reportlab) purely for
    test fixtures -- pypdf can read this directly.
    """
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 4 0 R >> >> "
        b"/MediaBox [0 0 300 200] /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    stream_data = f"BT /F1 24 Tf 20 100 Td ({text}) Tj ET".encode()
    objects.append(b"<< /Length " + str(len(stream_data)).encode() + b" >>\nstream\n" + stream_data + b"\nendstream")

    out = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for i, obj in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n".encode() + obj + b"\nendobj\n"

    xref_offset = len(out)
    n = len(objects) + 1
    out += f"xref\n0 {n}\n".encode()
    out += b"0000000000 65535 f \n"
    for off in offsets[1:]:
        out += f"{off:010d} 00000 n \n".encode()
    out += b"trailer\n<< /Size " + str(n).encode() + b" /Root 1 0 R >>\nstartxref\n" + str(xref_offset).encode() + b"\n%%EOF"
    return bytes(out)


def test_clean_text_normalizes_whitespace_and_unicode():
    assert clean_text("  hello   world  \n\n  again  ") == "hello world\nagain"
    assert clean_text("café") == "café"  # NFKC-composes e + combining acute


def test_text_loader_reads_and_cleans_content(tmp_path):
    p = tmp_path / "doc.txt"
    p.write_text("  hello   world  ", encoding="utf-8")
    doc = TextLoader().load(p)
    assert doc.content == "hello world"
    assert doc.document_id == "doc"
    assert doc.source == str(p)


def test_text_loader_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        TextLoader().load(tmp_path / "missing.txt")


def test_text_loader_empty_after_cleaning_raises(tmp_path):
    p = tmp_path / "blank.txt"
    p.write_text("   \n  \n  ", encoding="utf-8")
    with pytest.raises(ValueError):
        TextLoader().load(p)


def test_text_loader_load_dir_filters_by_pattern(tmp_path):
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    (tmp_path / "b.txt").write_text("b", encoding="utf-8")
    (tmp_path / "c.md").write_text("c", encoding="utf-8")
    docs = TextLoader().load_dir(tmp_path)
    assert {d.document_id for d in docs} == {"a", "b"}


def test_text_loader_load_dir_missing_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        TextLoader().load_dir(tmp_path / "nope")


def test_text_loader_load_dir_skips_bad_files_and_records_errors(tmp_path):
    (tmp_path / "good.txt").write_text("real content", encoding="utf-8")
    (tmp_path / "empty.txt").write_text("   ", encoding="utf-8")  # fails cleaning -> ValueError

    loader = TextLoader()
    docs = loader.load_dir(tmp_path)

    assert {d.document_id for d in docs} == {"good"}
    assert len(loader.errors) == 1
    assert loader.errors[0].path.endswith("empty.txt")


def test_pdf_loader_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        PDFLoader().load(tmp_path / "missing.pdf")


def test_pdf_loader_corrupted_pdf_raises(tmp_path):
    p = tmp_path / "corrupt.pdf"
    p.write_bytes(b"not a real pdf file")
    with pytest.raises(ValueError):
        PDFLoader().load(p)


def test_pdf_loader_blank_page_raises(tmp_path):
    pytest.importorskip("pypdf")
    from pypdf import PdfWriter

    p = tmp_path / "sample.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    with open(p, "wb") as f:
        writer.write(f)

    # A blank page has no extractable text, so this should raise, not crash.
    with pytest.raises(ValueError):
        PDFLoader().load(p)


def test_pdf_loader_extracts_real_text(tmp_path):
    p = tmp_path / "real.pdf"
    p.write_bytes(_build_minimal_pdf("Hello Phase 02 PDF Test"))
    doc = PDFLoader().load(p)
    assert "Hello Phase 02 PDF Test" in doc.content
    assert doc.document_id == "real"
