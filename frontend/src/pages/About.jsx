const stack = [
  ['Frontend', 'React.js, Tailwind CSS, Axios, Browser Media APIs'],
  ['Backend', 'FastAPI, OpenCV, SQLAlchemy, SQLite'],
  ['AI/ML', 'TensorFlow, Keras, MobileNetV2 transfer learning'],
  ['Deployment', 'Docker Compose, Nginx, environment variables']
];

export default function About() {
  return (
    <section className="space-y-8">
      <div className="glass-card rounded-[2rem] p-8 shadow-xl shadow-slate-200/50 dark:shadow-black/20">
        <p className="text-sm font-bold uppercase tracking-wide text-emerald-500">About Project</p>
        <h1 className="mt-2 text-4xl font-black text-slate-950 dark:text-white">AI-powered Face Mask Detection System</h1>
        <p className="mt-5 max-w-4xl text-lg leading-8 text-slate-600 dark:text-slate-300">
          MaskGuard AI is a complete final-year-project style system for detecting whether people are wearing masks,
          not wearing masks, or wearing masks incorrectly. It combines real-time browser capture, OpenCV face detection,
          Keras transfer learning, analytics persistence, and deployment-ready containers.
        </p>
      </div>

      <div className="grid gap-5 md:grid-cols-2">
        {stack.map(([title, body]) => (
          <article key={title} className="rounded-3xl border border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-slate-900">
            <h2 className="text-xl font-black text-slate-950 dark:text-white">{title}</h2>
            <p className="mt-3 text-slate-600 dark:text-slate-300">{body}</p>
          </article>
        ))}
      </div>

      <div className="rounded-3xl border border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-slate-900">
        <h2 className="text-xl font-black text-slate-950 dark:text-white">Core Workflow</h2>
        <ol className="mt-4 grid gap-3 text-slate-600 dark:text-slate-300 md:grid-cols-4">
          <li className="rounded-2xl bg-slate-100 p-4 dark:bg-slate-800">1. Capture or upload an image.</li>
          <li className="rounded-2xl bg-slate-100 p-4 dark:bg-slate-800">2. Detect faces using OpenCV.</li>
          <li className="rounded-2xl bg-slate-100 p-4 dark:bg-slate-800">3. Classify each face with MobileNetV2.</li>
          <li className="rounded-2xl bg-slate-100 p-4 dark:bg-slate-800">4. Store, annotate, and report results.</li>
        </ol>
      </div>
    </section>
  );
}
