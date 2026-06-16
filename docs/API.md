# API Documentation

Base URL:

- Local backend: `http://localhost:8000`
- Docker frontend proxy: `/api`

FastAPI also exposes interactive documentation at `/docs` and OpenAPI JSON at `/openapi.json`.

## `GET /health`

Returns service status, configured detector backend, and whether a trained Keras model is loaded.

```json
{
  "status": "ok",
  "app": "Face Mask Detection API",
  "environment": "development",
  "model_loaded": true,
  "model_status": "trained",
  "face_detector": "dnn"
}
```

## `POST /predict-image`

Uploads a JPG, JPEG, or PNG image and returns detections plus a URL to the annotated image.

Request: `multipart/form-data`

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `file` | file | yes | Image to analyze |

## `POST /predict-camera-frame`

Processes one browser camera frame.

```json
{
  "image_base64": "data:image/jpeg;base64,...",
  "persist": false
}
```

## Prediction response

```json
{
  "total_faces": 2,
  "mask_count": 1,
  "no_mask_count": 1,
  "incorrect_mask_count": 0,
  "compliance_percentage": 50,
  "predictions": [
    {
      "label": "Mask",
      "confidence": 0.9842,
      "box": { "x": 120, "y": 80, "width": 140, "height": 140 }
    }
  ],
  "annotated_image_url": "/uploads/upload_abc.jpg",
  "annotated_image_base64": "data:image/jpeg;base64,..."
}
```

## `GET /history`

Query parameters:

- `limit` default `100`, max `500`
- `offset` default `0`

Returns persisted detection rows.

## `GET /statistics`

Optional query:

- `hours`: restrict statistics to the last N hours.

Returns total faces, counts by class, and compliance percentage.

## `GET /analytics.csv`

Downloads detection history as CSV.

## `GET /reports/pdf`

Generates and downloads a PDF report containing summary statistics and recent history rows.
