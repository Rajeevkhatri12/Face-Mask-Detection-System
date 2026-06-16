"""
Download the Kaggle face-mask dataset and train the MobileNetV2 classifier.
Run from inside the training/ directory with the backend venv active:

    python download_and_train.py

Requires KAGGLE_USERNAME and KAGGLE_KEY env vars, or ~/.kaggle/kaggle.json.
"""

import json
import shutil
from pathlib import Path

import kagglehub

DATASET_SLUG = "shiekhburhan/face-mask-dataset"
TRAINING_DIR = Path(__file__).parent
DATASET_OUT = TRAINING_DIR / "dataset"
MODEL_OUT = TRAINING_DIR / "../backend/model/mask_detector.h5"
LABELS_OUT = TRAINING_DIR / "../backend/model/labels.json"

# Map any folder-name variants the Kaggle dataset might use -> canonical labels
LABEL_MAP = {
    "with_mask": "Mask",
    "withmask": "Mask",
    "mask": "Mask",
    "yes": "Mask",
    "without_mask": "No Mask",
    "withoutmask": "No Mask",
    "no_mask": "No Mask",
    "nomask": "No Mask",
    "no": "No Mask",
    "mask_weared_incorrect": "Incorrect Mask",
    "incorrect_mask": "Incorrect Mask",
    "incorrectmask": "Incorrect Mask",
    "incorrect": "Incorrect Mask",
}


def organise_dataset(raw_root: Path, out_dir: Path) -> list[str]:
    """Copy images from raw download into out_dir/<ClassName>/ layout.

    Handles multi-level structures like:
        with_mask/complex/img.jpg
        with_mask/simple/img.jpg
        incorrect_mask/mc/img.jpg
    by matching any ancestor directory name against LABEL_MAP.
    """
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    image_exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    copied: dict[str, int] = {}
    counters: dict[str, int] = {}

    # Find every directory whose name maps to a label, then grab all images inside it
    for path in sorted(raw_root.rglob("*")):
        if not path.is_dir():
            continue
        raw_name = path.name.lower().replace(" ", "_").replace("-", "_")
        label = LABEL_MAP.get(raw_name)
        if label is None:
            continue

        dest = out_dir / label
        dest.mkdir(exist_ok=True)
        count = 0
        for img in path.rglob("*"):
            if img.is_file() and img.suffix.lower() in image_exts:
                idx = counters.get(label, 0)
                counters[label] = idx + 1
                shutil.copy2(img, dest / f"{idx:06d}{img.suffix.lower()}")
                count += 1
        if count:
            print(f"  {str(path.relative_to(raw_root))!r} -> {label!r}: {count} images")
            copied[label] = copied.get(label, 0) + count

    print(f"\nDataset summary: {copied}")
    return sorted(copied.keys())


def main() -> None:
    print("=== Step 1: Downloading Kaggle dataset ===")
    raw_path = Path(kagglehub.dataset_download(DATASET_SLUG))
    print(f"Downloaded to: {raw_path}")

    print("\n=== Step 2: Organising into class folders ===")
    class_names = organise_dataset(raw_path, DATASET_OUT)
    if not class_names:
        raise RuntimeError(
            "No recognised class folders found. Check the raw dataset structure "
            f"at {raw_path} and update LABEL_MAP."
        )

    print(f"\nClasses: {class_names}")
    with open(LABELS_OUT, "w", encoding="utf-8") as f:
        json.dump(class_names, f, indent=2)
    print(f"Saved labels to {LABELS_OUT}")

    print("\n=== Step 3: Training MobileNetV2 classifier ===")
    import subprocess, sys
    result = subprocess.run(
        [
            sys.executable, "train.py",
            "--dataset", str(DATASET_OUT),
            "--output", str(MODEL_OUT),
            "--labels", str(LABELS_OUT),
            "--epochs", "20",
            "--batch-size", "32",
        ],
        cwd=TRAINING_DIR,
    )
    if result.returncode != 0:
        raise RuntimeError("Training failed — check output above.")

    print(f"\n=== Done! Model saved to {MODEL_OUT} ===")
    print("Restart the backend to load the trained model.")


if __name__ == "__main__":
    main()
