"""Image analysis module.

Provides image analysis functionality using TensorFlow for object detection
and classification. Handles image preprocessing and batch analysis.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
from PIL import Image

class ImageAnalyzer:
    """Analyzes images using TensorFlow.

    Uses a pre-trained MobileNetV2 model to identify objects and scenes in images.
    Supports both single image and batch analysis with confidence thresholds.
    """

    def __init__(self, confidence_threshold: float = 0.5):
        """Initialize analyzer with confidence threshold.

        Args:
            confidence_threshold: Minimum confidence (0-1) for predictions
        """
        try:
            from tensorflow import keras
            self.keras = keras  # Store keras as instance variable
        except ImportError as exc:
            raise ImportError(
                "TensorFlow required. Install with: "
                "pip install tensorflow==2.15.0 (or tensorflow-macos==2.15.0 for Mac)"
            ) from exc

        self.confidence_threshold = confidence_threshold
        self.logger = logging.getLogger(__name__)

        try:
            self.model = self.keras.applications.MobileNetV2(
                weights="imagenet",
                include_top=True
            )
            self.logger.info("Model loaded")
        except (ValueError, RuntimeError, ImportError) as e:
            self.logger.error("Model load failed: %s", e)
            raise

    def preprocess_image(self, image_path: Path) -> Optional[np.ndarray]:
        """Prepare image for analysis.

        Args:
            image_path: Path to image file

        Returns:
            Preprocessed image array or None if processing fails
        """
        try:
            image = Image.open(image_path)
            image = image.convert("RGB")
            image = image.resize((224, 224))
            image_array = self.keras.utils.img_to_array(image)
            image_array = self.keras.applications.mobilenet_v2.preprocess_input(
                image_array
            )
            return np.expand_dims(image_array, axis=0)
        except (IOError, ValueError) as e:
            self.logger.error("Preprocessing failed: %s", e)
            return None

    def analyze_image(self, image_path: Path) -> Dict[str, List[Dict[str, float]]]:
        """Analyze image content.

        Args:
            image_path: Path to image file

        Returns:
            Dict containing:
                - categories: List of identified objects with confidence scores
                - error: Error message if analysis fails
        """
        result = {"categories": [], "error": None}

        try:
            processed_image = self.preprocess_image(image_path)
            if processed_image is None:
                result["error"] = "Failed to process image"
                return result

            predictions = self.model.predict(processed_image, verbose=0)
            decoded_predictions = self.keras.applications.mobilenet_v2.decode_predictions(
                predictions, top=5
            )[0]

            for _, category, confidence in decoded_predictions:
                if confidence >= self.confidence_threshold:
                    result["categories"].append({
                        "category": category,
                        "confidence": float(confidence)
                    })

        except (ValueError, RuntimeError) as e:
            error_msg = f"Analysis failed: {e}"
            self.logger.error(error_msg)
            result["error"] = error_msg

        return result

    def batch_analyze(self, image_paths: List[Path]) -> Dict[str, Dict]:
        """Analyze multiple images.

        Args:
            image_paths: List of paths to analyze

        Returns:
            Dict mapping file paths to their analysis results
        """
        results = {}
        for path in image_paths:
            self.logger.info("Analyzing: %s", path)
            results[str(path)] = self.analyze_image(path)
        return results
