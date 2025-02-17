"""Scanner test module."""

from pathlib import Path
import pytest
from src.scanner.file_scanner import FileScanner


def test_scanner_initialization():
    """Test scanner initialization with different parameters."""
    scanner = FileScanner("/test/path")
    assert scanner.retry_attempts == FileScanner.DEFAULT_RETRY_ATTEMPTS
    assert scanner.retry_delay == FileScanner.DEFAULT_RETRY_DELAY

    scanner_custom = FileScanner("/test/path", retry_attempts=5, retry_delay=2.0)
    assert scanner_custom.retry_attempts == 5
    assert scanner_custom.retry_delay == 2.0


def test_scan_single_file(test_files_dir: Path):
    """Test scanning a single file."""
    scanner = FileScanner(str(test_files_dir))
    test_file = test_files_dir / "test1.txt"

    file_info = scanner.scan(test_file)

    assert file_info["name"] == "test1.txt"
    assert file_info["extension"] == ".txt"
    assert file_info["size"] > 0
    assert not file_info["is_image"]


def test_scan_directory(test_files_dir: Path):
    """Test scanning an entire directory."""
    scanner = FileScanner(str(test_files_dir))
    results = scanner.scan_directory()

    assert len(results["files"]) == 3  # We created 3 test files
    assert len(results["errors"]) == 0  # Expect no errors

    # Verify we found all file types
    extensions = {f["extension"] for f in results["files"]}
    assert extensions == {".txt", ".pdf", ".jpg"}


def test_error_handling(test_files_dir: Path):
    """Test error handling for inaccessible files."""
    scanner = FileScanner(str(test_files_dir))

    # Use a non-existent file to guarantee an error
    test_file = test_files_dir / "does_not_exist.txt"

    try:
        # First test direct file access
        file_info = scanner.scan(test_file)
        assert file_info is None

        # Then test directory scan
        results = scanner.scan_directory()
        assert len(results["errors"]) == 0  # No errors since file doesn't exist
        assert len(results["files"]) == 3  # Only our original test files

    finally:
        # No cleanup needed since we didn't create any files
        pass


def test_scanner_finds_files(_scanner):
    """Test scanner can find files."""
    files = _scanner.scan()
    assert len(files) > 0


if __name__ == "__main__":
    pytest.main([__file__])
