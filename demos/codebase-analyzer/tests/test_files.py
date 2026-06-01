"""Enumeration must ignore noise, cap the count, and SURFACE truncation —
a silent cap would make a partial analysis look complete.
"""

from pipeline.files import enumerate_source_files, read_text


def _make_repo(root):
    (root / "main.py").write_text("print('hi')\n")
    (root / "util.py").write_text("x = 1\n")
    (root / "README.md").write_text("# docs\n")            # not source -> skipped
    (root / "node_modules").mkdir()
    (root / "node_modules" / "dep.js").write_text("//noise\n")  # ignored dir
    (root / "src").mkdir()
    (root / "src" / "app.py").write_text("y = 2\n")


def test_enumerate_filters_noise_and_detects_language(tmp_path):
    _make_repo(tmp_path)
    result = enumerate_source_files(tmp_path)
    assert "main.py" in result.files
    assert "README.md" not in result.files                 # non-source skipped
    assert all("node_modules" not in f for f in result.files)  # ignored dir
    assert result.languages == ["Python"]
    assert not result.truncated


def test_truncation_is_recorded_not_silent(tmp_path):
    for i in range(10):
        (tmp_path / f"f{i}.py").write_text("a = 1\n")
    result = enumerate_source_files(tmp_path, max_files=3)
    assert len(result.files) == 3
    assert result.truncated is True
    assert result.total_found == 10


def test_entrypoints_survive_truncation(tmp_path):
    # If we can only keep a few files, keep the entry point over a deep helper.
    (tmp_path / "main.py").write_text("a = 1\n")
    deep = tmp_path / "a" / "b" / "c"
    deep.mkdir(parents=True)
    (deep / "helper.py").write_text("a = 1\n")
    result = enumerate_source_files(tmp_path, max_files=1)
    assert result.files == ["main.py"]


def test_read_text_tolerates_bad_encoding(tmp_path):
    (tmp_path / "weird.py").write_bytes(b"x = '\xff\xfe'\n")
    text = read_text(tmp_path, "weird.py")
    assert "x =" in text  # decoded with replacement, did not raise
