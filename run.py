"""Main script to run the NAS Gallery web application with test images."""

import socket
from pathlib import Path
from src.web.app import GalleryApp

def is_port_available(port: int) -> bool:
    """Check if a port is available."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('0.0.0.0', port))
            return True
        except OSError:
            return False

if __name__ == "__main__":
    print("Starting application...")

    # Use the NAS pictures directory
    nas_path = Path("/Volumes/PICTURES")

    # Verify NAS connection
    print("Checking NAS connection at:", nas_path)
    if not nas_path.exists():
        print("Error: Cannot access NAS path. Please ensure the NAS is mounted.")
        exit(1)

    print("NAS connection successful")
    print("Creating gallery app...")
    gallery = GalleryApp(str(nas_path))

    # Find an available port
    available_port = None  # pylint: disable=invalid-name
    for test_port in range(8080, 8090):
        if is_port_available(test_port):
            available_port = test_port
            break
        print(f"Port {test_port} is in use, trying next port...")

    if available_port is None:
        print("Error: Could not find an available port between 8080-8089")
        exit(1)

    print("\nStarting web server...")
    print(f"App will be available at: http://localhost:{available_port}")
    print(f"                     or: http://127.0.0.1:{available_port}")
    print(f"              External: http://0.0.0.0:{available_port}")
    print("\nPress CTRL+C to stop the server")

    gallery.app.run(
        debug=True,
        host='0.0.0.0',
        port=available_port,
        use_reloader=False  # Disable reloader here instead of using env vars
    )
