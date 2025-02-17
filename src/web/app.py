"""
Web application module for our NAS image gallery with enhanced image handling capabilities.
"""

import mimetypes
from pathlib import Path
from threading import Thread

from flask import Flask, render_template, jsonify, send_from_directory
from pillow_heif import register_heif_opener
from src.integration.file_processor import FileProcessor

# Register HEIF opener to handle HEIC files
register_heif_opener()

print("Importing GalleryApp...")  # Debug print

class GalleryApp:
    """
    Enhanced gallery application with thumbnail generation and advanced sorting.
    Includes support for HEIC images commonly found on Apple devices.
    """

    # Define class-level constants
    THUMBNAIL_SIZE = (300, 300)
    JPEG_QUALITY = 85
    ALLOWED_MIME_TYPES = {
        'image/jpeg',
        'image/png',
        'image/gif',
        'image/bmp',
        'image/heic',
        'image/heif'
    }

    def __init__(self, nas_path: str):
        """Initialize the gallery with enhanced image handling capabilities."""
        # Add MIME types
        mimetypes.init()
        mimetypes.add_type('image/heic', '.heic')
        mimetypes.add_type('image/heif', '.heif')

        # Initialize paths and components
        self.nas_path = Path(nas_path)
        self.processor = FileProcessor(str(self.nas_path))

        # Set up Flask with correct template path
        template_dir = Path(__file__).parent / 'templates'
        static_dir = Path(__file__).parent / 'static'

        # Create required directories
        template_dir.mkdir(parents=True, exist_ok=True)
        static_dir.mkdir(parents=True, exist_ok=True)

        # Initialize Flask with absolute paths
        self.app = Flask(__name__,
                        template_folder=str(template_dir),
                        static_folder=str(static_dir),
                        static_url_path='')  # Serve static files from root URL

        print("\nTemplate directory:", template_dir)
        print("Static directory:", static_dir)
        print("Template exists:", (template_dir / 'gallery.html').exists())

        @self.app.route('/')
        def index():
            print("Received request for index page")  # Debug print
            return render_template('gallery.html')

        @self.app.route('/api/images')
        def get_images():
            return jsonify(list(self.processor.processed_images.values()))

        @self.app.route('/images/<path:filename>')
        def serve_image(filename):
            return send_from_directory(str(self.nas_path), filename)

        @self.app.route('/api/progress')
        def get_progress():
            scanner = self.processor.scanner
            return jsonify({
                'scanning_active': scanner.is_scanning,
                'total_files': scanner.total_files,
                'processed_files': scanner.processed_files,
                'current_directory': scanner.current_directory,
                'error_count': getattr(scanner, 'error_count', 0)  # Use error_count instead of errors
            })

        # Start scanning in background thread
        Thread(target=self.processor.process_directory, daemon=True).start()

    def run(self, port=8080):
        """Run the Flask application."""
        self.app.run(host='0.0.0.0', port=port, debug=True)
