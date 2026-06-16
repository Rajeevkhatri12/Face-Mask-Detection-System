import csv
from io import StringIO
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy.orm import Session

from database import crud


class ReportService:
    def __init__(self, report_dir: Path) -> None:
        self.report_dir = report_dir
        self.report_dir.mkdir(parents=True, exist_ok=True)

    def build_pdf_report(self, db: Session) -> Path:
        records = crud.list_detection_records(db, limit=500)
        stats = crud.get_detection_statistics(db)
        output = self.report_dir / "face_mask_detection_report.pdf"

        doc = SimpleDocTemplate(str(output), pagesize=A4)
        styles = getSampleStyleSheet()
        story = [
            Paragraph("Face Mask Detection Report", styles["Title"]),
            Spacer(1, 12),
            Paragraph(
                f"Total faces: {stats['total_faces']} | Mask: {stats['mask_count']} | "
                f"No Mask: {stats['no_mask_count']} | Incorrect: {stats['incorrect_mask_count']} | "
                f"Compliance: {stats['compliance_percentage']}%",
                styles["Normal"],
            ),
            Spacer(1, 16),
        ]

        rows = [["Timestamp", "Source", "Result", "Confidence", "Image"]]
        rows.extend(
            [
                record.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                record.source,
                record.result,
                f"{record.confidence:.2%}",
                record.image_path or "-",
            ]
            for record in records
        )

        table = Table(rows, repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f4f6")]),
                ]
            )
        )
        story.append(table)
        doc.build(story)
        return output

    def build_csv_text(self, db: Session) -> str:
        records = crud.list_detection_records(db, limit=5000)
        buffer = StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["id", "timestamp", "source", "result", "confidence", "image_path", "face_x", "face_y", "face_width", "face_height"])
        for record in records:
            writer.writerow(
                [
                    record.id,
                    record.timestamp.isoformat(),
                    record.source,
                    record.result,
                    f"{record.confidence:.4f}",
                    record.image_path or "",
                    record.face_x or "",
                    record.face_y or "",
                    record.face_width or "",
                    record.face_height or "",
                ]
            )
        return buffer.getvalue()
