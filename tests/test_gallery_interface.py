"""Gallery interface tests."""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

pytestmark = pytest.mark.timeout(30)

def test_gallery_loads(_client):
    """Test basic page load."""
    response = _client.get('/')
    assert response.status_code == 200
    assert b'NAS Image Gallery' in response.data

def test_gallery_ui(_browser):
    """Test UI components."""
    try:
        _browser.get("http://localhost:5000")
        WebDriverWait(_browser, 20).until(
            EC.presence_of_element_located((By.ID, "image-grid"))
        )
        assert _browser.find_element(By.ID, "search-input").is_displayed()
        assert _browser.find_element(By.ID, "sort-select").is_displayed()
    except TimeoutException:
        pytest.fail("UI elements not loaded")

def test_image_modal(_browser):
    """Test modal interaction."""
    try:
        _browser.get("http://localhost:5000")
        first_image = WebDriverWait(_browser, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "masonry-grid-item"))
        )
        first_image.click()

        WebDriverWait(_browser, 10).until(
            EC.presence_of_element_located((By.ID, "image-modal"))
        )
        modal = _browser.find_element(By.ID, "image-modal")
        assert "hidden" not in modal.get_attribute("class")
        assert _browser.find_element(By.ID, "modal-image").is_displayed()
    except TimeoutException:
        pytest.fail("Modal interaction failed")
