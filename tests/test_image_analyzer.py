"""
Test module for the image analysis functionality.
These tests ensure our image analyzer can correctly process images and handle various
scenarios that might occur when analyzing files from a NAS.
"""

from pathlib import Path

import numpy as np
import pytest

from src.analyzer.image_analyzer import ImageAnalyzer


def test_analyzer_initialization():
    """
    Verifies that the ImageAnalyzer initializes correctly with both default and custom
    settings. This ensures our analyzer is properly configured before attempting any analysis.
    """
    # Test default initialization
    default_analyzer = ImageAnalyzer()
    assert default_analyzer.confidence_threshold == 0.5
    assert default_analyzer.model is not None

    # Test custom confidence threshold
    custom_analyzer = ImageAnalyzer(confidence_threshold=0.75)
    assert custom_analyzer.confidence_threshold == 0.75
    assert custom_analyzer.model is not None


def test_image_preprocessing(test_images_dir: Path):
    """
    Verifies that our image preprocessing works correctly for various input images.
    Preprocessing is crucial as it ensures images are in the correct format for our
    neural network model.
    """
    analyzer = ImageAnalyzer()

    # Test preprocessing a valid image
    valid_path = test_images_dir / "red_square.jpg"
    processed = analyzer.preprocess_image(valid_path)
    assert processed is not None
    assert isinstance(processed, np.ndarray)
    assert processed.shape == (
        1,
        224,
        224,
        3,
    )  # Batch size 1, 224x224 pixels, 3 color channels

    # Test preprocessing an invalid image
    invalid_path = test_images_dir / "invalid.jpg"
    invalid_processed = analyzer.preprocess_image(invalid_path)
    assert invalid_processed is None

    # Test preprocessing an empty file
    empty_path = test_images_dir / "empty.jpg"
    empty_processed = analyzer.preprocess_image(empty_path)
    assert empty_processed is None


def test_image_analysis(test_images_dir: Path):
    """
    Tests the complete image analysis pipeline, from loading an image through getting
    predictions. This verifies our ability to identify content in images and handle
    various error conditions.
    """
    analyzer = ImageAnalyzer(confidence_threshold=0.01)

    # Test analyzing a valid image
    valid_path = test_images_dir / "red_square.jpg"
    result = analyzer.analyze_image(valid_path)

    # Verify the structure of successful analysis results
    assert "categories" in result
    assert "error" in result
    assert result["error"] is None
    assert isinstance(result["categories"], list)

    # For valid images, we should get some predictions
    # (even if it's just guessing what a red square might be)
    assert len(result["categories"]) > 0

    # Verify each prediction has the expected structure
    for prediction in result["categories"]:
        assert "category" in prediction
        assert "confidence" in prediction
        assert isinstance(prediction["confidence"], float)
        assert 0 <= prediction["confidence"] <= 1

    # Test analyzing an invalid image
    invalid_path = test_images_dir / "invalid.jpg"
    invalid_result = analyzer.analyze_image(invalid_path)
    assert invalid_result["error"] is not None
    assert len(invalid_result["categories"]) == 0


def test_batch_analysis(test_images_dir: Path):
    """
    Tests our ability to process multiple images in batch. This verifies that our analyzer
    can handle a collection of images efficiently while properly tracking results for each image.
    """
    analyzer = ImageAnalyzer(confidence_threshold=0.01)

    # Get all jpg files in the test directory
    image_paths = list(test_images_dir.glob("*.jpg"))
    assert len(image_paths) > 0  # Ensure we found our test images

    # Run batch analysis
    results = analyzer.batch_analyze(image_paths)

    # Verify we got results for every image
    assert len(results) == len(image_paths)

    # Check that each result has the expected structure
    for path, result in results.items():
        assert isinstance(result, dict)
        assert "categories" in result
        assert "error" in result

        # If it's our valid image, we should have categories
        if "red_square.jpg" in path:
            assert len(result["categories"]) > 0
            assert result["error"] is None

        # If it's our invalid image, we should have an error
        if "invalid.jpg" in path:
            assert len(result["categories"]) == 0
            assert result["error"] is not None


if __name__ == "__main__":
    pytest.main([__file__])
