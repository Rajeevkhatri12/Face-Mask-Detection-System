from pathlib import Path

import cv2
import numpy as np
from sqlalchemy.orm import Session

from database import crud
from .face_detector import FaceBox, FaceDetector
from .image_utils import encode_image_base64, persist_annotated_image
from .mask_classifier import MaskClassifier
from .schemas import BoundingBox, FacePrediction, PredictionResponse


LABEL_COLORS = {
    "Mask": (46, 204, 113),
    "No Mask": (231, 76, 60),
    "Incorrect Mask": (241, 196, 15),
}


class DetectionService:
    def __init__(self, detector: FaceDetector, classifier: MaskClassifier, upload_dir: Path) -> None:
        self.detector = detector
        self.classifier = classifier
        self.upload_dir = upload_dir

    def process_image(
        self,
        image: np.ndarray,
        source: str,
        db: Session | None = None,
        persist: bool = True,
        include_base64: bool = False,
    ) -> PredictionResponse:
        annotated = image.copy()
        faces = self.detector.detect(image)
        predictions: list[FacePrediction] = []

        for face in faces:
            crop = self._crop_face(image, face)
            label, confidence = self.classifier.predict(crop)
            prediction = FacePrediction(
                label=label,
                confidence=confidence,
                box=BoundingBox(x=face.x, y=face.y, width=face.width, height=face.height),
            )
            predictions.append(prediction)
            self._draw_annotation(annotated, face, label, confidence)

        annotated_url = None
        if persist or source == "upload":
            annotated_url = persist_annotated_image(annotated, self.upload_dir, prefix=source)

        if persist and db is not None and predictions:
            image_path = annotated_url or ""
            crud.create_detection_records(
                db,
                [
                    {
                        "source": source,
                        "result": prediction.label,
                        "confidence": prediction.confidence,
                        "image_path": image_path,
                        "face_x": prediction.box.x,
                        "face_y": prediction.box.y,
                        "face_width": prediction.box.width,
                        "face_height": prediction.box.height,
                    }
                    for prediction in predictions
                ],
            )

        return PredictionResponse(
            total_faces=len(predictions),
            mask_count=sum(1 for item in predictions if item.label == "Mask"),
            no_mask_count=sum(1 for item in predictions if item.label == "No Mask"),
            incorrect_mask_count=sum(1 for item in predictions if item.label == "Incorrect Mask"),
            compliance_percentage=self._compliance(predictions),
            predictions=predictions,
            annotated_image_url=annotated_url,
            annotated_image_base64=encode_image_base64(annotated) if include_base64 else None,
        )

    def _crop_face(self, image: np.ndarray, face: FaceBox) -> np.ndarray:
        height, width = image.shape[:2]
        x1 = max(face.x, 0)
        y1 = max(face.y, 0)
        x2 = min(face.x + face.width, width)
        y2 = min(face.y + face.height, height)
        return image[y1:y2, x1:x2]

    def _draw_annotation(self, image: np.ndarray, face: FaceBox, label: str, confidence: float) -> None:
        color = LABEL_COLORS.get(label, (52, 152, 219))
        x1, y1 = face.x, face.y
        x2, y2 = face.x + face.width, face.y + face.height
        text = f"{label}: {confidence * 100:.1f}%"

        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        text_y = max(y1 - 10, 20)
        (text_width, text_height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.rectangle(image, (x1, text_y - text_height - 8), (x1 + text_width + 8, text_y + 4), color, -1)
        cv2.putText(image, text, (x1 + 4, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    def _compliance(self, predictions: list[FacePrediction]) -> float:
        if not predictions:
            return 0.0
        return round((sum(1 for item in predictions if item.label == "Mask") / len(predictions)) * 100, 2)
