"""Test file creation utilities."""

from pathlib import Path

def create_test_files(root: Path) -> Path:
    """Create basic test files."""
    root.mkdir(exist_ok=True)
    (root / "test1.txt").write_text("test content")
    (root / "test2.pdf").write_text("pdf content")
    (root / "test3.jpg").write_bytes(b"fake jpg content")
    return root