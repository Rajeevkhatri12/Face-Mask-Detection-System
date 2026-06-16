export default function HistoryTable({ rows = [] }) {
  return (
    <div className="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-xl shadow-slate-200/50 dark:border-slate-800 dark:bg-slate-900 dark:shadow-black/20">
      <div className="border-b border-slate-200 px-6 py-4 dark:border-slate-800">
        <h2 className="text-xl font-black text-slate-950 dark:text-white">Detection History</h2>
        <p className="text-sm text-slate-500 dark:text-slate-400">Latest persisted upload and camera detections.</p>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200 text-left text-sm dark:divide-slate-800">
          <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500 dark:bg-slate-950 dark:text-slate-400">
            <tr>
              <th className="px-6 py-3">Time</th>
              <th className="px-6 py-3">Source</th>
              <th className="px-6 py-3">Result</th>
              <th className="px-6 py-3">Confidence</th>
              <th className="px-6 py-3">Face Box</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
            {rows.length === 0 ? (
              <tr>
                <td colSpan="5" className="px-6 py-8 text-center text-slate-500 dark:text-slate-400">
                  No detections recorded yet.
                </td>
              </tr>
            ) : (
              rows.map((row) => (
                <tr key={row.id} className="text-slate-700 dark:text-slate-200">
                  <td className="whitespace-nowrap px-6 py-4">{new Date(row.timestamp).toLocaleString()}</td>
                  <td className="px-6 py-4 capitalize">{row.source}</td>
                  <td className="px-6 py-4">
                    <span className={badgeClass(row.result)}>{row.result}</span>
                  </td>
                  <td className="px-6 py-4">{Math.round(row.confidence * 100)}%</td>
                  <td className="px-6 py-4">
                    {row.face_x ?? '-'}, {row.face_y ?? '-'} / {row.face_width ?? '-'}x{row.face_height ?? '-'}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function badgeClass(result) {
  const base = 'rounded-full px-3 py-1 text-xs font-bold';
  if (result === 'Mask') return `${base} bg-emerald-100 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-300`;
  if (result === 'No Mask') return `${base} bg-rose-100 text-rose-700 dark:bg-rose-500/15 dark:text-rose-300`;
  return `${base} bg-amber-100 text-amber-700 dark:bg-amber-500/15 dark:text-amber-300`;
}
