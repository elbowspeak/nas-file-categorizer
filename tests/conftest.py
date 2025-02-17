"""Test configuration for NAS Gallery."""

import logging
import os
import signal
import sys
import threading
import time
from pathlib import Path

import pytest
from PIL import Image
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import WebDriverException

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add source to path
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR / "src"))

# Resource creation functions
def _create_test_files(root: Path) -> Path:
    """Create basic test files."""
    root.mkdir(exist_ok=True)
    (root / "test1.txt").write_text("test content")
    (root / "test2.pdf").write_text("pdf content")
    (root / "test3.jpg").write_bytes(b"fake jpg content")
    return root

def _create_test_images(root: Path) -> Path:
    """Create test images."""
    root.mkdir(exist_ok=True)
    Image.new("RGB", (224, 224), "red").save(root / "red.jpg")
    Image.new("RGB", (224, 224), "black").save(root / "black.jpg")
    (root / "invalid.jpg").write_text("not an image")
    (root / "empty.jpg").touch()
    return root

def _create_gallery_structure(root: Path) -> Path:
    """Create gallery structure."""
    root.mkdir(exist_ok=True)
    (root / "landscapes").mkdir()
    (root / "people").mkdir()
    Image.new("RGB", (224, 224), "green").save(root / "landscapes/nature.jpg")
    Image.new("RGB", (224, 224), "blue").save(root / "people/portrait.jpg")
    return root

# Core dependencies
try:
    import tensorflow as tf
    print("✓ Found TensorFlow")
    logging.getLogger('tensorflow').setLevel(logging.ERROR)
except ImportError as e:
    print(f"✗ TensorFlow not found: {e}")
    tf = None

try:
    from src.web.app import GalleryApp
    print("✓ Found GalleryApp")
except ImportError as e:
    print(f"✗ GalleryApp not found: {e}")
    GalleryApp = None

try:
    from src.scanner.file_scanner import FileScanner
    print("✓ Found FileScanner")
except ImportError as e:
    print(f"✗ FileScanner not found: {e}")
    FileScanner = None

try:
    from src.analyzer.image_analyzer import ImageAnalyzer
    print("✓ Found ImageAnalyzer")
except ImportError as e:
    print(f"✗ ImageAnalyzer not found: {e}")
    ImageAnalyzer = None

@pytest.fixture(scope="session")
def _tensorflow():
    """Initialize TensorFlow."""
    if tf is None:
        pytest.skip("TensorFlow not available")
    return tf

@pytest.fixture(scope="session")
def _gallery_app():
    """Initialize GalleryApp."""
    if GalleryApp is None:
        pytest.skip("GalleryApp not available")
    return GalleryApp

@pytest.fixture
def _test_files(tmp_path):
    """Create test files."""
    return {
        'files': _create_test_files(tmp_path / 'files'),
        'images': _create_test_images(tmp_path / 'images'),
        'gallery': _create_gallery_structure(tmp_path / 'gallery')
    }

@pytest.fixture
def _scanner(_test_files):
    """Create FileScanner."""
    if FileScanner is None:
        pytest.skip("FileScanner not available")
    return FileScanner(str(_test_files['files']))

@pytest.fixture
def _analyzer(_tensorflow, _test_files):
    """Create ImageAnalyzer."""
    if ImageAnalyzer is None:
        pytest.skip("ImageAnalyzer not available")
    return ImageAnalyzer()

@pytest.fixture
def _app(_gallery_app, _test_files):
    """Create Flask app."""
    app = _gallery_app(str(_test_files['gallery']))
    app.app.config.update({
        'TESTING': True,
        'DEBUG': False,
        'SERVER_NAME': None
    })
    return app

@pytest.fixture
def _client(_app):
    """Create test client."""
    with _app.app.test_client() as client:
        yield client

@pytest.fixture
def _browser(_app):
    """Create Selenium browser."""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')

    server = None
    driver = None

    try:
        server = threading.Thread(
            target=_app.app.run,
            kwargs={
                'host': 'localhost',
                'port': 5000,
                'use_reloader': False,
                'debug': False,
                'threaded': True
            }
        )
        server.daemon = True
        server.start()
        time.sleep(2)

        try:
            driver = webdriver.Firefox(options=options)
            driver.implicitly_wait(10)
            yield driver
        except WebDriverException as e:
            logger.error("Failed to start Firefox: %s", e)
            pytest.skip("Firefox webdriver not available")

    except (RuntimeError, IOError) as e:
        logger.error("Test setup failed: %s", e)
        pytest.fail(f"Test environment setup failed: {e}")

    finally:
        if driver:
            try:
                driver.quit()
            except (WebDriverException, IOError) as e:
                logger.error("Error closing browser: %s", e)

        if server and server.is_alive():
            try:
                os.kill(os.getpid(), signal.SIGINT)
                server.join(timeout=1)
            except (RuntimeError, IOError) as e:
                logger.error("Error shutting down server: %s", e)
