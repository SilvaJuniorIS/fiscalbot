import { useEffect, useMemo, useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import Button from '../components/ui/Button'
import {
  createContrato,
  fetchContrato,
  fetchFornecedores,
  fetchSecretarias,
  fetchUsuarios,
  updateContrato,
} from '../services/contratos'
import { useAuth } from '../hooks/useAuth'
import { useToast } from '../hooks/useToast'
import type { ContratoPayload, Fornecedor, Secretaria, User } from '../types'

const emptyForm: ContratoPayload = {
  numero: '',
  orgao: '',
  objeto: '',
  valor: '',
  inicio: '',
  termino: '',
  status: 'ativo',
  tags: '',
  secretaria_id: 0,
  fornecedor_id: 0,
  fiscal_responsavel_id: null,
  gestor_responsavel_id: null,
}

const requiredFields: Array<keyof ContratoPayload> = [
  'numero',
  'orgao',
  'objeto',
  'valor',
  'inicio',
  'termino',
  'secretaria_id',
  'fornecedor_id',
]

export default function ContratoForm() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user, hasRole } = useAuth()
  const { showToast, ToastView } = useToast()
  const contratoId = id ? Number(id) : null
  const isEdit = Boolean(contratoId)
  const canWrite = hasRole('admin', 'gestor')

  const [form, setForm] = useState<ContratoPayload>(emptyForm)
  const [secretarias, setSecretarias] = useState<Secretaria[]>([])
  const [fornecedores, setFornecedores] = useState<Fornecedor[]>([])
  const [usuarios, setUsuarios] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [submitted, setSubmitted] = useState(false)

  const fiscais = useMemo(() => usuarios.filter((u) => ['fiscal', 'admin'].includes(u.role)), [usuarios])
  const gestores = useMemo(() => usuarios.filter((u) => ['gestor', 'admin'].includes(u.role)), [usuarios])

  useEffect(() => {
    async function load() {
      setLoading(true)
      try {
        const [secs, fors] = await Promise.all([fetchSecretarias(), fetchFornecedores()])
        setSecretarias(secs)
        setFornecedores(fors)
        try {
          setUsuarios(await fetchUsuarios())
        } catch {
          setUsuarios(user ? [user] : [])
        }
        if (contratoId) {
          const contrato = await fetchContrato(contratoId)
          setForm({
            numero: contrato.numero,
            orgao: contrato.orgao,
            objeto: contrato.objeto,
            valor: String(contrato.valor),
            inicio: contrato.inicio,
            termino: contrato.termino,
            status: contrato.status,
            tags: contrato.tags || '',
            secretaria_id: contrato.secretaria_id,
            fornecedor_id: contrato.fornecedor_id,
            fiscal_responsavel_id: contrato.fiscal_responsavel_id || null,
            gestor_responsavel_id: contrato.gestor_responsavel_id || null,
          })
        } else {
          setForm((current) => ({
            ...current,
            secretaria_id: user?.secretaria_id || secs[0]?.id || 0,
            fornecedor_id: fors[0]?.id || 0,
            gestor_responsavel_id: user?.role === 'gestor' ? user.id : null,
          }))
        }
      } catch {
        showToast('error', 'Nao foi possivel carregar os dados do formulario.')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [contratoId, user])

  function updateField(field: keyof ContratoPayload, value: string | number | null) {
    setForm((current) => ({ ...current, [field]: value }))
  }

  function invalid(field: keyof ContratoPayload) {
    const value = form[field]
    return submitted && requiredFields.includes(field) && (!value || value === 0)
  }

  function validate() {
    if (!canWrite) return false
    if (requiredFields.some((field) => !form[field] || form[field] === 0)) return false
    if (Number(form.valor) < 0) return false
    if (form.termino < form.inicio) return false
    return true
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    setSubmitted(true)
    if (!validate()) {
      showToast('error', 'Revise os campos obrigatorios do contrato.')
      return
    }
    setSaving(true)
    try {
      const payload = {
        ...form,
        fiscal_responsavel_id: form.fiscal_responsavel_id || null,
        gestor_responsavel_id: form.gestor_responsavel_id || null,
      }
      const saved = isEdit && contratoId ? await updateContrato(contratoId, payload) : await createContrato(payload)
      showToast('success', isEdit ? 'Contrato atualizado.' : 'Contrato criado.')
      navigate(`/contratos/${saved.id}`)
    } catch {
      showToast('error', 'Nao foi possivel salvar o contrato.')
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <p className="text-slate-400">Carregando formulario...</p>

  return (
    <div className="space-y-5">
      <ToastView />
      <div className="flex items-center justify-between gap-3">
        <div>
          <Link to="/contratos" className="text-sm text-emerald-400 hover:underline">
            &larr; Voltar
          </Link>
          <h1 className="mt-2 text-2xl font-semibold">{isEdit ? 'Editar contrato' : 'Novo contrato'}</h1>
        </div>
      </div>

      {!canWrite && (
        <div className="rounded-lg border border-amber-700 bg-amber-950/40 p-3 text-sm text-amber-200">
          Seu perfil permite apenas visualizacao.
        </div>
      )}

      <form onSubmit={onSubmit} className="space-y-5 rounded-lg border border-slate-800 bg-slate-900/80 p-5">
        <div className="grid gap-4 md:grid-cols-3">
          <Field label="Numero" invalid={invalid('numero')}>
            <input className="input" value={form.numero} onChange={(e) => updateField('numero', e.target.value)} />
          </Field>
          <Field label="Orgao" invalid={invalid('orgao')}>
            <input className="input" value={form.orgao} onChange={(e) => updateField('orgao', e.target.value)} />
          </Field>
          <Field label="Status">
            <select className="input" value={form.status} onChange={(e) => updateField('status', e.target.value)}>
              {['ativo', 'alerta', 'critico', 'suspenso', 'encerrado', 'rescindido', 'rascunho'].map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </Field>
        </div>

        <Field label="Objeto" invalid={invalid('objeto')}>
          <textarea
            className="input min-h-24"
            value={form.objeto}
            onChange={(e) => updateField('objeto', e.target.value)}
          />
        </Field>

        <div className="grid gap-4 md:grid-cols-3">
          <Field label="Valor" invalid={invalid('valor')}>
            <input
              className="input"
              type="number"
              min="0"
              step="0.01"
              value={form.valor}
              onChange={(e) => updateField('valor', e.target.value)}
            />
          </Field>
          <Field label="Inicio" invalid={invalid('inicio')}>
            <input className="input" type="date" value={form.inicio} onChange={(e) => updateField('inicio', e.target.value)} />
          </Field>
          <Field label="Termino" invalid={invalid('termino') || (submitted && form.termino < form.inicio)}>
            <input className="input" type="date" value={form.termino} onChange={(e) => updateField('termino', e.target.value)} />
          </Field>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <Field label="Secretaria" invalid={invalid('secretaria_id')}>
            <select
              className="input"
              value={form.secretaria_id}
              onChange={(e) => updateField('secretaria_id', Number(e.target.value))}
              disabled={user?.role === 'gestor'}
            >
              <option value={0}>Selecione</option>
              {secretarias.map((s) => <option key={s.id} value={s.id}>{s.nome}</option>)}
            </select>
          </Field>
          <Field label="Fornecedor" invalid={invalid('fornecedor_id')}>
            <select className="input" value={form.fornecedor_id} onChange={(e) => updateField('fornecedor_id', Number(e.target.value))}>
              <option value={0}>Selecione</option>
              {fornecedores.map((f) => <option key={f.id} value={f.id}>{f.razao_social}</option>)}
            </select>
          </Field>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <Field label="Fiscal">
            <select
              className="input"
              value={form.fiscal_responsavel_id || ''}
              onChange={(e) => updateField('fiscal_responsavel_id', e.target.value ? Number(e.target.value) : null)}
            >
              <option value="">Sem fiscal</option>
              {fiscais.map((u) => <option key={u.id} value={u.id}>{u.nome}</option>)}
            </select>
          </Field>
          <Field label="Gestor">
            <select
              className="input"
              value={form.gestor_responsavel_id || ''}
              onChange={(e) => updateField('gestor_responsavel_id', e.target.value ? Number(e.target.value) : null)}
              disabled={user?.role === 'gestor'}
            >
              <option value="">Sem gestor</option>
              {gestores.map((u) => <option key={u.id} value={u.id}>{u.nome}</option>)}
            </select>
          </Field>
        </div>

        <Field label="Tags">
          <input className="input" value={form.tags || ''} onChange={(e) => updateField('tags', e.target.value)} />
        </Field>

        <div className="flex justify-end gap-2">
          <Button type="button" variant="ghost" onClick={() => navigate(-1)}>
            Cancelar
          </Button>
          <Button type="submit" disabled={saving || !canWrite}>
            {saving ? 'Salvando...' : 'Salvar contrato'}
          </Button>
        </div>
      </form>
    </div>
  )
}

function Field({ label, invalid = false, children }: { label: string; invalid?: boolean; children: React.ReactNode }) {
  return (
    <label className="block text-sm">
      <span className="mb-1 block text-slate-300">{label}</span>
      {children}
      {invalid && <span className="mt-1 block text-xs text-red-300">Campo obrigatorio ou invalido.</span>}
    </label>
  )
}
