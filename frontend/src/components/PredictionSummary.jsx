export default function PredictionSummary({ result }) {
  if (!result) return null;

  return (
    <div className="glass-card rounded-3xl p-6 shadow-xl shadow-slate-200/50 dark:shadow-black/20">
      <h2 className="text-xl font-black text-slate-950 dark:text-white">Detection Result</h2>
      <div className="mt-4 grid gap-3 sm:grid-cols-4">
        <Metric label="Faces" value={result.total_faces} />
        <Metric label="Mask" value={result.mask_count} tone="text-emerald-500" />
        <Metric label="No Mask" value={result.no_mask_count} tone="text-rose-500" />
        <Metric label="Compliance" value={`${result.compliance_percentage}%`} tone="text-violet-500" />
      </div>
      <div className="mt-5 space-y-2">
        {result.predictions?.map((prediction, index) => (
          <div
            key={`${prediction.label}-${index}`}
            className="flex flex-wrap items-center justify-between gap-3 rounded-2xl bg-slate-100 px-4 py-3 dark:bg-slate-800"
          >
            <span className="font-bold text-slate-800 dark:text-slate-100">
              Face {index + 1}: {prediction.label}
            </span>
            <span className="text-sm font-semibold text-slate-500 dark:text-slate-400">
              {(prediction.confidence * 100).toFixed(1)}% confidence | x:{prediction.box.x} y:{prediction.box.y}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

function Metric({ label, value, tone = 'text-slate-950 dark:text-white' }) {
  return (
    <div className="rounded-2xl bg-white p-4 dark:bg-slate-900">
      <p className="text-xs font-bold uppercase tracking-wide text-slate-500 dark:text-slate-400">{label}</p>
      <p className={`mt-1 text-2xl font-black ${tone}`}>{value}</p>
    </div>
  );
}
