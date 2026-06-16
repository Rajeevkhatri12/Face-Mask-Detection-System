import { useEffect, useRef, useState } from 'react';

import PredictionSummary from '../components/PredictionSummary.jsx';
import { predictCameraFrame } from '../services/api.js';

export default function LiveDetection() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const timerRef = useRef(null);
  const streamRef = useRef(null);
  const requestRef = useRef(null);
  const sessionRef = useRef(0);
  const persistRef = useRef(false);
  const [streaming, setStreaming] = useState(false);
  const [starting, setStarting] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [persist, setPersist] = useState(false);
  const [result, setResult] = useState(null);
  const [annotatedFrame, setAnnotatedFrame] = useState('');
  const [status, setStatus] = useState('Camera is idle.');

  useEffect(() => {
    persistRef.current = persist;
  }, [persist]);

  useEffect(
    () => () => {
      window.clearTimeout(timerRef.current);
      requestRef.current?.abort();
      streamRef.current?.getTracks().forEach((track) => track.stop());
    },
    []
  );

  const startCamera = async () => {
    if (!window.isSecureContext || !navigator.mediaDevices?.getUserMedia) {
      setStatus('Camera access requires HTTPS and a supported browser.');
      return;
    }

    setStarting(true);
    setStatus('Requesting camera access...');

    try {
      let stream;
      try {
        stream = await navigator.mediaDevices.getUserMedia({
          video: {
            width: { ideal: 640 },
            height: { ideal: 360 },
            facingMode: { ideal: 'user' }
          },
          audio: false
        });
      } catch (error) {
        if (error?.name !== 'OverconstrainedError') throw error;
        stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
      }

      const sessionId = sessionRef.current + 1;
      sessionRef.current = sessionId;
      streamRef.current = stream;
      setStreaming(true);
      videoRef.current.srcObject = stream;
      await new Promise((resolve) => window.requestAnimationFrame(resolve));
      await videoRef.current.play();

      setStatus('Camera started. Analyzing the first frame...');
      scheduleNextDetection(sessionId, 500);
    } catch (error) {
      streamRef.current?.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
      if (videoRef.current) videoRef.current.srcObject = null;
      setStreaming(false);
      setStatus(cameraErrorMessage(error));
    } finally {
      setStarting(false);
    }
  };

  const stopCamera = () => {
    sessionRef.current += 1;
    window.clearTimeout(timerRef.current);
    timerRef.current = null;
    requestRef.current?.abort();
    requestRef.current = null;
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    if (videoRef.current) videoRef.current.srcObject = null;
    setStreaming(false);
    setProcessing(false);
    setStatus('Camera stopped.');
  };

  const scheduleNextDetection = (sessionId, delay = 2200) => {
    window.clearTimeout(timerRef.current);
    timerRef.current = window.setTimeout(async () => {
      await captureAndPredict(sessionId);
      if (sessionId === sessionRef.current && streamRef.current?.active) {
        scheduleNextDetection(sessionId);
      }
    }, delay);
  };

  const captureAndPredict = async (sessionId = sessionRef.current) => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas || video.readyState < 2 || !streamRef.current?.active) {
      setStatus('Camera is not ready yet.');
      return;
    }
    if (requestRef.current) {
      setStatus('A frame is already being analyzed.');
      return;
    }

    const scale = Math.min(1, 640 / video.videoWidth);
    canvas.width = Math.max(1, Math.round(video.videoWidth * scale));
    canvas.height = Math.max(1, Math.round(video.videoHeight * scale));
    canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
    const imageBase64 = canvas.toDataURL('image/jpeg', 0.72);
    const controller = new window.AbortController();
    requestRef.current = controller;
    setProcessing(true);
    setStatus('Analyzing camera frame...');

    try {
      const data = await predictCameraFrame(imageBase64, persistRef.current, controller.signal);
      if (sessionId !== sessionRef.current) return;
      setResult(data);
      setAnnotatedFrame(data.annotated_image_base64);
      setStatus(`Detected ${data.total_faces} face(s).`);
    } catch (error) {
      if (error.code !== 'ERR_CANCELED' && sessionId === sessionRef.current) {
        setStatus(error.response?.data?.detail || 'Unable to process the camera frame.');
      }
    } finally {
      if (requestRef.current === controller) {
        requestRef.current = null;
        setProcessing(false);
      }
    }
  };

  const downloadScreenshot = () => {
    const link = document.createElement('a');
    link.href = annotatedFrame || canvasRef.current.toDataURL('image/jpeg', 0.9);
    link.download = `maskguard-screenshot-${Date.now()}.jpg`;
    link.click();
  };

  return (
    <section className="space-y-6">
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
        <div>
          <p className="text-sm font-bold uppercase tracking-wide text-emerald-500">Live Camera Detection</p>
          <h1 className="mt-2 text-4xl font-black text-slate-950 dark:text-white">Browser webcam mask detection</h1>
          <p className="mt-3 max-w-2xl text-slate-600 dark:text-slate-300">
            Frames are captured in the browser, sent to FastAPI, processed by OpenCV and the mask classifier, then returned with labels and confidence scores.
          </p>
        </div>
        <label className="flex items-center gap-3 rounded-full bg-white px-4 py-3 text-sm font-bold shadow dark:bg-slate-900">
          <input type="checkbox" checked={persist} onChange={(event) => setPersist(event.target.checked)} />
          Save camera detections
        </label>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="glass-card rounded-3xl p-4 shadow-xl shadow-slate-200/50 dark:shadow-black/20">
          <div className="relative overflow-hidden rounded-2xl bg-slate-950">
            <video
              ref={videoRef}
              autoPlay
              muted
              playsInline
              className="aspect-video w-full object-cover"
            />
            {!streaming && annotatedFrame && <img src={annotatedFrame} alt="Latest annotated camera frame" className="absolute inset-0 aspect-video w-full object-cover" />}
            {!streaming && !annotatedFrame && (
              <button
                type="button"
                onClick={startCamera}
                disabled={starting}
                className="absolute inset-0 grid w-full place-items-center bg-slate-950 text-slate-200 disabled:cursor-wait"
              >
                <span className="flex flex-col items-center gap-3 px-6 text-center">
                  <span className="rounded-full bg-emerald-500 px-6 py-3 font-black text-white shadow-lg shadow-emerald-500/30">
                    {starting ? 'Requesting Camera...' : 'Start Camera'}
                  </span>
                  <span className="max-w-md text-sm font-semibold text-slate-400">{status}</span>
                </span>
              </button>
            )}
            {streaming && (
              <span className="absolute left-3 top-3 rounded-full bg-rose-500 px-3 py-1 text-xs font-black uppercase tracking-wide text-white shadow">
                {processing ? 'Analyzing' : 'Live'}
              </span>
            )}
          </div>
          <canvas ref={canvasRef} className="hidden" />
          <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
            <p className="text-sm font-semibold text-slate-600 dark:text-slate-300">{status}</p>
            <div className="flex flex-wrap gap-3">
              {!streaming ? (
                <button
                  onClick={startCamera}
                  disabled={starting}
                  className="rounded-full bg-emerald-500 px-5 py-2 font-bold text-white disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {starting ? 'Starting...' : 'Start Camera'}
                </button>
              ) : (
                <button onClick={stopCamera} className="rounded-full bg-rose-500 px-5 py-2 font-bold text-white">
                  Stop Camera
                </button>
              )}
              <button onClick={() => captureAndPredict()} disabled={!streaming || processing} className="rounded-full border border-slate-300 px-5 py-2 font-bold disabled:opacity-50 dark:border-slate-700">
                {processing ? 'Analyzing...' : 'Detect Now'}
              </button>
              <button onClick={downloadScreenshot} disabled={!annotatedFrame && !streaming} className="rounded-full border border-slate-300 px-5 py-2 font-bold disabled:opacity-50 dark:border-slate-700">
                Capture Screenshot
              </button>
            </div>
          </div>
        </div>
        <PredictionSummary result={result} />
      </div>
    </section>
  );
}

function cameraErrorMessage(error) {
  switch (error?.name) {
    case 'NotAllowedError':
    case 'SecurityError':
      return 'Camera permission was denied. Allow camera access in your browser settings and try again.';
    case 'NotFoundError':
    case 'DevicesNotFoundError':
      return 'No camera was found on this device.';
    case 'NotReadableError':
    case 'TrackStartError':
      return 'The camera is already in use by another application.';
    case 'OverconstrainedError':
      return 'The camera does not support the requested video settings.';
    default:
      return 'Unable to start the camera. Check browser permissions and try again.';
  }
}
