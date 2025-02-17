import logging
from pathlib import Path
from typing import Dict, List

class FileScanner:
    """Enhanced scanner with detailed logging and memory tracking."""

    def __init__(self, root_path: str):
        """Initialize scanner with root path."""
        self.root_path = Path(root_path)
        self.is_scanning = False
        self.total_files = 0
        self.processed_files = 0
        self.current_directory = ''
        self.results = {'files': [], 'errors': []}

        # Set up dedicated scanner logger
        self.logger = logging.getLogger('scanner')
        handler = logging.FileHandler('scanner.log')
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def scan_directory(self) -> Dict[str, List]:
        """Scan directory with detailed logging."""
        self.is_scanning = True
        results = {
            'files': [],
            'errors': []
        }

        try:
            print(f"Starting scan of {self.root_path}")

            # First count total files
            self.total_files = sum(1 for _ in self.root_path.rglob('*') if _.is_file())
            print(f"Found total of {self.total_files} files")

            # Then process them
            for file_path in self.root_path.rglob('*'):
                try:
                    if file_path.is_file():
                        file_info = self.scan(file_path)
                        if file_info:
                            results['files'].append(file_info)
                            self.processed_files += 1

                        if self.processed_files % 100 == 0:
                            print(f"Processed {self.processed_files} of {self.total_files} files...")

                except PermissionError as e:
                    error_msg = f"Permission error on {file_path}: {e}"
                    print(error_msg)
                    results['errors'].append(error_msg)
                    continue
                except OSError as e:
                    error_msg = f"OS error on {file_path}: {e}"
                    print(error_msg)
                    results['errors'].append(error_msg)
                    continue

            return results

        finally:
            self.is_scanning = False

    def scan(self, file_path: Path) -> Dict:
        """Scan single file and return metadata."""
        try:
            stats = file_path.stat()
            return {
                'path': str(file_path),
                'name': file_path.name,
                'extension': file_path.suffix.lower(),
                'size': stats.st_size,
                'modified': stats.st_mtime,
                'is_image': file_path.suffix.lower() in {'.jpg', '.jpeg', '.png', '.gif', '.heic'}
            }
        except (OSError, PermissionError) as e:
            self.logger.error("Error scanning file %s: %s", file_path, e)
            return None