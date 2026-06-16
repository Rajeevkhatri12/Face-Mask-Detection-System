import argparse
from pathlib import Path

import tensorflow as tf
import tf2onnx
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export the trained Keras classifier to ONNX.")
    parser.add_argument("--model", default="../backend/model/mask_detector.h5")
    parser.add_argument("--output", default="../backend/model/mask_detector.onnx")
    parser.add_argument("--image-size", type=int, default=224)
    parser.add_argument("--opset", type=int, default=13)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    model_path = Path(args.model)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    model = tf.keras.models.load_model(
        model_path,
        custom_objects={"preprocess_input": preprocess_input},
        compile=False,
    )
    input_signature = (
        tf.TensorSpec((None, args.image_size, args.image_size, 3), tf.float32, name="input"),
    )
    tf2onnx.convert.from_keras(
        model,
        input_signature=input_signature,
        opset=args.opset,
        output_path=str(output_path),
    )
    print(f"Saved ONNX model to {output_path}")


if __name__ == "__main__":
    main()
