"""
Module for scanning NAS directories and cataloging files.
Provides functionality to recursively traverse directories and collect file metadata.
"""

from pathlib import Path
import logging
from typing import Generator, Dict, Optional
from datetime import datetime
import time


class NASScanner:
    """
    A scanner that explores NAS directories and catalogs files with network resilience.
    Includes retry mechanisms for handling temporary network issues.
    """

    def __init__(
        self, root_path: str, retry_attempts: int = 3, retry_delay: float = 1.0
    ):
        """
        Initialize the NAS scanner with retry capabilities for network resilience.

        Args:
            root_path: The base path to scan on the NAS
            retry_attempts: Number of times to retry if a network error occurs
            retry_delay: Time to wait between retries (in seconds)
        """
        self.root_path = Path(root_path)
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def scan_with_retry(self, path: Path) -> Optional[Dict[str, str]]:
        """
        Attempts to scan a file with retry logic for network resilience.
        Like a librarian who doesn't give up after finding a locked door,
        but tries again a few times before moving on.
        """
        for attempt in range(self.retry_attempts):
            try:
                if not path.is_file():
                    return None

                stats = path.stat()
                return {
                    "path": str(path.absolute()),
                    "name": path.name,
                    "extension": path.suffix.lower(),
                    "size": stats.st_size,
                    "created": self.format_timestamp(stats.st_ctime),
                    "modified": self.format_timestamp(stats.st_mtime),
                }
            except OSError as e:
                if attempt < self.retry_attempts - 1:
                    self.logger.warning(
                        "Retry %d: Error accessing %s: %s", attempt + 1, path, e
                    )
                    time.sleep(self.retry_delay)
                else:
                    self.logger.error(
                        "Failed to access %s after %d attempts: %s",
                        path,
                        self.retry_attempts,
                        e,
                    )
                    return None

    def scan_directory(self) -> Generator[Dict[str, str], None, None]:
        """
        Scans the NAS directory with improved error handling and network resilience.
        """
        self.logger.info("Starting scan from %s", self.root_path)

        try:
            for entry in self.root_path.rglob("*"):
                file_info = self.scan_with_retry(entry)
                if file_info:
                    self.logger.debug("Found file: %s", file_info["name"])
                    yield file_info

        except OSError as e:
            self.logger.error("Error scanning directory: %s", e)
            raise

    def format_timestamp(self, timestamp: float) -> str:
        """
        Converts a Unix timestamp into a human-readable date string.
        """
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
