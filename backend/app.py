from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, Query, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from database import crud
from database.session import get_db, init_db
from services.config import get_settings
from services.detection_service import DetectionService
from services.face_detector import FaceDetector
from services.image_utils import decode_base64_image, decode_image_bytes
from services.mask_classifier import MaskClassifier
from services.report_service import ReportService
from services.schemas import (
    DetectionHistoryItem,
    FramePayload,
    PredictionResponse,
    StatisticsResponse,
)

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="AI-powered real-time face mask detection API using FastAPI, OpenCV, and TensorFlow/Keras.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

detector = FaceDetector(
    settings.face_detector_backend,
    settings.confidence_threshold,
    settings.face_detector_model_path,
)
classifier = MaskClassifier(settings.model_path, settings.labels_path)
detection_service = DetectionService(detector, classifier, settings.upload_dir)
report_service = ReportService(settings.report_dir)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.app_env,
        "model_loaded": classifier.is_model_loaded,
        "model_status": "trained" if classifier.is_model_loaded else "fallback",
        "model_runtime": classifier.model_runtime,
        "face_detector": detector.backend,
    }


@app.post("/predict-image", response_model=PredictionResponse)
async def predict_image(file: UploadFile = File(...), db: Session = Depends(get_db)) -> PredictionResponse:
    if not _is_allowed_image(file.filename):
        raise HTTPException(status_code=400, detail="Only JPG, JPEG, and PNG images are supported.")

    try:
        image = decode_image_bytes(await file.read())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return detection_service.process_image(image, source="upload", db=db, persist=True, include_base64=False)


@app.post("/predict-camera-frame", response_model=PredictionResponse)
async def predict_camera_frame(payload: FramePayload, db: Session = Depends(get_db)) -> PredictionResponse:
    try:
        image = decode_base64_image(payload.image_base64)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid base64 image payload.") from exc

    return detection_service.process_image(
        image,
        source="camera",
        db=db,
        persist=payload.persist,
        include_base64=True,
    )


@app.get("/history", response_model=list[DetectionHistoryItem])
def detection_history(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[DetectionHistoryItem]:
    return crud.list_detection_records(db, limit=limit, offset=offset)


@app.get("/statistics", response_model=StatisticsResponse)
def statistics(hours: int | None = Query(default=None, ge=1, le=8760), db: Session = Depends(get_db)) -> dict:
    return crud.get_detection_statistics(db, hours=hours)


@app.get("/reports/pdf")
def download_pdf_report(db: Session = Depends(get_db)) -> FileResponse:
    report_path = report_service.build_pdf_report(db)
    return FileResponse(path=report_path, filename=report_path.name, media_type="application/pdf")


@app.get("/analytics.csv")
def export_analytics_csv(db: Session = Depends(get_db)) -> Response:
    csv_text = report_service.build_csv_text(db)
    return Response(
        content=csv_text,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=face_mask_detection_analytics.csv"},
    )


def _is_allowed_image(filename: str | None) -> bool:
    if not filename:
        return False
    return Path(filename).suffix.lower() in {".jpg", ".jpeg", ".png"}


app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")
app.mount("/reports", StaticFiles(directory=settings.report_dir), name="reports")
