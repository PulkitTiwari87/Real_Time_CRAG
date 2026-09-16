import pytest

from rag_baseline.loader import load_text_dir, load_text_file


def test_load_text_file_reads_content(tmp_path):
    p = tmp_path / "doc.txt"
    p.write_text("hello world", encoding="utf-8")
    doc = load_text_file(p)
    assert doc.content == "hello world"
    assert doc.document_id == "doc"
    assert doc.source == str(p)


def test_load_text_file_missing_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_text_file(tmp_path / "missing.txt")


def test_load_text_file_empty_raises(tmp_path):
    p = tmp_path / "empty.txt"
    p.write_text("   ", encoding="utf-8")
    with pytest.raises(ValueError):
        load_text_file(p)


def test_load_text_dir_loads_only_matching_files(tmp_path):
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    (tmp_path / "b.txt").write_text("b", encoding="utf-8")
    (tmp_path / "c.md").write_text("c", encoding="utf-8")
    docs = load_text_dir(tmp_path)
    assert {d.document_id for d in docs} == {"a", "b"}


def test_load_text_dir_missing_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_text_dir(tmp_path / "nope")
