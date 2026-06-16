import base64
import mimetypes
import os
from pathlib import Path
from uuid import uuid4

import cv2
import numpy as np


def decode_image_bytes(file_bytes: bytes) -> np.ndarray:
    buffer = np.frombuffer(file_bytes, np.uint8)
    image = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Unable to decode image. Please upload a valid JPG, JPEG, or PNG file.")
    return image


def decode_base64_image(payload: str) -> np.ndarray:
    if "," in payload:
        payload = payload.split(",", 1)[1]
    return decode_image_bytes(base64.b64decode(payload))


def encode_image_base64(image: np.ndarray, extension: str = ".jpg") -> str:
    success, buffer = cv2.imencode(extension, image)
    if not success:
        raise ValueError("Unable to encode annotated image.")
    mime = mimetypes.types_map.get(extension, "image/jpeg")
    encoded = base64.b64encode(buffer).decode("utf-8")
    return f"data:{mime};base64,{encoded}"


def save_image(image: np.ndarray, directory: Path, prefix: str = "detection", extension: str = ".jpg") -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    file_path = directory / f"{prefix}_{uuid4().hex}{extension}"
    cv2.imwrite(str(file_path), image)
    return file_path


def persist_annotated_image(image: np.ndarray, directory: Path, prefix: str) -> str:
    filename = f"{prefix}_{uuid4().hex}.jpg"
    if os.getenv("BLOB_READ_WRITE_TOKEN"):
        success, buffer = cv2.imencode(".jpg", image)
        if not success:
            raise ValueError("Unable to encode annotated image for storage.")

        from vercel.blob import BlobClient

        blob = BlobClient().put(
            f"detections/{filename}",
            buffer.tobytes(),
            access="public",
            content_type="image/jpeg",
        )
        return blob.url

    file_path = save_image(image, directory, prefix=prefix)
    return f"/uploads/{file_path.name}"
