import { Link } from 'react-router-dom';

export default function Home() {
  return (
    <section className="grid items-center gap-10 py-10 lg:grid-cols-[1.1fr_0.9fr]">
      <div>
        <p className="mb-4 inline-flex rounded-full bg-emerald-100 px-4 py-2 text-sm font-bold text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-300">
          AI + OpenCV + FastAPI + React
        </p>
        <h1 className="text-5xl font-black leading-tight text-slate-950 dark:text-white md:text-7xl">
          Intelligent Face Mask Detection System
        </h1>
        <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-600 dark:text-slate-300">
          Detect mask compliance in real time from a browser camera or uploaded images. The system annotates every face,
          records detections, and produces analytics, CSV exports, and PDF reports for final-year project documentation.
        </p>
        <div className="mt-8 flex flex-wrap gap-4">
          <Link to="/live" className="rounded-full bg-emerald-500 px-6 py-3 font-bold text-white shadow-lg shadow-emerald-500/30">
            Start Live Detection
          </Link>
          <Link to="/upload" className="rounded-full border border-slate-300 px-6 py-3 font-bold text-slate-700 dark:border-slate-700 dark:text-slate-100">
            Upload Image
          </Link>
        </div>
      </div>

      <div className="glass-card relative overflow-hidden rounded-[2rem] p-6 shadow-2xl shadow-emerald-500/10">
        <div className="absolute -right-16 -top-16 h-48 w-48 rounded-full bg-emerald-400/30 blur-3xl" />
        <div className="relative rounded-[1.5rem] bg-slate-950 p-5 text-white">
          <div className="mb-5 flex gap-2">
            <span className="h-3 w-3 rounded-full bg-red-400" />
            <span className="h-3 w-3 rounded-full bg-amber-400" />
            <span className="h-3 w-3 rounded-full bg-emerald-400" />
          </div>
          <div className="grid gap-4">
            {[
              ['Mask', '98.4%', 'border-emerald-400 text-emerald-300'],
              ['No Mask', '94.2%', 'border-rose-400 text-rose-300'],
              ['Incorrect Mask', '86.8%', 'border-amber-400 text-amber-300']
            ].map(([label, confidence, classes]) => (
              <div key={label} className={`rounded-2xl border p-4 ${classes}`}>
                <div className="flex items-center justify-between">
                  <span className="font-black">{label}</span>
                  <span>{confidence}</span>
                </div>
                <div className="mt-3 h-24 rounded-xl border border-dashed border-current opacity-70" />
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
