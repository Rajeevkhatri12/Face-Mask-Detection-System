# Installation Guide

## Prerequisites

- Python 3.11+
- Node.js 22+
- Docker and Docker Compose for container deployment
- A face mask dataset with class folders such as `Mask`, `No Mask`, and `Incorrect Mask`

## Backend setup

```bash
cd backend
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000/docs` for the API console.

## Frontend setup

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Open `http://localhost:5173`.

## Train the AI model

```bash
cd training
pip install -r requirements.txt
python train.py --dataset dataset --epochs 30
python evaluate.py --dataset dataset
```

The trained model is saved to `backend/model/mask_detector.h5`. Run
`python export_onnx.py` to create the production
`backend/model/mask_detector.onnx`, then restart the backend.

## Docker deployment

```bash
cp .env.example .env
docker compose up --build
```

Services:

- Frontend: `http://localhost`
- Backend: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`

## Build and test verification

From the repository root:

```bash
./scripts/verify.sh
```

The script validates Python syntax, Vercel JSON, Docker Compose config when Docker is available, frontend dependency installation, frontend linting, and frontend production build.

For detailed build instructions, see [`BUILD.md`](../BUILD.md).

## Environment variables

| Variable | Description |
| --- | --- |
| `DATABASE_URL` | SQLite locally or PostgreSQL in production |
| `MODEL_PATH` | ONNX classifier path |
| `LABELS_PATH` | Labels JSON path |
| `FACE_DETECTOR_BACKEND` | `dnn` for YuNet, with automatic Haar fallback |
| `FACE_DETECTOR_MODEL_PATH` | Path to the YuNet ONNX face detector |
| `CONFIDENCE_THRESHOLD` | Detector/classifier threshold |
| `UPLOAD_DIR` | Annotated image output directory |
| `REPORT_DIR` | PDF report output directory |
| `FRONTEND_ORIGINS` | Comma-separated CORS origins |
| `VITE_API_BASE_URL` | Frontend API base URL |
