from datetime import datetime

from pydantic import BaseModel, Field


class FramePayload(BaseModel):
    image_base64: str = Field(..., description="Base64 encoded image, optionally prefixed with a data URL header.")
    persist: bool = Field(default=False, description="Store frame detections and annotated image when true.")


class BoundingBox(BaseModel):
    x: int
    y: int
    width: int
    height: int


class FacePrediction(BaseModel):
    label: str
    confidence: float
    box: BoundingBox


class PredictionResponse(BaseModel):
    total_faces: int
    mask_count: int
    no_mask_count: int
    incorrect_mask_count: int
    compliance_percentage: float
    predictions: list[FacePrediction]
    annotated_image_url: str | None = None
    annotated_image_base64: str | None = None


class DetectionHistoryItem(BaseModel):
    id: int
    timestamp: datetime
    source: str
    result: str
    confidence: float
    image_path: str | None
    face_x: int | None
    face_y: int | None
    face_width: int | None
    face_height: int | None

    class Config:
        from_attributes = True


class StatisticsResponse(BaseModel):
    total_faces: int
    mask_count: int
    no_mask_count: int
    incorrect_mask_count: int
    compliance_percentage: float
