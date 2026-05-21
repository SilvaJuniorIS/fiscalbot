import { useEffect, useState } from 'react'
import api from '../services/api'
import Card from '../components/ui/Card'
import type { FiscalizacaoResumo } from '../types'

export default function Fiscalizacao() {
  const [resumo, setResumo] = useState<FiscalizacaoResumo | null>(null)

  useEffect(() => {
    api.get<FiscalizacaoResumo>('/api/v1/fiscalizacao/resumo').then((r) => setResumo(r.data))
  }, [])

  if (!resumo) return <p className="text-slate-400">Carregando...</p>

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Fiscalizacao operacional</h1>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <Card title="Vistorias no mes" value={resumo.vistorias_mes} />
        <Card title="Ocorrencias abertas" value={resumo.ocorrencias_abertas} />
        <Card title="Conformes" value={resumo.conformes} />
        <Card title="Com ressalva" value={resumo.com_ressalva} />
        <Card title="Com pendencia" value={resumo.com_pendencia} />
      </div>
      <p className="text-sm text-slate-400">
        Registre ocorrencias na pagina de detalhe de cada contrato (vistorias, pendencias, notificacoes).
      </p>
    </div>
  )
}
