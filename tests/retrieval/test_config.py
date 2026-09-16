import pytest

from retrieval.config import load_retrieval_config


def test_load_default_config_has_expected_keys():
    config = load_retrieval_config()
    assert config["retrieval"]["top_k"] == 5
    assert config["grader"]["confidence_threshold"] == 0.35


def test_load_missing_config_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_retrieval_config(tmp_path / "nope.yaml")
