import { useEffect, useState } from 'react'
import { Bar, BarChart, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { Link } from 'react-router-dom'
import Badge from '../components/ui/Badge'
import Card from '../components/ui/Card'
import { fetchContractsDashboard } from '../services/contracts'
import type { ContractDashboard } from '../types'

const PIE_COLORS = ['#10b981', '#f59e0b', '#ef4444', '#64748b', '#3b82f6']

export default function Dashboard() {
  const [dash, setDash] = useState<ContractDashboard | null>(null)
  const [error, setError] = useState(false)

  useEffect(() => {
    fetchContractsDashboard().then(setDash).catch(() => setError(true))
  }, [])

  if (error) return <p role="alert" className="text-red-400">Nao foi possivel carregar o dashboard. Atualize a pagina para tentar novamente.</p>

  if (!dash) return <p className="text-slate-400">Carregando dashboard...</p>

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Dashboard gerencial</h1>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Link to="/contratos"><Card title="Registros cadastrados" value={dash.total_registros ?? 0} /></Link>
        <Link to="/contratos?tipo=contrato"><Card title="Contratos" value={dash.total_contratos ?? 0} /></Link>
        <Link to="/contratos?tipo=ata"><Card title="Atas" value={dash.total_atas ?? 0} /></Link>
        <Link to="/contratos?incompletos=true"><Card title="Dados incompletos" value={dash.dados_incompletos ?? 0} /></Link>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card title="Contratos ativos" value={dash.contratos_ativos} />
        <Card title="Vencendo em 30 dias" value={dash.vencendo_em_30} />
        <Card
          title="Valor total"
          value={Number(dash.valor_total_contratado).toLocaleString('pt-BR', {
            style: 'currency',
            currency: 'BRL',
          })}
        />
        <Card title="Vencidos" value={dash.vencidos} />
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-4">
          <h2 className="mb-3 text-sm font-medium text-slate-300">Por secretaria</h2>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={dash.por_secretaria ?? []}>
              <XAxis dataKey="nome" tick={{ fill: '#94a3b8', fontSize: 11 }} />
              <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} />
              <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid #334155' }} />
              <Bar dataKey="total" fill="#10b981" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-4">
          <h2 className="mb-3 text-sm font-medium text-slate-300">Por status</h2>
          <ResponsiveContainer width="100%" height={240}>
            <PieChart>
              <Pie data={dash.por_status ?? []} dataKey="total" nameKey="status" cx="50%" cy="50%" outerRadius={80}>
                {(dash.por_status ?? []).map((_, i) => (
                  <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid #334155' }} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
      <section className="rounded-xl border border-slate-800 bg-slate-900/80 p-4">
        <h2 className="font-medium">O que precisa de atencao hoje</h2>
        <p className="mt-1 text-xs text-slate-400">Ate 10 registros por vencimento, incluindo dados incompletos. A situacao e calculada na consulta.</p>
        <div className="mt-3 space-y-3">{(dash.prioridades ?? []).map(c => <div key={c.id} className="border-t border-slate-800 pt-2 text-sm">
          <Link className="text-emerald-400" to={`/contratos/${c.id}`}>{c.tipo === 'ata' ? 'Ata' : 'Contrato'} · {c.numero_contrato || 'Sem numero'}</Link>
          <span className="ml-3 text-slate-300">{c.situacao} · {c.fim_vigencia || 'Sem vencimento'}</span>
          {!!c.dados_pendentes?.length && <p className="text-xs text-amber-400">Revisar: {c.dados_pendentes.join(', ')}</p>}
        </div>)}{!dash.prioridades?.length && <p className="text-sm text-slate-400">Nenhuma prioridade encontrada.</p>}</div>
      </section>
      {!!dash.grupos_duplicados && <section className="rounded-xl border border-amber-800 p-4">
        <h2 className="font-medium text-amber-300">{dash.grupos_duplicados} grupos com possiveis duplicados</h2>
        <p className="text-sm text-slate-400">Nenhum registro foi excluido automaticamente. Confira os detalhes antes de alterar. Exibindo ate 20 registros.</p>
        <ul className="mt-3 space-y-2">{(dash.duplicados ?? []).map(c => <li key={c.id}><Link className="text-sm text-emerald-400" to={`/contratos/${c.id}`}>{c.tipo} · {c.numero_contrato} · {c.fornecedor} · {c.secretaria}</Link></li>)}</ul>
      </section>}
      <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-4">
        <h2 className="mb-3 text-sm font-medium text-slate-300">Ultimos contratos e atas</h2>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-slate-500">
              <th className="pb-2">Numero</th>
              <th>Status</th>
              <th>Termino</th>
            </tr>
          </thead>
          <tbody>
            {(dash.ultimos_contratos ?? []).map((c) => (
              <tr key={c.id} className="border-t border-slate-800">
                <td className="py-2">
                  <Link className="text-emerald-400 hover:underline" to={`/contratos/${c.id}`}>
                    {c.numero_contrato}
                  </Link>
                </td>
                <td>
                  <Badge label={c.situacao || c.status || 'Sem status'} />
                </td>
                <td className="text-slate-400">{c.fim_vigencia || 'Sem data'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
