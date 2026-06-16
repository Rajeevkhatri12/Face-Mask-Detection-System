import { NavLink } from 'react-router-dom';

const links = [
  { to: '/', label: 'Home' },
  { to: '/live', label: 'Live Detection' },
  { to: '/upload', label: 'Upload Image' },
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/about', label: 'About' }
];

export default function Navbar({ darkMode, onToggleTheme }) {
  return (
    <header className="sticky top-0 z-40 border-b border-slate-200/70 bg-white/85 backdrop-blur dark:border-slate-800 dark:bg-slate-950/85">
      <nav className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-4 md:flex-row md:items-center md:justify-between">
        <NavLink to="/" className="flex items-center gap-3">
          <span className="grid h-11 w-11 place-items-center rounded-2xl bg-emerald-500 text-xl font-black text-white shadow-lg shadow-emerald-500/30">
            FM
          </span>
          <div>
            <p className="text-lg font-black text-slate-950 dark:text-white">MaskGuard AI</p>
            <p className="text-xs text-slate-500 dark:text-slate-400">Real-time face mask detection</p>
          </div>
        </NavLink>

        <div className="flex flex-wrap items-center gap-2">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                `rounded-full px-4 py-2 text-sm font-semibold transition ${
                  isActive
                    ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/25'
                    : 'text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800'
                }`
              }
            >
              {link.label}
            </NavLink>
          ))}
          <button
            type="button"
            onClick={onToggleTheme}
            className="rounded-full border border-slate-200 px-4 py-2 text-sm font-bold text-slate-700 transition hover:bg-slate-100 dark:border-slate-700 dark:text-slate-100 dark:hover:bg-slate-800"
          >
            {darkMode ? 'Light' : 'Dark'} mode
          </button>
        </div>
      </nav>
    </header>
  );
}
