import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from services.detection_service import DetectionService
from services.face_detector import FaceBox, FaceDetector
from services.mask_classifier import MaskClassifier


class RecordingModel:
    output_shape = (None, 3)

    def __init__(self) -> None:
        self.batch = None

    def predict(self, batch, verbose=0):
        self.batch = batch
        return np.array([[0.05, 0.9, 0.05]], dtype=np.float32)


class StubDetector:
    def detect(self, image):
        return [FaceBox(x=10, y=10, width=20, height=20)]


class StubClassifier:
    def predict(self, image):
        return "Mask", 0.9


class MaskClassifierTests(unittest.TestCase):
    def test_predict_converts_bgr_to_raw_rgb_for_embedded_preprocessing(self):
        with tempfile.TemporaryDirectory() as directory:
            labels_path = Path(directory) / "labels.json"
            labels_path.write_text(json.dumps(["Incorrect Mask", "Mask", "No Mask"]), encoding="utf-8")
            classifier = MaskClassifier(Path(directory) / "missing.h5", labels_path, image_size=2)
            model = RecordingModel()
            classifier.model = model
            classifier.model_runtime = "keras"

            face = np.zeros((2, 2, 3), dtype=np.uint8)
            face[:, :] = [10, 20, 30]
            label, confidence = classifier.predict(face)

            self.assertEqual(label, "Mask")
            self.assertEqual(confidence, 0.9)
            np.testing.assert_array_equal(model.batch[0, 0, 0], np.array([30, 20, 10], dtype=np.float32))

    def test_rejects_empty_face_crop(self):
        classifier = MaskClassifier(Path("missing.h5"), Path("missing.json"))
        with self.assertRaises(ValueError):
            classifier.predict(np.empty((0, 0, 3), dtype=np.uint8))


class FaceDetectorTests(unittest.TestCase):
    def test_missing_dnn_model_falls_back_to_haar(self):
        detector = FaceDetector("dnn", model_path=Path("missing.onnx"))
        self.assertEqual(detector.backend, "haar")

    def test_rejects_invalid_image(self):
        detector = FaceDetector("haar")
        with self.assertRaises(ValueError):
            detector.detect(np.empty((0, 0, 3), dtype=np.uint8))


class DetectionServiceTests(unittest.TestCase):
    def test_process_image_returns_prediction_counts(self):
        with tempfile.TemporaryDirectory() as directory:
            service = DetectionService(StubDetector(), StubClassifier(), Path(directory))
            image = np.zeros((40, 40, 3), dtype=np.uint8)

            result = service.process_image(
                image,
                source="camera",
                persist=False,
                include_base64=False,
            )

            self.assertEqual(result.total_faces, 1)
            self.assertEqual(result.mask_count, 1)
            self.assertEqual(result.no_mask_count, 0)
            self.assertEqual(result.compliance_percentage, 100.0)


if __name__ == "__main__":
    unittest.main()
