# Face Detection Model

`face_detection_yunet_2023mar.onnx` is the YuNet face detector from the
[official OpenCV Zoo repository](https://github.com/opencv/opencv_zoo/tree/main/models/face_detection_yunet).

`mask_detector.onnx` is the production classifier exported from the trained
Keras model. OpenCV DNN runs it without shipping the TensorFlow runtime.

The application uses YuNet by default and automatically falls back to OpenCV's
bundled Haar Cascade when the ONNX model cannot be loaded.
