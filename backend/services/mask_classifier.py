import json
from pathlib import Path
from threading import Lock

import cv2
import numpy as np


DEFAULT_LABELS = ["Incorrect Mask", "Mask", "No Mask"]


class MaskClassifier:
    """Keras mask classifier with a deterministic fallback before a model is trained."""

    def __init__(self, model_path: Path, labels_path: Path, image_size: int = 224) -> None:
        self.model_path = model_path
        self.labels_path = labels_path
        self.image_size = image_size
        self.load_error: str | None = None
        self.model_runtime = "fallback"
        self._predict_lock = Lock()
        self.labels = self._load_labels(labels_path)
        self.model = self._load_model(model_path)
        self._validate_model_contract()

    @property
    def is_model_loaded(self) -> bool:
        return self.model is not None

    def predict(self, face_bgr: np.ndarray) -> tuple[str, float]:
        if not isinstance(face_bgr, np.ndarray) or face_bgr.size == 0:
            raise ValueError("Mask classification requires a non-empty face image.")

        if self.model is None:
            return self._fallback_predict(face_bgr)

        face_rgb = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2RGB)
        resized = cv2.resize(face_rgb, (self.image_size, self.image_size))
        batch = resized.astype("float32")

        input_batch = np.expand_dims(batch, axis=0)
        with self._predict_lock:
            if self.model_runtime == "onnx":
                self.model.setInput(input_batch)
                predictions = np.asarray(self.model.forward()).reshape(-1)
            else:
                predictions = np.asarray(self.model.predict(input_batch, verbose=0))[0]

        if predictions.ndim != 1 or not np.all(np.isfinite(predictions)):
            raise RuntimeError("Mask model returned an invalid prediction.")

        class_index = int(np.argmax(predictions))
        confidence = float(predictions[class_index])
        label = self.labels[class_index]
        return label, round(confidence, 4)

    def _load_model(self, model_path: Path):
        if not model_path.exists():
            return None

        if model_path.suffix.lower() == ".onnx":
            try:
                model = cv2.dnn.readNetFromONNX(str(model_path))
                self.model_runtime = "onnx"
                return model
            except cv2.error as exc:
                self.load_error = str(exc)
                print(f"Warning: could not load ONNX mask model from {model_path}: {exc}")
                return None

        try:
            from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
            from tensorflow.keras.models import load_model

            model = load_model(
                model_path,
                custom_objects={"preprocess_input": preprocess_input},
                compile=False,
            )
            self.model_runtime = "keras"
            return model
        except Exception as exc:
            self.load_error = str(exc)
            print(f"Warning: could not load mask model from {model_path}: {exc}")
            return None

    def _load_labels(self, labels_path: Path) -> list[str]:
        if labels_path.exists():
            with labels_path.open("r", encoding="utf-8") as label_file:
                labels = json.load(label_file)
            if isinstance(labels, dict):
                return [labels[str(index)] for index in range(len(labels))]
            if isinstance(labels, list) and labels and all(isinstance(label, str) for label in labels):
                return labels
        return DEFAULT_LABELS

    def _validate_model_contract(self) -> None:
        if self.model is None or self.model_runtime == "onnx":
            return

        output_shape = self.model.output_shape
        class_count = output_shape[-1] if isinstance(output_shape, tuple) else None
        if class_count != len(self.labels):
            self.load_error = (
                f"Model outputs {class_count} classes but labels.json contains {len(self.labels)} labels."
            )
            print(f"Warning: {self.load_error} Using fallback classifier.")
            self.model = None
            self.model_runtime = "fallback"

    def _fallback_predict(self, face_bgr: np.ndarray) -> tuple[str, float]:
        """Lightweight heuristic keeps demos functional until training produces a model."""
        height = face_bgr.shape[0]
        lower_face = face_bgr[int(height * 0.45) :, :]
        hsv = cv2.cvtColor(lower_face, cv2.COLOR_BGR2HSV)
        saturation = hsv[:, :, 1]
        value = hsv[:, :, 2]

        covered_ratio = float(np.mean((saturation > 35) & (value > 45)))
        edge_density = float(np.mean(cv2.Canny(cv2.cvtColor(lower_face, cv2.COLOR_BGR2GRAY), 80, 160) > 0))

        if covered_ratio > 0.42 and edge_density < 0.18:
            return "Mask", round(min(0.88, 0.58 + covered_ratio * 0.45), 4)
        if 0.28 < covered_ratio <= 0.42:
            return "Incorrect Mask", round(0.55 + covered_ratio * 0.4, 4)
        return "No Mask", round(min(0.9, 0.62 + (0.28 - covered_ratio) * 0.7), 4)
