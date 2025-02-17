"""
Test module for our image gallery web application.
These tests ensure our gallery can properly display and organize images from the NAS.
"""

import json
import time

import pytest


def test_gallery_initialization(gallery_app):
    """Test gallery initialization."""
    assert gallery_app.nas_path.exists()
    assert gallery_app.processor is not None
    assert gallery_app.image_cache == {}
    assert gallery_app.category_cache == {}

def test_image_processing(gallery_app, test_timeout):
    """Test image processing."""
    gallery_app.start_processing()
    time.sleep(min(2, test_timeout/5))  # Use shorter timeout
    assert len(gallery_app.image_cache) > 0

def test_api_endpoints(gallery_app):
    """
    Tests the gallery's API endpoints to ensure they return correct data
    in the expected format. This verifies our web interface will receive
    the information it needs.
    """
    with gallery_app.app.test_client() as client:
        # Test home page
        response = client.get('/')
        assert response.status_code == 200

        # Test image list endpoint
        response = client.get('/api/images')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)

        # Test categories endpoint
        response = client.get('/api/categories')
        assert response.status_code == 200
        categories = json.loads(response.data)
        assert isinstance(categories, list)

def test_category_filtering(gallery_app):
    """
    Verifies that our gallery can properly filter images by category.
    This ensures users can effectively browse images based on their content.
    """
    # First process some images
    gallery_app.start_processing()
    time.sleep(2)

    # Test filtering by each category
    for category in gallery_app.get_categories():
        images = gallery_app.get_images_by_category(category)
        assert isinstance(images, list)
        # Verify each image in the category has the correct categorization
        for image in images:
            assert any(cat['category'] == category
                      for cat in image.get('categories', []))

def test_error_handling(gallery_app, gallery_test_dir):
    """
    Tests how our gallery handles various error conditions, such as
    invalid files or processing failures. This ensures our application
    remains stable even when encountering problems.
    """
    # Create an invalid image file
    invalid_path = gallery_test_dir / "invalid.jpg"
    invalid_path.write_text("Not a valid image")

    with gallery_app.app.test_client() as client:
        # Test that the application continues running
        response = client.get('/')
        assert response.status_code == 200

        # Verify error handling in image processing
        gallery_app.start_processing()
        time.sleep(2)
        # The application should continue running despite the invalid file
        assert gallery_app.processing_thread.is_alive()

if __name__ == "__main__":
    pytest.main([__file__])
    