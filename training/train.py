import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras import layers
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train MobileNetV2 face mask classifier.")
    parser.add_argument("--dataset", default="dataset", help="Directory with class subfolders.")
    parser.add_argument("--output", default="../backend/model/mask_detector.h5", help="Output Keras model path.")
    parser.add_argument("--labels", default="../backend/model/labels.json", help="Output labels JSON path.")
    parser.add_argument("--plots-dir", default="artifacts", help="Directory for training plots.")
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--image-size", type=int, default=224)
    parser.add_argument("--validation-split", type=float, default=0.2)
    return parser.parse_args()


def build_model(image_size: int, num_classes: int) -> tf.keras.Model:
    inputs = layers.Input(shape=(image_size, image_size, 3))
    x = layers.RandomFlip("horizontal")(inputs)
    x = layers.RandomRotation(0.08)(x)
    x = layers.RandomZoom(0.12)(x)
    x = layers.RandomContrast(0.12)(x)
    x = layers.Lambda(preprocess_input, name="mobilenetv2_preprocess")(x)

    base_model = MobileNetV2(weights="imagenet", include_top=False, input_tensor=x)
    base_model.trainable = False

    x = layers.GlobalAveragePooling2D()(base_model.output)
    x = layers.Dropout(0.35)(x)
    x = layers.Dense(128, activation="relu")(x)
    x = layers.Dropout(0.25)(x)
    outputs = layers.Dense(num_classes, activation="softmax")(x)

    model = tf.keras.Model(inputs, outputs)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def load_datasets(args: argparse.Namespace):
    train_ds = tf.keras.utils.image_dataset_from_directory(
        args.dataset,
        validation_split=args.validation_split,
        subset="training",
        seed=42,
        image_size=(args.image_size, args.image_size),
        batch_size=args.batch_size,
    )
    val_ds = tf.keras.utils.image_dataset_from_directory(
        args.dataset,
        validation_split=args.validation_split,
        subset="validation",
        seed=42,
        image_size=(args.image_size, args.image_size),
        batch_size=args.batch_size,
    )

    autotune = tf.data.AUTOTUNE
    return (
        train_ds.cache().shuffle(1000).prefetch(autotune),
        val_ds.cache().prefetch(autotune),
        train_ds.class_names,
    )


def plot_history(history: tf.keras.callbacks.History, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    for metric in ["accuracy", "loss"]:
        plt.figure(figsize=(8, 5))
        plt.plot(history.history[metric], label=f"train_{metric}")
        plt.plot(history.history[f"val_{metric}"], label=f"val_{metric}")
        plt.title(f"Training {metric.title()}")
        plt.xlabel("Epoch")
        plt.ylabel(metric.title())
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_dir / f"{metric}.png", dpi=160)
        plt.close()


def main() -> None:
    args = parse_args()
    dataset_path = Path(args.dataset)
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset directory not found: {dataset_path.resolve()}")

    output_path = Path(args.output)
    labels_path = Path(args.labels)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    labels_path.parent.mkdir(parents=True, exist_ok=True)

    train_ds, val_ds, class_names = load_datasets(args)
    with labels_path.open("w", encoding="utf-8") as labels_file:
        json.dump(class_names, labels_file, indent=2)

    model = build_model(args.image_size, len(class_names))
    callbacks = [
        EarlyStopping(monitor="val_loss", patience=6, restore_best_weights=True),
        ReduceLROnPlateau(monitor="val_loss", patience=3, factor=0.3, min_lr=1e-7),
        ModelCheckpoint(str(output_path), monitor="val_accuracy", save_best_only=True),
    ]

    history = model.fit(train_ds, validation_data=val_ds, epochs=args.epochs, callbacks=callbacks)
    plot_history(history, Path(args.plots_dir))
    model.save(output_path)
    print(f"Saved model to {output_path}")
    print(f"Saved labels to {labels_path}")


if __name__ == "__main__":
    main()
