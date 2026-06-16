from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String

from .session import Base


class DetectionRecord(Base):
    __tablename__ = "detection_records"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    source = Column(String(32), nullable=False, default="upload")
    result = Column(String(32), nullable=False, index=True)
    confidence = Column(Float, nullable=False)
    image_path = Column(String(512), nullable=True)
    face_x = Column(Integer, nullable=True)
    face_y = Column(Integer, nullable=True)
    face_width = Column(Integer, nullable=True)
    face_height = Column(Integer, nullable=True)
