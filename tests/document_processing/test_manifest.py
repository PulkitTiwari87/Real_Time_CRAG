from document_processing.chunker import TokenChunk
from document_processing.manifest import read_manifest, write_manifest


def _chunk(i: int) -> TokenChunk:
    return TokenChunk(
        chunk_id=f"doc1::{i}",
        document_id="doc1",
        source="doc1.txt",
        content=f"chunk {i} content",
        token_count=3,
    )


def test_write_and_read_manifest_round_trip(tmp_path):
    chunks = [_chunk(0), _chunk(1)]
    out = write_manifest(chunks, tmp_path / "chunks" / "manifest.json", chunk_size=200, overlap=20)
    assert out.is_file()

    manifest = read_manifest(out)
    assert manifest["chunk_count"] == 2
    assert manifest["chunk_size"] == 200
    assert manifest["overlap"] == 20
    assert manifest["chunks"][0]["chunk_id"] == "doc1::0"
    assert "generated_at" in manifest


def test_write_manifest_creates_parent_dirs(tmp_path):
    out_path = tmp_path / "deeply" / "nested" / "manifest.json"
    write_manifest([_chunk(0)], out_path, chunk_size=200, overlap=20)
    assert out_path.is_file()


def test_read_manifest_missing_raises(tmp_path):
    import pytest

    with pytest.raises(FileNotFoundError):
        read_manifest(tmp_path / "nope.json")
