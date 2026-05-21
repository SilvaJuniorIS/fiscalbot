import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'

const nav = [
  { to: '/', label: 'Dashboard' },
  { to: '/contratos', label: 'Contratos' },
  { to: '/alertas', label: 'Alertas' },
  { to: '/fiscalizacao', label: 'Fiscalizacao' },
]

export default function Layout({ children }: { children: React.ReactNode }) {
  const { pathname } = useLocation()
  const { user, logout } = useAuth()

  return (
    <div className="flex min-h-screen">
      <aside className="flex w-56 flex-col border-r border-slate-800 bg-slate-900 p-4">
        <div className="mb-6 text-lg font-bold text-emerald-400">FiscalBot</div>
        <nav className="flex flex-col gap-1">
          {nav.map(({ to, label }) => (
            <Link
              key={to}
              to={to}
              className={`rounded-lg px-3 py-2 text-sm ${
                pathname === to || (to !== '/' && pathname.startsWith(to))
                  ? 'bg-emerald-600 text-white'
                  : 'text-slate-300 hover:bg-slate-800'
              }`}
            >
              {label}
            </Link>
          ))}
        </nav>
        <div className="mt-auto border-t border-slate-800 pt-4 text-xs text-slate-400">
          <p className="font-medium text-slate-200">{user?.nome}</p>
          <p>{user?.role}</p>
          <button type="button" onClick={logout} className="mt-2 text-red-400 hover:underline">
            Sair
          </button>
        </div>
      </aside>
      <main className="flex-1 overflow-auto p-6">{children}</main>
    </div>
  )
}
