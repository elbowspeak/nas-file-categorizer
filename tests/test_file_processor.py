"""
Test module for the FileProcessor integration.
These tests verify that our file scanning and image analysis components
work together correctly, handling various scenarios that might occur
when processing files on a NAS.
"""

from pathlib import Path

import pytest
from PIL import Image

from src.integration.file_processor import FileProcessor

@pytest.fixture
def processor_test_dir(tmp_path: Path) -> Path:
    """Creates a test directory structure for file processor testing."""
    # Create our main test directory
    test_dir = tmp_path / "test_nas"
    test_dir.mkdir()

    # Create some subdirectories to test recursive scanning
    images_dir = test_dir / "photos"
    documents_dir = test_dir / "documents"
    images_dir.mkdir()
    documents_dir.mkdir()

    # Create some test images that our analyzer can process
    simple_image = Image.new('RGB', (224, 224), color='red')
    gradient_image = Image.new('RGB', (224, 224))

    # Create a gradient pattern in our second image
    pixels = gradient_image.load()
    for i in range(224):
        for j in range(224):
            pixels[i, j] = (i, j, 100)

    # Save our test images
    simple_image.save(images_dir / "red_square.jpg")
    gradient_image.save(images_dir / "gradient.jpg")

    # Create some non-image files
    (documents_dir / "document.txt").write_text("Test document")
    (documents_dir / "data.csv").write_text("test,data,file")

    # Create an invalid image file to test error handling
    (images_dir / "invalid.jpg").write_text("Not a real image")

    return test_dir

def test_processor_initialization():
    """
    Verifies that the FileProcessor initializes correctly with both
    default and custom settings.
    """
    # Test with default settings
    processor = FileProcessor("/test/path")
    assert processor.scanner is not None
    assert processor.analyzer is not None
    assert processor.analyzer.confidence_threshold == 0.5

    # Test with custom confidence threshold
    custom_processor = FileProcessor("/test/path", confidence_threshold=0.75)
    assert custom_processor.analyzer.confidence_threshold == 0.75

def test_image_identification():
    """
    Tests our ability to correctly identify which files are images
    based on their extensions.
    """
    processor = FileProcessor("/test/path")

    # Test various file types
    assert processor.is_image({'extension': '.jpg'}) is True
    assert processor.is_image({'extension': '.JPEG'}) is True
    assert processor.is_image({'extension': '.png'}) is True
    assert processor.is_image({'extension': '.txt'}) is False
    assert processor.is_image({'extension': '.pdf'}) is False

def test_directory_processing(test_images_dir):
    """
    Tests the complete directory processing workflow, verifying that
    we can find files and analyze images correctly.
    """
    processor = FileProcessor(str(test_images_dir))
    results = processor.process_directory()

    # Verify we have all the expected result categories
    assert 'all_files' in results
    assert 'analyzed_images' in results
    assert 'errors' in results

    # Check that we found all files
    assert len(results['all_files']) > 0

    # Verify image analysis results
    assert len(results['analyzed_images']) > 0
    for image_result in results['analyzed_images']:
        assert 'file_info' in image_result
        assert 'analysis' in image_result
        assert 'categories' in image_result

def test_error_handling(test_images_dir):
    """Test error handling for invalid files."""
    processor = FileProcessor(str(test_images_dir))
    results = processor.process_directory()

    invalid_results = [r for r in results['analyzed_images']
                      if 'invalid.jpg' in r['file_info']['path']]
    if invalid_results:
        assert invalid_results[0]['analysis'].get('error') is not None

def test_category_summary(test_images_dir):
    """Test category summary generation."""
    processor = FileProcessor(str(test_images_dir))
    category_summary = processor.get_category_summary()
    assert isinstance(category_summary, dict)
    assert len(category_summary) > 0

if __name__ == "__main__":
    pytest.main([__file__])