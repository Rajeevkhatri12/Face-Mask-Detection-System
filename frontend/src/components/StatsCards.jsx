const cards = [
  { key: 'total_faces', label: 'Total Faces', tone: 'from-blue-500 to-cyan-500' },
  { key: 'mask_count', label: 'Mask Count', tone: 'from-emerald-500 to-green-500' },
  { key: 'no_mask_count', label: 'No Mask Count', tone: 'from-rose-500 to-red-500' },
  { key: 'compliance_percentage', label: 'Compliance', tone: 'from-violet-500 to-fuchsia-500', suffix: '%' }
];

export default function StatsCards({ stats }) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {cards.map((card) => (
        <article key={card.key} className="glass-card rounded-3xl p-5 shadow-xl shadow-slate-200/50 dark:shadow-black/20">
          <div className={`mb-4 h-2 w-20 rounded-full bg-gradient-to-r ${card.tone}`} />
          <p className="text-sm font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">{card.label}</p>
          <p className="mt-2 text-4xl font-black text-slate-950 dark:text-white">
            {stats?.[card.key] ?? 0}
            {card.suffix || ''}
          </p>
        </article>
      ))}
    </div>
  );
}
