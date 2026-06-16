# AI-Powered Face Mask Detection System

Complete production-ready face mask detection project using **Python**, **FastAPI**, **TensorFlow/Keras**, **OpenCV**, **React**, **Tailwind CSS**, **SQLite**, **Docker**, and **Nginx**.

The system detects whether each face in a live camera frame or uploaded image is:

- **Mask**
- **No Mask**
- **Incorrect Mask**

It annotates detected faces with bounding boxes, labels, confidence scores, stores detection history, and provides analytics, CSV export, and PDF report generation.

## Features

### Live Camera Detection

- Browser webcam access through React.
- Real-time frame capture and FastAPI processing.
- OpenCV face detection.
- Keras/TensorFlow mask classification.
- Annotated frame rendering with labels and confidence scores.
- Optional persistence of camera detections.
- Screenshot capture from live camera.

### Image Upload Detection

- Upload JPG, JPEG, and PNG images.
- Detect all faces in the uploaded image.
- Predict mask status for every face.
- Return processed image with bounding boxes and labels.

### Analytics Dashboard

- Total faces detected.
- Mask count.
- No mask count.
- Incorrect mask count.
- Compliance percentage.
- Detection history table.
- CSV export.
- PDF report download.

### AI/ML Pipeline

- MobileNetV2 transfer learning.
- Data augmentation.
- Early stopping.
- Model checkpointing.
- Accuracy/loss graphs.
- Accuracy, precision, recall, F1 score.
- Confusion matrix.
- ROC curve.

### Deployment

- Dockerized backend and frontend.
- Nginx SPA hosting and `/api` reverse proxy.
- Vercel-ready frontend configuration.
- Environment variable configuration.
- SQLite persistence volumes.

## Project Structure

```text
face-mask-detection/
├── backend/
│   ├── app.py
│   ├── model/
│   │   └── labels.json
│   ├── services/
│   │   ├── config.py
│   │   ├── detection_service.py
│   │   ├── face_detector.py
│   │   ├── image_utils.py
│   │   ├── mask_classifier.py
│   │   ├── report_service.py
│   │   └── schemas.py
│   ├── database/
│   │   ├── crud.py
│   │   ├── models.py
│   │   └── session.py
│   ├── uploads/
│   ├── reports/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── training/
│   ├── train.py
│   ├── evaluate.py
│   └── dataset/
├── docs/
│   ├── API.md
│   ├── DIAGRAMS.md
│   ├── INSTALLATION.md
│   ├── USER_MANUAL.md
│   └── VERCEL_DEPLOYMENT.md
├── scripts/
│   └── verify.sh
├── BUILD.md
├── docker-compose.yml
├── vercel.json
├── .env.example
└── README.md
```

## Quick Start with Docker

```bash
cp .env.example .env
docker compose up --build
```

Open:

- Frontend: <http://localhost>
- Backend API: <http://localhost:8000>
- FastAPI docs: <http://localhost:8000/docs>

## Build and Test

For the complete build, test, Docker, Vercel, training, and troubleshooting guide, see [BUILD.md](BUILD.md).

Quick verification:

```bash
./scripts/verify.sh
```

Manual core checks:

```bash
python3 -m compileall backend training
python3 -m json.tool vercel.json >/dev/null
cd frontend && npm ci && npm run lint && npm run build
docker compose config
```

## Vercel Deployment

The frontend and FastAPI backend deploy together from the repository root. The
production setup uses Neon PostgreSQL for history and Vercel Blob for annotated
images. The browser calls the backend through the same-origin `/api` path.

```bash
npx vercel link
npx vercel blob create-store face-mask-detection-images --access public --yes
npx vercel integration add neon --plan free_v3
npx vercel deploy --prod
```

See [docs/VERCEL_DEPLOYMENT.md](docs/VERCEL_DEPLOYMENT.md) for dashboard and CLI deployment steps.

## Local Development

### Backend

```bash
cd backend
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Open <http://localhost:5173>.

## Train the Model

Place the dataset in `training/dataset/`:

```text
dataset/
  Mask/
  No Mask/
  Incorrect Mask/
```

Run:

```bash
cd training
pip install -r requirements.txt
python train.py --dataset dataset --epochs 30
python evaluate.py --dataset dataset
```

Training outputs:

- `backend/model/mask_detector.h5`
- `backend/model/mask_detector.onnx` after running `python export_onnx.py`
- `backend/model/labels.json`
- `training/artifacts/accuracy.png`
- `training/artifacts/loss.png`
- `training/artifacts/confusion_matrix.png`
- `training/artifacts/roc_curve.png`
- `training/artifacts/metrics.json`

Production inference uses `backend/model/mask_detector.onnx` through OpenCV DNN.
If the model is missing, the backend uses a deterministic fallback classifier.

## Backend API

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/health` | Health check and model status |
| `POST` | `/predict-image` | Upload image detection |
| `POST` | `/predict-camera-frame` | Base64 camera frame detection |
| `GET` | `/history` | Detection history |
| `GET` | `/statistics` | Aggregated analytics |
| `GET` | `/analytics.csv` | CSV export |
| `GET` | `/reports/pdf` | PDF report |

See [docs/API.md](docs/API.md) for request and response examples.

## Documentation

- [Installation Guide](docs/INSTALLATION.md)
- [User Manual](docs/USER_MANUAL.md)
- [API Documentation](docs/API.md)
- [Architecture, Use Case, Class, Sequence, and ER Diagrams](docs/DIAGRAMS.md)
- [Vercel Deployment Guide](docs/VERCEL_DEPLOYMENT.md)
- [Build, Test, and Deployment Guide](BUILD.md)

## Tech Stack

| Layer | Technologies |
| --- | --- |
| Frontend | React, Tailwind CSS, Axios, Vite |
| Backend | FastAPI, Python, OpenCV, SQLAlchemy |
| AI/ML | TensorFlow, Keras, MobileNetV2 |
| Database | SQLite |
| Deployment | Docker, Docker Compose, Nginx, Vercel frontend hosting |

## Environment Variables

Copy `.env.example` to `.env` and adjust values as needed.

Important variables:

- `DATABASE_URL`
- `MODEL_PATH`
- `LABELS_PATH`
- `FACE_DETECTOR_BACKEND`
- `UPLOAD_DIR`
- `REPORT_DIR`
- `FRONTEND_ORIGINS`
- `VITE_API_BASE_URL`

## Production Notes

- Use a representative and balanced dataset for reliable classification.
- Review consent/privacy requirements before storing face-related images.
- Put Nginx or a cloud load balancer behind HTTPS in public deployments.
- Backup the SQLite database and uploaded annotated images if they are operational records.
