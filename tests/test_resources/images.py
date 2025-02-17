"""Test image creation utilities."""

from pathlib import Path
from PIL import Image

def create_test_images(root: Path) -> Path:
    """Create test images."""
    root.mkdir(exist_ok=True)

    # Valid images
    Image.new("RGB", (224, 224), "red").save(root / "red.jpg")
    Image.new("RGB", (224, 224), "black").save(root / "black.jpg")

    # Invalid images
    (root / "invalid.jpg").write_text("not an image")
    (root / "empty.jpg").touch()

    return root