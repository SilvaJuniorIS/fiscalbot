import { useEffect, useState } from 'react'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'
import Card from '../components/ui/Card'
import { fetchAlertas, fetchResumo, marcarLido, resolver } from '../services/alertas'
import type { Alerta, AlertaResumo } from '../types'

export default function Alertas() {
  const [alertas, setAlertas] = useState<Alerta[]>([])
  const [resumo, setResumo] = useState<AlertaResumo | null>(null)

  async function load() {
    const [list, sum] = await Promise.all([fetchAlertas({ lido: false }), fetchResumo()])
    setAlertas(list)
    setResumo(sum)
  }

  useEffect(() => {
    load()
  }, [])

  async function onLido(id: number) {
    await marcarLido(id)
    load()
  }

  async function onResolver(id: number) {
    await resolver(id)
    load()
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Alertas</h1>
      {resumo && (
        <div className="grid gap-4 sm:grid-cols-4">
          <Card title="Urgentes" value={resumo.urgentes} />
          <Card title="Atencao" value={resumo.atencao} />
          <Card title="Informativos" value={resumo.info} />
          <Card title="Nao lidos" value={resumo.total_nao_lidos} />
        </div>
      )}
      <div className="space-y-3">
        {alertas.map((a) => (
          <div
            key={a.id}
            className="flex flex-wrap items-start justify-between gap-3 rounded-xl border border-slate-800 bg-slate-900/80 p-4"
          >
            <div>
              <div className="flex items-center gap-2">
                <Badge label={a.tipo} />
                <Badge label={a.status} />
              </div>
              <h3 className="mt-1 font-medium">{a.titulo}</h3>
              <p className="text-sm text-slate-400">{a.mensagem}</p>
              <p className="mt-1 text-xs text-slate-500">Ref: {a.data_referencia}</p>
            </div>
            <div className="flex gap-2">
              <Button variant="ghost" onClick={() => onLido(a.id)}>
                Marcar lido
              </Button>
              <Button onClick={() => onResolver(a.id)}>Resolver</Button>
            </div>
          </div>
        ))}
        {alertas.length === 0 && (
          <p className="text-slate-500">Nenhum alerta pendente. Execute a geracao na API se necessario.</p>
        )}
      </div>
    </div>
  )
}
