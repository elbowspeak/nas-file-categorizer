"""
Module that coordinates file scanning and image analysis.
Project manager, bringing together our file discovery and image understanding capabilities.
"""

import logging
from pathlib import Path
from typing import Dict, Set
from datetime import datetime

from src.scanner.file_scanner import FileScanner
from src.analyzer.face_detector import FaceDetector

class FileProcessor:
    """
    Coordinates the scanning and analysis of files on the NAS.
    This class brings together our file scanning and image analysis capabilities,
    managing the workflow of finding files and understanding their contents.
    """

    # Define common image extensions we'll look for
    IMAGE_EXTENSIONS: Set[str] = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.heic'}

    def __init__(self, root_path: str):
        """
        Initialize the file processor with both scanning and analysis capabilities.

        Args:
            root_path: The base directory to process
        """
        self.root_path = root_path
        self.scanner = FileScanner(root_path)
        self.face_detector = FaceDetector()
        self.processed_images = {}
        self.face_groups = {}  # Store groups of similar faces

        # Set up logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    def process_directory(self) -> Dict:
        """Process directory with enhanced face detection."""
        print("Starting directory processing...")
        self.scanner.is_scanning = True
        results = {
            'analyzed_images': [],
            'face_groups': [],
            'errors': []
        }

        try:
            print("Scanning for files...")
            scan_results = self.scanner.scan_directory()
            print(f"Found {len(scan_results['files'])} files")

            print("Starting to process images...")

            for file_info in scan_results['files']:
                try:
                    if self._is_image_file(file_info['path']):
                        print(f"Processing image: {file_info['path']}")
                        image_info = self._process_image(file_info['path'])
                        if image_info:
                            self.processed_images[file_info['path']] = image_info
                            results['analyzed_images'].append(image_info)
                except Exception as e:
                    print(f"Error processing {file_info['path']}: {e}")
                    results['errors'].append(str(e))

            return results

        finally:
            self.scanner.is_scanning = False

    def _is_image_file(self, path: str) -> bool:
        """
        Check if file is a supported image type.

        Args:
            path: Path to the file to check

        Returns:
            bool: True if the file is a supported image type
        """
        return Path(path).suffix.lower() in self.IMAGE_EXTENSIONS

    def get_face_groups(self) -> Dict:
        """
        Get the current face groupings.

        Returns:
            Dict containing face groups and their associated images
        """
        return self.face_groups

    def _process_image(self, file_path: str) -> Dict:
        """Process a single image file."""
        print(f"Processing image: {file_path}")
        try:
            file_info = {
                'path': file_path,
                'name': Path(file_path).name,
                'size': Path(file_path).stat().st_size,
                'modified': datetime.fromtimestamp(Path(file_path).stat().st_mtime).isoformat()
            }

            # For now, just return basic file info
            return {
                'file_info': file_info,
                'categories': []  # We'll add categories later
            }

        except (OSError, ValueError) as e:
            print(f"Error processing {file_path}: {str(e)}")
            return None
