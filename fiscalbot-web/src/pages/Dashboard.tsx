import { useEffect, useState } from 'react'
import { Bar, BarChart, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { Link } from 'react-router-dom'
import Badge from '../components/ui/Badge'
import Card from '../components/ui/Card'
import { fetchContratos, fetchDashboard } from '../services/contratos'
import type { Contrato, ContratoDashboard } from '../types'

const PIE_COLORS = ['#10b981', '#f59e0b', '#ef4444', '#64748b', '#3b82f6']

export default function Dashboard() {
  const [dash, setDash] = useState<ContratoDashboard | null>(null)
  const [contratos, setContratos] = useState<Contrato[]>([])

  useEffect(() => {
    fetchDashboard().then(setDash)
    fetchContratos({ limit: 5, page: 1 }).then(setContratos)
  }, [])

  if (!dash) return <p className="text-slate-400">Carregando dashboard...</p>

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Dashboard gerencial</h1>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card title="Contratos ativos" value={dash.ativos} />
        <Card title="Vencendo em 30 dias" value={dash.vencendo_30} />
        <Card
          title="Valor total"
          value={Number(dash.valor_total).toLocaleString('pt-BR', {
            style: 'currency',
            currency: 'BRL',
          })}
        />
        <Card title="Em risco" value={dash.em_risco} />
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-4">
          <h2 className="mb-3 text-sm font-medium text-slate-300">Por secretaria</h2>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={dash.por_secretaria}>
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
              <Pie data={dash.por_status} dataKey="total" nameKey="status" cx="50%" cy="50%" outerRadius={80}>
                {dash.por_status.map((_, i) => (
                  <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid #334155' }} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
      <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-4">
        <h2 className="mb-3 text-sm font-medium text-slate-300">Ultimos contratos</h2>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-slate-500">
              <th className="pb-2">Numero</th>
              <th>Status</th>
              <th>Termino</th>
            </tr>
          </thead>
          <tbody>
            {contratos.map((c) => (
              <tr key={c.id} className="border-t border-slate-800">
                <td className="py-2">
                  <Link className="text-emerald-400 hover:underline" to={`/contratos/${c.id}`}>
                    {c.numero}
                  </Link>
                </td>
                <td>
                  <Badge label={c.status} />
                </td>
                <td className="text-slate-400">{c.termino}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
