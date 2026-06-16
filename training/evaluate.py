import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import tensorflow as tf
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_curve,
    auc,
)
from sklearn.preprocessing import label_binarize


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate trained face mask classifier.")
    parser.add_argument("--dataset", default="dataset", help="Evaluation dataset with class subfolders.")
    parser.add_argument("--model", default="../backend/model/mask_detector.h5")
    parser.add_argument("--labels", default="../backend/model/labels.json")
    parser.add_argument("--output-dir", default="artifacts")
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--image-size", type=int, default=224)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    dataset = tf.keras.utils.image_dataset_from_directory(
        args.dataset,
        shuffle=False,
        image_size=(args.image_size, args.image_size),
        batch_size=args.batch_size,
    )
    class_names = load_labels(Path(args.labels), dataset.class_names)

    model = tf.keras.models.load_model(args.model)
    probabilities = model.predict(dataset, verbose=1)
    y_pred = np.argmax(probabilities, axis=1)
    y_true = np.concatenate([labels.numpy() for _, labels in dataset])

    metrics = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision_macro": float(precision_score(y_true, y_pred, average="macro", zero_division=0)),
        "recall_macro": float(recall_score(y_true, y_pred, average="macro", zero_division=0)),
        "f1_macro": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "classification_report": classification_report(y_true, y_pred, target_names=class_names, zero_division=0, output_dict=True),
    }

    with (output_dir / "metrics.json").open("w", encoding="utf-8") as metrics_file:
        json.dump(metrics, metrics_file, indent=2)

    plot_confusion_matrix(y_true, y_pred, class_names, output_dir / "confusion_matrix.png")
    plot_roc_curve(y_true, probabilities, class_names, output_dir / "roc_curve.png")
    print(json.dumps(metrics, indent=2))


def load_labels(path: Path, fallback: list[str]) -> list[str]:
    if not path.exists():
        return fallback
    with path.open("r", encoding="utf-8") as labels_file:
        labels = json.load(labels_file)
    return labels if isinstance(labels, list) else fallback


def plot_confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray, class_names: list[str], output_path: Path) -> None:
    matrix = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(matrix, annot=True, fmt="d", cmap="Greens", xticklabels=class_names, yticklabels=class_names)
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title("Confusion Matrix")
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()


def plot_roc_curve(y_true: np.ndarray, probabilities: np.ndarray, class_names: list[str], output_path: Path) -> None:
    y_bin = label_binarize(y_true, classes=list(range(len(class_names))))
    if y_bin.shape[1] == 1:
        y_bin = np.column_stack([1 - y_bin[:, 0], y_bin[:, 0]])

    plt.figure(figsize=(8, 6))
    for index, class_name in enumerate(class_names):
        if index >= probabilities.shape[1]:
            continue
        fpr, tpr, _ = roc_curve(y_bin[:, index], probabilities[:, index])
        roc_auc = auc(fpr, tpr)
        plt.plot(fpr, tpr, label=f"{class_name} (AUC={roc_auc:.3f})")

    plt.plot([0, 1], [0, 1], "k--", label="Random")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curve")
    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()


if __name__ == "__main__":
    main()
