"""Test helper functions."""

from pathlib import Path
from PIL import Image

def make_scanner_files(root: Path) -> Path:
    """Make scanner test files."""
    test_dir = root / "scanner_files"
    test_dir.mkdir()
    (test_dir / "test1.txt").write_text("test content")
    (test_dir / "test2.pdf").write_text("pdf content")
    (test_dir / "test3.jpg").write_bytes(b"fake jpg content")
    return test_dir

def make_analyzer_files(root: Path) -> Path:
    """Make analyzer test files."""
    test_dir = root / "analyzer_files"
    test_dir.mkdir()
    Image.new("RGB", (224, 224), color="red").save(test_dir / "red_square.jpg")
    Image.new("RGB", (224, 224), color="black").save(test_dir / "black_square.jpg")

    gradient = Image.new("RGB", (224, 224))
    pixels = gradient.load()
    for i in range(224):
        for j in range(224):
            pixels[i, j] = (i, j, 100)
    gradient.save(test_dir / "gradient.jpg")

    (test_dir / "invalid.jpg").write_text("Not a valid image")
    (test_dir / "empty.jpg").touch()
    return test_dir

def make_gallery_files(root: Path) -> Path:
    """Make gallery test files."""
    test_dir = root / "gallery_files"
    test_dir.mkdir()
    (test_dir / "landscapes").mkdir()
    (test_dir / "people").mkdir()
    Image.new('RGB', (224, 224), color='green').save(test_dir / "landscapes" / "nature.jpg")
    Image.new('RGB', (224, 224), color='blue').save(test_dir / "people" / "portrait.jpg")
    return test_dir