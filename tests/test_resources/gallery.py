"""Gallery structure creation utilities."""

from pathlib import Path
from PIL import Image

def create_gallery_structure(root: Path) -> Path:
    """Create gallery test structure."""
    root.mkdir(exist_ok=True)

    # Create directories
    (root / "landscapes").mkdir()
    (root / "people").mkdir()

    # Create images
    Image.new("RGB", (224, 224), "green").save(root / "landscapes/nature.jpg")
    Image.new("RGB", (224, 224), "blue").save(root / "people/portrait.jpg")

    return root