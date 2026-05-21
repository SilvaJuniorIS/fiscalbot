import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import Badge from '../components/ui/Badge'
import { fetchContratos } from '../services/contratos'
import type { Contrato } from '../types'

export default function Contratos() {
  const [items, setItems] = useState<Contrato[]>([])
  const [status, setStatus] = useState('')
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)

  useEffect(() => {
    const params: Record<string, string | number> = { page, limit: 20 }
    if (status) params.status = status
    if (search) params.numero = search
    fetchContratos(params).then(setItems)
  }, [status, search, page])

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-semibold">Contratos</h1>
      </div>
      <div className="flex flex-wrap gap-2">
        <input
          className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm"
          placeholder="Buscar numero..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <select
          className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm"
          value={status}
          onChange={(e) => setStatus(e.target.value)}
        >
          <option value="">Todos os status</option>
          <option value="ativo">ativo</option>
          <option value="alerta">alerta</option>
          <option value="critico">critico</option>
          <option value="encerrado">encerrado</option>
        </select>
      </div>
      <div className="overflow-hidden rounded-xl border border-slate-800">
        <table className="w-full text-sm">
          <thead className="bg-slate-900 text-slate-400">
            <tr>
              <th className="px-4 py-3 text-left">Numero</th>
              <th className="px-4 py-3 text-left">Objeto</th>
              <th className="px-4 py-3 text-left">Secretaria</th>
              <th className="px-4 py-3 text-left">Status</th>
              <th className="px-4 py-3 text-left">Termino</th>
            </tr>
          </thead>
          <tbody>
            {items.map((c) => (
              <tr key={c.id} className="border-t border-slate-800 hover:bg-slate-900/50">
                <td className="px-4 py-3">
                  <Link to={`/contratos/${c.id}`} className="text-emerald-400 hover:underline">
                    {c.numero}
                  </Link>
                </td>
                <td className="max-w-xs truncate px-4 py-3 text-slate-300">{c.objeto}</td>
                <td className="px-4 py-3">{c.secretaria?.nome}</td>
                <td className="px-4 py-3">
                  <Badge label={c.status} />
                </td>
                <td className="px-4 py-3 text-slate-400">{c.termino}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="flex gap-2">
        <button
          type="button"
          disabled={page <= 1}
          onClick={() => setPage((p) => p - 1)}
          className="rounded border border-slate-700 px-3 py-1 text-sm disabled:opacity-40"
        >
          Anterior
        </button>
        <span className="px-2 py-1 text-sm text-slate-400">Pagina {page}</span>
        <button
          type="button"
          onClick={() => setPage((p) => p + 1)}
          className="rounded border border-slate-700 px-3 py-1 text-sm"
        >
          Proxima
        </button>
      </div>
    </div>
  )
}
