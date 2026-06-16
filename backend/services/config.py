import os
import tempfile
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parent.parent
RUNTIME_DIR = Path(tempfile.gettempdir()) if os.getenv("VERCEL") else BACKEND_DIR


class Settings(BaseSettings):
    app_name: str = "Face Mask Detection API"
    app_env: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    frontend_origins: str = "http://localhost:5173,http://localhost:3000"

    database_url: str = f"sqlite:///{(BACKEND_DIR / 'database' / 'mask_detection.db').as_posix()}"
    model_path: Path = BACKEND_DIR / "model" / "mask_detector.onnx"
    labels_path: Path = BACKEND_DIR / "model" / "labels.json"
    face_detector_backend: str = Field(default="dnn", pattern="^(haar|dnn)$")
    face_detector_model_path: Path = BACKEND_DIR / "model" / "face_detection_yunet_2023mar.onnx"
    confidence_threshold: float = 0.5
    upload_dir: Path = RUNTIME_DIR / "uploads"
    report_dir: Path = RUNTIME_DIR / "reports"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.frontend_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    settings.report_dir.mkdir(parents=True, exist_ok=True)
    settings.model_path.parent.mkdir(parents=True, exist_ok=True)
    settings.face_detector_model_path.parent.mkdir(parents=True, exist_ok=True)

    if settings.database_url.startswith("sqlite:///"):
        database_path = Path(settings.database_url.replace("sqlite:///", "", 1))
        database_path.parent.mkdir(parents=True, exist_ok=True)

    return settings
