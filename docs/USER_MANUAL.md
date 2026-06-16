# User Manual

## Home

The home page introduces the system and links to live detection and image upload workflows.

## Live Detection

1. Open **Live Detection**.
2. Click **Start Camera** and allow browser camera access.
3. The browser sends frames to the backend every 1.5 seconds.
4. Annotated frames show bounding boxes, labels, and confidence scores.
5. Enable **Save camera detections** to store live results in SQLite.
6. Click **Capture Screenshot** to download the current annotated frame.

## Upload Image

1. Open **Upload Image**.
2. Select a JPG, JPEG, or PNG file.
3. Click **Run Detection**.
4. View the processed image with annotations and per-face predictions.

## Analytics Dashboard

The dashboard displays:

- Total faces detected
- Mask count
- No mask count
- Incorrect mask count
- Compliance percentage
- Detection history table

Actions:

- **Refresh** reloads statistics and history.
- **Export CSV** downloads raw analytics.
- **Download PDF** generates a printable report.

## About Project

The about page summarizes the AI, backend, frontend, and deployment architecture.

## Notes

- If `backend/model/mask_detector.h5` is missing, the backend runs a deterministic fallback classifier so the interface remains testable.
- For real production accuracy, train with a balanced dataset and deploy the generated model file.
