import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'
import { fetchContratosPage } from '../services/contratos'
import type { Contrato } from '../types'

export default function Contratos() {
  const [items, setItems] = useState<Contrato[]>([])
  const [total, setTotal] = useState(0)
  const [status, setStatus] = useState('')
  const [search, setSearch] = useState('')
  const [orderBy, setOrderBy] = useState('termino')
  const [orderDir, setOrderDir] = useState<'asc' | 'desc'>('asc')
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const params: Record<string, string | number> = { page, limit: 20, order_by: orderBy, order_dir: orderDir }
    if (status) params.status = status
    if (search) params.q = search
    setLoading(true)
    fetchContratosPage(params)
      .then((result) => {
        setItems(result.items)
        setTotal(result.total)
      })
      .finally(() => setLoading(false))
  }, [status, search, page, orderBy, orderDir])

  const pages = Math.max(1, Math.ceil(total / 20))

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-semibold">Contratos</h1>
        <div className="flex gap-2">
          <Link to="/importacao/contratos">
            <Button type="button" variant="ghost">Importar Contratos</Button>
          </Link>
          <Link to="/contratos/novo">
            <Button type="button">Novo Contrato</Button>
          </Link>
        </div>
      </div>
      <div className="flex flex-wrap gap-2">
        <input
          className="input max-w-xs"
          placeholder="Buscar numero, orgao ou objeto..."
          value={search}
          onChange={(e) => {
            setSearch(e.target.value)
            setPage(1)
          }}
        />
        <select
          className="input max-w-48"
          value={status}
          onChange={(e) => {
            setStatus(e.target.value)
            setPage(1)
          }}
        >
          <option value="">Todos os status</option>
          <option value="ativo">ativo</option>
          <option value="alerta">alerta</option>
          <option value="critico">critico</option>
          <option value="encerrado">encerrado</option>
        </select>
        <select className="input max-w-44" value={orderBy} onChange={(e) => setOrderBy(e.target.value)}>
          <option value="termino">Termino</option>
          <option value="numero">Numero</option>
          <option value="valor">Valor</option>
          <option value="status">Status</option>
        </select>
        <select className="input max-w-36" value={orderDir} onChange={(e) => setOrderDir(e.target.value as 'asc' | 'desc')}>
          <option value="asc">Crescente</option>
          <option value="desc">Decrescente</option>
        </select>
      </div>
      <div className="overflow-x-auto rounded-lg border border-slate-800">
        <table className="min-w-[760px] w-full text-sm">
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
            {!loading && items.length === 0 && (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-slate-500">
                  Nenhum contrato encontrado.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      <div className="flex flex-wrap items-center justify-between gap-2">
        <span className="text-sm text-slate-400">
          {loading ? 'Carregando...' : `${total} contratos encontrados`}
        </span>
        <div className="flex gap-2">
        <button
          type="button"
          disabled={page <= 1}
          onClick={() => setPage((p) => p - 1)}
          className="rounded border border-slate-700 px-3 py-1 text-sm disabled:opacity-40"
        >
          Anterior
        </button>
        <span className="px-2 py-1 text-sm text-slate-400">Pagina {page} de {pages}</span>
        <button
          type="button"
          disabled={page >= pages}
          onClick={() => setPage((p) => p + 1)}
          className="rounded border border-slate-700 px-3 py-1 text-sm disabled:opacity-40"
        >
          Proxima
        </button>
        </div>
      </div>
    </div>
  )
}
