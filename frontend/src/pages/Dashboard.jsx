import { useEffect, useState } from 'react';

import HistoryTable from '../components/HistoryTable.jsx';
import StatsCards from '../components/StatsCards.jsx';
import { API_BASE_URL, getHistory, getStatistics } from '../services/api.js';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  const refresh = async () => {
    setLoading(true);
    try {
      const [statsData, historyData] = await Promise.all([getStatistics(), getHistory(100)]);
      setStats(statsData);
      setHistory(historyData);
    } catch {
      // backend unreachable — keep stale data visible
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refresh();
  }, []);

  return (
    <section className="space-y-6">
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
        <div>
          <p className="text-sm font-bold uppercase tracking-wide text-emerald-500">Analytics Dashboard</p>
          <h1 className="mt-2 text-4xl font-black text-slate-950 dark:text-white">Compliance overview and reports</h1>
          <p className="mt-3 text-slate-600 dark:text-slate-300">
            Monitor all saved detections, export analytics as CSV, and download a PDF report.
          </p>
        </div>
        <div className="flex flex-wrap gap-3">
          <button onClick={refresh} className="rounded-full border border-slate-300 px-5 py-2 font-bold dark:border-slate-700">
            {loading ? 'Refreshing...' : 'Refresh'}
          </button>
          <a href={`${API_BASE_URL}/analytics.csv`} className="rounded-full bg-slate-950 px-5 py-2 font-bold text-white dark:bg-white dark:text-slate-950">
            Export CSV
          </a>
          <a href={`${API_BASE_URL}/reports/pdf`} className="rounded-full bg-emerald-500 px-5 py-2 font-bold text-white">
            Download PDF
          </a>
        </div>
      </div>

      <StatsCards stats={stats} />
      <ComplianceBar stats={stats} />
      <HistoryTable rows={history} />
    </section>
  );
}

function ComplianceBar({ stats }) {
  const value = stats?.compliance_percentage ?? 0;
  return (
    <div className="glass-card rounded-3xl p-6 shadow-xl shadow-slate-200/50 dark:shadow-black/20">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-black text-slate-950 dark:text-white">Mask Compliance Percentage</h2>
          <p className="text-sm text-slate-500 dark:text-slate-400">Mask detections divided by total detected faces.</p>
        </div>
        <span className="text-3xl font-black text-emerald-500">{value}%</span>
      </div>
      <div className="mt-5 h-4 overflow-hidden rounded-full bg-slate-200 dark:bg-slate-800">
        <div className="h-full rounded-full bg-gradient-to-r from-emerald-400 to-cyan-400" style={{ width: `${Math.min(value, 100)}%` }} />
      </div>
    </div>
  );
}
