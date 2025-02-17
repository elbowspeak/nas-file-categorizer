"""
Module for face detection and recognition in images.
Provides functionality to detect, encode, and group faces across multiple images.
"""

import logging
from pathlib import Path
from typing import Dict, List

import face_recognition
import numpy as np

class FaceDetector:
    """
    Handles face detection and recognition operations.
    Uses face_recognition library for accurate face detection and encoding.
    """

    def __init__(self, tolerance: float = 0.6):
        """
        Initialize the face detector.

        Args:
            tolerance: Threshold for face similarity (lower = more strict)
        """
        self.tolerance = tolerance
        self.logger = logging.getLogger(__name__)
        self.known_faces = {}  # Will store face encodings
        self.face_locations = {}  # Will store face locations by image

    def analyze_image(self, image_path: Path) -> Dict:
        """
        Detect and encode faces in an image.

        Args:
            image_path: Path to the image file

        Returns:
            Dictionary containing face locations and encodings
        """
        try:
            # Load image and detect faces
            image = face_recognition.load_image_file(str(image_path))
            face_locs = face_recognition.face_locations(image, model="hog")

            if not face_locs:
                return {"faces": []}

            # Generate face encodings for each detected face
            face_encodings = face_recognition.face_encodings(image, face_locs)

            # Prepare results
            faces = []
            for loc, encoding in zip(face_locs, face_encodings):
                top, right, bottom, left = loc
                faces.append({
                    "location": {
                        "top": top,
                        "right": right,
                        "bottom": bottom,
                        "left": left
                    },
                    "encoding": encoding.tolist(),  # Convert numpy array to list for JSON
                    "size": (bottom - top) * (right - left)  # Face size in pixels
                })

            return {
                "faces": sorted(faces, key=lambda x: x["size"], reverse=True)
            }

        except (IOError, ValueError, RuntimeError) as e:
            self.logger.error("Error analyzing faces in %s: %s", image_path, e)
            return {"faces": [], "error": str(e)}

    def group_similar_faces(self, face_data: List[Dict]) -> List[List[int]]:
        """
        Group similar faces across multiple images.

        Args:
            face_data: List of face analysis results

        Returns:
            List of groups, where each group is a list of indices
        """
        encodings = []
        valid_indices = []

        # Collect all valid face encodings
        for idx, data in enumerate(face_data):
            if data.get("faces"):
                # Use the largest face in each image
                encodings.append(np.array(data["faces"][0]["encoding"]))
                valid_indices.append(idx)

        if not encodings:
            return []

        # Convert list to numpy array for efficient comparison
        encodings = np.array(encodings)

        # Initialize groups
        groups = []
        used = set()

        # Group similar faces
        for i, encoding in enumerate(encodings):
            if i in used:
                continue

            # Compare current face with all others
            distances = face_recognition.face_distance(encodings, encoding)
            matches = [valid_indices[j] for j, d in enumerate(distances)
                      if d <= self.tolerance]

            if matches:
                groups.append(matches)
                used.update(range(len(distances)))

        return groups

    def detect_faces(self, image_path: str) -> Dict:
        """Detect and analyze faces in an image."""
        try:
            # Load image
            image = face_recognition.load_image_file(image_path)

            # Find faces
            face_locations = face_recognition.face_locations(image)
            face_encodings = face_recognition.face_encodings(image, face_locations)

            results = {
                'face_count': len(face_locations),
                'faces': []
            }

            # Analyze each face
            for location, encoding in zip(face_locations, face_encodings):
                face_info = {
                    'location': location,
                    'encoding': encoding.tolist(),
                }
                results['faces'].append(face_info)

            return results

        except (IOError, ValueError, RuntimeError) as e:
            self.logger.error("Error detecting faces in %s: %s", image_path, e)
            return {'face_count': 0, 'faces': [], 'error': str(e)}
