from dataclasses import dataclass
from pathlib import Path
from threading import Lock

import cv2
import numpy as np


@dataclass(frozen=True)
class FaceBox:
    x: int
    y: int
    width: int
    height: int


class FaceDetector:
    """OpenCV YuNet face detector with Haar Cascade as a local fallback."""

    def __init__(
        self,
        backend: str = "dnn",
        confidence_threshold: float = 0.5,
        model_path: Path | None = None,
    ) -> None:
        self.requested_backend = backend
        self.backend = backend
        self.confidence_threshold = confidence_threshold
        self.model_path = model_path
        self._lock = Lock()
        self._yunet = None

        cascade_path = Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"
        self._haar = cv2.CascadeClassifier(str(cascade_path))
        if self._haar.empty():
            raise RuntimeError(f"Failed to load Haar Cascade from {cascade_path}")

        if backend == "dnn":
            self._load_yunet()

    def detect(self, image: np.ndarray) -> list[FaceBox]:
        self._validate_image(image)

        if self._yunet is not None:
            faces = self._detect_yunet(image)
            if faces:
                return faces

        return self._detect_haar(image)

    def _load_yunet(self) -> None:
        if self.model_path is None or not self.model_path.exists():
            print(f"Warning: YuNet face detector model not found at {self.model_path}; using Haar Cascade.")
            self.backend = "haar"
            return

        try:
            self._yunet = cv2.FaceDetectorYN.create(
                str(self.model_path),
                "",
                (320, 320),
                self.confidence_threshold,
                0.3,
                5000,
            )
        except (AttributeError, cv2.error) as exc:
            print(f"Warning: could not load YuNet face detector from {self.model_path}: {exc}")
            self.backend = "haar"

    def _detect_haar(self, image: np.ndarray) -> list[FaceBox]:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self._haar.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(40, 40),
            flags=cv2.CASCADE_SCALE_IMAGE,
        )
        return [FaceBox(int(x), int(y), int(w), int(h)) for (x, y, w, h) in faces]

    def _detect_yunet(self, image: np.ndarray) -> list[FaceBox]:
        resized, scale = self._resize_for_detection(image)
        input_size = (resized.shape[1], resized.shape[0])

        with self._lock:
            self._yunet.setInputSize(input_size)
            _, detections = self._yunet.detect(resized)

        if detections is None:
            return []

        height, width = image.shape[:2]
        boxes: list[FaceBox] = []
        for detection in detections:
            score = float(detection[-1])
            if score < self.confidence_threshold:
                continue

            x, y, box_width, box_height = detection[:4] / scale
            x1 = max(0, min(int(round(x)), width - 1))
            y1 = max(0, min(int(round(y)), height - 1))
            x2 = max(x1 + 1, min(int(round(x + box_width)), width))
            y2 = max(y1 + 1, min(int(round(y + box_height)), height))
            boxes.append(FaceBox(x=x1, y=y1, width=x2 - x1, height=y2 - y1))
        return boxes

    def _resize_for_detection(self, image: np.ndarray) -> tuple[np.ndarray, float]:
        height, width = image.shape[:2]
        largest_dimension = max(height, width)

        if largest_dimension < 320:
            scale = 320 / largest_dimension
        elif largest_dimension > 1280:
            scale = 1280 / largest_dimension
        else:
            return image, 1.0

        resized = cv2.resize(
            image,
            (max(1, int(round(width * scale))), max(1, int(round(height * scale)))),
            interpolation=cv2.INTER_CUBIC if scale > 1 else cv2.INTER_AREA,
        )
        return resized, scale

    @staticmethod
    def _validate_image(image: np.ndarray) -> None:
        if not isinstance(image, np.ndarray) or image.ndim != 3 or image.shape[2] != 3 or image.size == 0:
            raise ValueError("Face detection requires a non-empty BGR image.")
