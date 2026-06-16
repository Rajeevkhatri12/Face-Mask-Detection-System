# Build, Test, and Deployment README

This guide explains how to build, test, and deploy the complete Face Mask Detection System.

## 1. What gets built

| Component | Path | Build output |
| --- | --- | --- |
| FastAPI backend | `backend/` | Python API service on port `8000` |
| React frontend | `frontend/` | Static production files in `frontend/dist/` |
| ML training pipeline | `training/` | Keras model and evaluation artifacts |
| Docker deployment | repository root | Backend and frontend containers |
| Vercel deployment | repository root | Frontend hosted from `frontend/dist/` |

## 2. Prerequisites

- Python 3.11 or newer
- Node.js 22 or newer
- npm 10 or newer
- Docker and Docker Compose for container builds
- Optional: Vercel account/token for live Vercel deployment
- Optional: Face mask dataset for training

Check versions:

```bash
python3 --version
node --version
npm --version
docker --version
docker compose version
```

## 3. Environment setup

Create the root environment file:

```bash
cp .env.example .env
```

For local frontend development:

```bash
cd frontend
cp .env.example .env
```

For Vercel production, set this in Vercel Project Settings:

```text
VITE_API_BASE_URL=https://your-fastapi-backend.example.com
```

## 4. Build backend locally

```bash
cd backend
cp .env.example .env
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Open:

- API health: `http://localhost:8000/health`
- API docs: `http://localhost:8000/docs`

Backend outputs:

- SQLite database: `backend/database/mask_detection.db`
- Uploaded/annotated images: `backend/uploads/`
- PDF reports: `backend/reports/`

## 5. Build frontend locally

```bash
cd frontend
npm ci
npm run lint
npm run build
npm run preview
```

Open `http://localhost:4173`.

For development:

```bash
npm run dev
```

Open `http://localhost:5173`.

## 6. Build the full app with Docker

```bash
cp .env.example .env
docker compose build
docker compose up
```

Open:

- Frontend: `http://localhost`
- Backend: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`

Health check:

```bash
curl http://localhost:8000/health
```

Stop containers:

```bash
docker compose down
```

Reset persistent Docker volumes:

```bash
docker compose down -v
```

## 7. Build for Vercel

The repository includes `vercel.json`, so Vercel can build from the repository root.

Expected Vercel build commands:

```bash
cd frontend && npm ci
cd frontend && npm run build
```

Output directory:

```text
frontend/dist
```

Deploy with the Vercel dashboard:

1. Import the GitHub repository and keep the repository root as the project root.
2. Connect a public Vercel Blob store.
3. Connect a Neon PostgreSQL database.
4. Deploy. The frontend calls the FastAPI function through `/api`.

Deploy with CLI if a token is available:

```bash
npx vercel deploy --prod --token "$VERCEL_TOKEN"
```

The production API uses the ONNX classifier through OpenCV DNN, Neon for
persistent analytics, and Vercel Blob for annotated images.

## 8. Train and build the ML model

Place the dataset in `training/dataset/`:

```text
training/dataset/
  Mask/
  No Mask/
  Incorrect Mask/
```

Install training dependencies:

```bash
cd training
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Train:

```bash
python train.py --dataset dataset --epochs 30
```

Evaluate:

```bash
python evaluate.py --dataset dataset
```

Generated model and artifacts:

- `backend/model/mask_detector.h5`
- `backend/model/mask_detector.onnx` after `python export_onnx.py`
- `backend/model/labels.json`
- `training/artifacts/accuracy.png`
- `training/artifacts/loss.png`
- `training/artifacts/confusion_matrix.png`
- `training/artifacts/roc_curve.png`
- `training/artifacts/metrics.json`

Restart the backend after replacing the model.

## 9. Test and verification commands

Run the lightweight project verification script:

```bash
./scripts/verify.sh
```

This runs:

- Python syntax compilation for `backend/` and `training/`
- `vercel.json` validation
- Docker Compose config validation when Docker is available
- `npm ci`
- frontend lint
- frontend production build

Run commands manually:

```bash
python3 -m compileall backend training
python3 -m json.tool vercel.json >/dev/null
cd frontend && npm ci && npm run lint && npm run build
docker compose config
```

Backend runtime smoke test after starting the backend:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/statistics
```

Frontend manual smoke test:

1. Open the frontend.
2. Visit Home, Live Detection, Upload Image, Dashboard, and About.
3. Upload a JPG/PNG image.
4. Confirm the backend returns predictions and an annotated image.
5. Confirm Dashboard refresh, CSV export, and PDF report download.

## 10. Production checklist

- Train the model and export `mask_detector.onnx` into `backend/model/`.
- Set `FRONTEND_ORIGINS` to the deployed frontend URL.
- Connect Neon PostgreSQL and a public Vercel Blob store.
- Keep `VITE_API_BASE_URL=/api` for the combined Vercel deployment.
- Review privacy/consent rules before storing face images.
- Back up SQLite and uploaded annotated images if they are operational records.

## 11. Troubleshooting

### Frontend cannot reach backend

Check `VITE_API_BASE_URL` and CORS:

```text
VITE_API_BASE_URL=https://your-backend-domain.com
FRONTEND_ORIGINS=https://your-frontend-domain.com
```

### Backend starts but model is not loaded

Check:

```bash
curl http://localhost:8000/health
```

If `model_loaded` is `false`, train or copy the model to:

```text
backend/model/mask_detector.h5
```

The app still runs with a deterministic fallback classifier for demos and UI testing.

### Docker frontend cannot call backend

Use the Docker/Nginx setup or set:

```text
VITE_API_BASE_URL=/api
```

### TensorFlow install is slow

TensorFlow is large. Use Docker for backend deployment or install backend dependencies in a dedicated virtual environment.
