import { useState } from 'react';

import PredictionSummary from '../components/PredictionSummary.jsx';
import { buildAssetUrl, predictImage } from '../services/api.js';

export default function UploadImage() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleFile = (selectedFile) => {
    setFile(selectedFile);
    setResult(null);
    setError('');
    setPreview(selectedFile ? URL.createObjectURL(selectedFile) : '');
  };

  const submit = async (event) => {
    event.preventDefault();
    if (!file) return;
    setLoading(true);
    setError('');
    try {
      setResult(await predictImage(file));
    } catch (err) {
      setError(err.response?.data?.detail || 'Image prediction failed.');
    } finally {
      setLoading(false);
    }
  };

  const imageToShow = result?.annotated_image_url ? buildAssetUrl(result.annotated_image_url) : preview;

  return (
    <section className="space-y-6">
      <div>
        <p className="text-sm font-bold uppercase tracking-wide text-emerald-500">Image Upload Detection</p>
        <h1 className="mt-2 text-4xl font-black text-slate-950 dark:text-white">Detect masks in JPG and PNG images</h1>
      </div>

      <div className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
        <form onSubmit={submit} className="glass-card rounded-3xl p-6 shadow-xl shadow-slate-200/50 dark:shadow-black/20">
          <label className="grid cursor-pointer place-items-center rounded-3xl border-2 border-dashed border-slate-300 bg-white/70 px-6 py-12 text-center transition hover:border-emerald-400 dark:border-slate-700 dark:bg-slate-900/70">
            <input
              type="file"
              accept=".jpg,.jpeg,.png,image/jpeg,image/png"
              className="hidden"
              onChange={(event) => handleFile(event.target.files?.[0])}
            />
            <span className="text-5xl">+</span>
            <span className="mt-3 text-lg font-black text-slate-900 dark:text-white">{file ? file.name : 'Choose an image'}</span>
            <span className="mt-1 text-sm text-slate-500 dark:text-slate-400">JPG, JPEG, PNG supported</span>
          </label>

          {error && <p className="mt-4 rounded-2xl bg-rose-100 p-3 text-sm font-semibold text-rose-700 dark:bg-rose-500/15 dark:text-rose-300">{error}</p>}

          <button
            type="submit"
            disabled={!file || loading}
            className="mt-5 w-full rounded-full bg-emerald-500 px-6 py-3 font-black text-white shadow-lg shadow-emerald-500/30 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? 'Processing...' : 'Run Detection'}
          </button>
        </form>

        <div className="space-y-6">
          <div className="rounded-3xl border border-slate-200 bg-white p-4 shadow-xl shadow-slate-200/50 dark:border-slate-800 dark:bg-slate-900 dark:shadow-black/20">
            {imageToShow ? (
              <img src={imageToShow} alt="Detection preview" className="max-h-[540px] w-full rounded-2xl object-contain" />
            ) : (
              <div className="grid aspect-video place-items-center rounded-2xl bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400">
                Uploaded and annotated image appears here.
              </div>
            )}
          </div>
          <PredictionSummary result={result} />
        </div>
      </div>
    </section>
  );
}
