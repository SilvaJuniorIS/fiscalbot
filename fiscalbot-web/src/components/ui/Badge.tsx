const colors: Record<string, string> = {
  ativo: 'bg-emerald-900 text-emerald-300',
  alerta: 'bg-amber-900 text-amber-300',
  critico: 'bg-red-900 text-red-300',
  encerrado: 'bg-slate-700 text-slate-300',
  pendente: 'bg-orange-900 text-orange-300',
  lido: 'bg-slate-700 text-slate-300',
  resolvido: 'bg-emerald-800 text-emerald-200',
}

export default function Badge({ label }: { label: string }) {
  const cls = colors[label] || 'bg-slate-800 text-slate-300'
  return (
    <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${cls}`}>
      {label}
    </span>
  )
}
