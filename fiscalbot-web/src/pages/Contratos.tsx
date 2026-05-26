import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'
import Card from '../components/ui/Card'
import { downloadContractsExport, fetchContracts, fetchContractsDashboard } from '../services/contracts'
import type { Contract, ContractDashboard } from '../types'

function expirationClass(days?: number | null) {
  if (days == null) return 'bg-slate-800 text-slate-300'
  if (days <= 7) return 'bg-red-950 text-red-200'
  if (days <= 15) return 'bg-orange-950 text-orange-200'
  if (days <= 30) return 'bg-amber-950 text-amber-200'
  return 'bg-emerald-950 text-emerald-200'
}

export default function Contratos() {
  const [items, setItems] = useState<Contract[]>([])
  const [dashboard, setDashboard] = useState<ContractDashboard | null>(null)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [status, setStatus] = useState('')
  const [secretaria, setSecretaria] = useState('')
  const [fornecedor, setFornecedor] = useState('')
  const [vencendo30, setVencendo30] = useState(false)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchContractsDashboard().then(setDashboard)
  }, [])

  useEffect(() => {
    setLoading(true)
    fetchContracts({
      page,
      limit: 20,
      status: status || undefined,
      secretaria: secretaria || undefined,
      fornecedor: fornecedor || undefined,
      vencendo_em_30: vencendo30 || undefined,
    })
      .then((result) => {
        setItems(result.items)
        setTotal(result.total)
      })
      .finally(() => setLoading(false))
  }, [page, status, secretaria, fornecedor, vencendo30])

  const pages = Math.max(1, Math.ceil(total / 20))
  const exportParams = {
    status: status || undefined,
    secretaria: secretaria || undefined,
    fornecedor: fornecedor || undefined,
    vencendo_em_30: vencendo30 || undefined,
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-semibold">Contratos</h1>
        <Link to="/importacao/contratos">
          <Button type="button">Importar Planilha</Button>
        </Link>
      </div>

      <div className="grid gap-4 md:grid-cols-5">
        <Card title="Contratos ativos" value={dashboard?.contratos_ativos ?? 0} />
        <Card title="Vencendo em 30 dias" value={dashboard?.vencendo_em_30 ?? 0} />
        <Card title="Vencendo em 15 dias" value={dashboard?.vencendo_em_15 ?? 0} />
        <Card title="Vencidos" value={dashboard?.vencidos ?? 0} />
        <Card
          title="Valor contratado"
          value={Number(dashboard?.valor_total_contratado ?? 0).toLocaleString('pt-BR', {
            style: 'currency',
            currency: 'BRL',
          })}
        />
      </div>

      <section className="rounded-lg border border-slate-800 bg-slate-900/70 p-4">
        <div className="grid gap-3 md:grid-cols-[1fr_1fr_160px_170px]">
          <input
            className="input"
            placeholder="Filtrar por fornecedor"
            value={fornecedor}
            onChange={(e) => {
              setFornecedor(e.target.value)
              setPage(1)
            }}
          />
          <input
            className="input"
            placeholder="Filtrar por secretaria"
            value={secretaria}
            onChange={(e) => {
              setSecretaria(e.target.value)
              setPage(1)
            }}
          />
          <select
            className="input"
            value={status}
            onChange={(e) => {
              setStatus(e.target.value)
              setPage(1)
            }}
          >
            <option value="">Todos</option>
            <option value="ativo">ativo</option>
            <option value="encerrado">encerrado</option>
            <option value="suspenso">suspenso</option>
          </select>
          <label className="flex items-center gap-2 rounded border border-slate-700 px-3 text-sm text-slate-300">
            <input
              type="checkbox"
              checked={vencendo30}
              onChange={(e) => {
                setVencendo30(e.target.checked)
                setPage(1)
              }}
            />
            Vencendo em 30
          </label>
        </div>
        <div className="mt-3 flex flex-wrap justify-end gap-2">
          <Button type="button" variant="ghost" onClick={() => downloadContractsExport('csv', exportParams)}>
            Exportar CSV
          </Button>
          <Button type="button" variant="ghost" onClick={() => downloadContractsExport('xlsx', exportParams)}>
            Exportar XLSX
          </Button>
          <Button type="button" variant="ghost" onClick={() => downloadContractsExport('pdf', exportParams)}>
            Exportar PDF
          </Button>
        </div>
      </section>

      <div className="overflow-x-auto rounded-lg border border-slate-800">
        <table className="w-full min-w-[900px] text-sm">
          <thead className="bg-slate-900 text-slate-400">
            <tr>
              <th className="px-4 py-3 text-left">Contrato</th>
              <th className="px-4 py-3 text-left">Fornecedor</th>
              <th className="px-4 py-3 text-left">Secretaria</th>
              <th className="px-4 py-3 text-left">Fiscal</th>
              <th className="px-4 py-3 text-left">Vencimento</th>
              <th className="px-4 py-3 text-left">Dias restantes</th>
              <th className="px-4 py-3 text-left">Status</th>
            </tr>
          </thead>
          <tbody>
            {items.map((contract) => (
              <tr key={contract.id} className="border-t border-slate-800 hover:bg-slate-900/50">
                <td className="px-4 py-3">
                  <Link to={`/contratos/${contract.id}`} className="text-emerald-400 hover:underline">
                    {contract.numero_contrato || 'Sem numero'}
                  </Link>
                </td>
                <td className="max-w-xs truncate px-4 py-3">{contract.fornecedor}</td>
                <td className="px-4 py-3">{contract.secretaria}</td>
                <td className="px-4 py-3">{contract.fiscal}</td>
                <td className="px-4 py-3 text-slate-300">{contract.fim_vigencia}</td>
                <td className="px-4 py-3">
                  <span className={`rounded-full px-2 py-1 text-xs ${expirationClass(contract.dias_para_vencimento)}`}>
                    {contract.dias_para_vencimento ?? '-'}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <Badge label={contract.status || 'sem_status'} />
                </td>
              </tr>
            ))}
            {!loading && items.length === 0 && (
              <tr>
                <td colSpan={7} className="px-4 py-8 text-center text-slate-500">
                  Nenhum contrato encontrado.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="flex items-center justify-between text-sm text-slate-400">
        <span>{loading ? 'Carregando...' : `${total} contratos encontrados`}</span>
        <div className="flex items-center gap-2">
          <button className="rounded border border-slate-700 px-3 py-1 disabled:opacity-40" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
            Anterior
          </button>
          <span>Pagina {page} de {pages}</span>
          <button className="rounded border border-slate-700 px-3 py-1 disabled:opacity-40" disabled={page >= pages} onClick={() => setPage((p) => p + 1)}>
            Proxima
          </button>
        </div>
      </div>
    </div>
  )
}
