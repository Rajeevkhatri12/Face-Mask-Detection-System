# Model Training

Place the face mask dataset in `training/dataset/` with one folder per class, for example:

```text
dataset/
  Mask/
  No Mask/
  Incorrect Mask/
```

Train the MobileNetV2 transfer-learning classifier:

```bash
cd training
pip install -r requirements.txt
python train.py --dataset dataset --epochs 30
python evaluate.py --dataset dataset
```

Generated artifacts:

- `backend/model/mask_detector.h5`
- `backend/model/labels.json`
- `training/artifacts/accuracy.png`
- `training/artifacts/loss.png`
- `training/artifacts/confusion_matrix.png`
- `training/artifacts/roc_curve.png`
- `training/artifacts/metrics.json`
