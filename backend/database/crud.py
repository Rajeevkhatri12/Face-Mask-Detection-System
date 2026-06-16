from datetime import datetime, timedelta
from typing import Iterable

from sqlalchemy import func
from sqlalchemy.orm import Session

from .models import DetectionRecord


def create_detection_records(db: Session, records: Iterable[dict]) -> list[DetectionRecord]:
    db_records = [DetectionRecord(**record) for record in records]
    db.add_all(db_records)
    db.commit()
    for record in db_records:
        db.refresh(record)
    return db_records


def list_detection_records(db: Session, limit: int = 100, offset: int = 0) -> list[DetectionRecord]:
    return (
        db.query(DetectionRecord)
        .order_by(DetectionRecord.timestamp.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def get_detection_statistics(db: Session, hours: int | None = None) -> dict:
    query = db.query(DetectionRecord)
    if hours:
        query = query.filter(DetectionRecord.timestamp >= datetime.utcnow() - timedelta(hours=hours))

    total = query.count()
    grouped = {
        result: count
        for result, count in query.with_entities(DetectionRecord.result, func.count(DetectionRecord.id)).group_by(DetectionRecord.result).all()
    }
    mask_count = grouped.get("Mask", 0)
    no_mask_count = grouped.get("No Mask", 0)
    incorrect_count = grouped.get("Incorrect Mask", 0)
    compliance = round((mask_count / total) * 100, 2) if total else 0.0

    return {
        "total_faces": total,
        "mask_count": mask_count,
        "no_mask_count": no_mask_count,
        "incorrect_mask_count": incorrect_count,
        "compliance_percentage": compliance,
    }
