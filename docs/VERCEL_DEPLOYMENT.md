# Vercel Deployment Guide

The repository deploys as one Vercel project:

```text
Vite frontend -> /api FastAPI function -> Neon PostgreSQL
                                      -> Vercel Blob
```

Production inference uses `backend/model/mask_detector.onnx` through OpenCV
DNN. TensorFlow remains a training dependency and is not included in the
serverless function.

## Required resources

1. A Vercel project linked to the repository root.
2. A public Vercel Blob store for annotated images.
3. A Neon PostgreSQL resource for detection history and analytics.

## CLI deployment

```bash
npx vercel link
npx vercel blob create-store face-mask-detection-images \
  --access public --yes \
  --environment production --environment preview --environment development
npx vercel integration add neon --plan free_v3
npx vercel deploy --prod
```

Vercel and the integrations provide `BLOB_READ_WRITE_TOKEN` and
`DATABASE_URL`. Set these project variables as well:

```text
APP_ENV=production
FRONTEND_ORIGINS=https://your-project.vercel.app
```

The production frontend defaults to `VITE_API_BASE_URL=/api`, so a separate
backend URL is not required.

## Verification

```bash
curl https://your-project.vercel.app/api/health
curl https://your-project.vercel.app/api/statistics
```

Also verify image upload, live camera detection, dashboard history, CSV export,
PDF report download, and that annotated image URLs use Vercel Blob.

## Retraining

After training the Keras model, export it before deployment:

```bash
cd training
python export_onnx.py
```

Commit or include `backend/model/mask_detector.onnx` in the next deployment.
