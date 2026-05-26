import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import Button from '../components/ui/Button'
import { useToast } from '../hooks/useToast'
import { fetchContract, updateContract } from '../services/contracts'
import type { Contract } from '../types'

const fields: { key: keyof Contract; label: string; type?: string; multiline?: boolean }[] = [
  { key: 'status', label: 'Status' },
  { key: 'numero_contrato', label: 'Numero do contrato' },
  { key: 'numero_aditivo', label: 'Numero do aditivo' },
  { key: 'fornecedor', label: 'Fornecedor' },
  { key: 'cnpj', label: 'CNPJ' },
  { key: 'secretaria', label: 'Secretaria' },
  { key: 'secretario', label: 'Secretario' },
  { key: 'gestor', label: 'Gestor' },
  { key: 'gestor_cpf', label: 'CPF do gestor' },
  { key: 'fiscal', label: 'Fiscal' },
  { key: 'fiscal_cpf', label: 'CPF do fiscal' },
  { key: 'objeto', label: 'Objeto', multiline: true },
  { key: 'vigencia_texto', label: 'Vigencia original' },
  { key: 'inicio_vigencia', label: 'Inicio da vigencia', type: 'date' },
  { key: 'fim_vigencia', label: 'Fim da vigencia', type: 'date' },
  { key: 'data_os', label: 'Data OS', type: 'date' },
  { key: 'processo_administrativo', label: 'Processo administrativo' },
  { key: 'processo_execucao', label: 'Processo execucao' },
  { key: 'audesp_licitacao', label: 'Audesp licitacao' },
  { key: 'audesp_ajuste', label: 'Audesp ajuste', multiline: true },
  { key: 'modalidade', label: 'Modalidade' },
  { key: 'valor_total', label: 'Valor total' },
  { key: 'data_assinatura', label: 'Data assinatura', type: 'date' },
  { key: 'data_publicacao', label: 'Data publicacao', type: 'date' },
  { key: 'observacao', label: 'Observacao', multiline: true },
]

export default function ContractForm() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { showToast, ToastView } = useToast()
  const [contract, setContract] = useState<Contract | null>(null)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (id) fetchContract(id).then(setContract)
  }, [id])

  function updateField(key: keyof Contract, value: string) {
    setContract((current) => (current ? { ...current, [key]: value || null } : current))
  }

  async function onSubmit(event: FormEvent) {
    event.preventDefault()
    if (!contract) return
    setSaving(true)
    try {
      const updated = await updateContract(contract.id, contract)
      setContract(updated)
      showToast('success', 'Contrato atualizado.')
      navigate(`/contratos/${updated.id}`)
    } catch {
      showToast('error', 'Nao foi possivel salvar o contrato.')
    } finally {
      setSaving(false)
    }
  }

  if (!contract) return <p className="text-slate-400">Carregando...</p>

  return (
    <form onSubmit={onSubmit} className="space-y-6">
      <ToastView />
      <Link to={`/contratos/${contract.id}`} className="text-sm text-emerald-400 hover:underline">
        &larr; Voltar
      </Link>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-semibold">Editar contrato</h1>
        <Button type="submit" disabled={saving}>
          {saving ? 'Salvando...' : 'Salvar'}
        </Button>
      </div>

      <section className="grid gap-4 md:grid-cols-2">
        {fields.map((field) => (
          <label key={field.key} className={field.multiline ? 'md:col-span-2' : ''}>
            <span className="mb-1 block text-xs uppercase text-slate-500">{field.label}</span>
            {field.multiline ? (
              <textarea
                className="input min-h-28"
                value={String(contract[field.key] ?? '')}
                onChange={(event) => updateField(field.key, event.target.value)}
              />
            ) : (
              <input
                className="input"
                type={field.type || 'text'}
                value={String(contract[field.key] ?? '')}
                onChange={(event) => updateField(field.key, event.target.value)}
              />
            )}
          </label>
        ))}
      </section>
    </form>
  )
}
