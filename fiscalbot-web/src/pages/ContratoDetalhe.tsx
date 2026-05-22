import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import api from '../services/api'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'
import ConfirmModal from '../components/ui/ConfirmModal'
import { deleteContrato, fetchContrato } from '../services/contratos'
import { listDocumentos, uploadDocumento } from '../services/documentos'
import { useAuth } from '../hooks/useAuth'
import { useToast } from '../hooks/useToast'
import type { Anexo, Contrato, Ocorrencia } from '../types'

export default function ContratoDetalhe() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { hasRole } = useAuth()
  const { showToast, ToastView } = useToast()
  const contratoId = Number(id)
  const [contrato, setContrato] = useState<Contrato | null>(null)
  const [docs, setDocs] = useState<Anexo[]>([])
  const [ocorrencias, setOcorrencias] = useState<Ocorrencia[]>([])
  const [file, setFile] = useState<File | null>(null)
  const [tipo, setTipo] = useState('contrato')
  const [confirmDelete, setConfirmDelete] = useState(false)
  const [deleting, setDeleting] = useState(false)

  async function load() {
    const [c, d, o] = await Promise.all([
      fetchContrato(contratoId),
      listDocumentos(contratoId),
      api.get<Ocorrencia[]>(`/api/v1/fiscalizacao/contratos/${contratoId}/ocorrencias`),
    ])
    setContrato(c)
    setDocs(d)
    setOcorrencias(o.data)
  }

  useEffect(() => {
    if (contratoId) load()
  }, [contratoId])

  async function onUpload(e: FormEvent) {
    e.preventDefault()
    if (!file) return
    await uploadDocumento(contratoId, file, tipo)
    setFile(null)
    load()
  }

  if (!contrato) return <p className="text-slate-400">Carregando...</p>

  async function onDelete() {
    setDeleting(true)
    try {
      await deleteContrato(contratoId)
      showToast('success', 'Contrato excluido.')
      navigate('/contratos')
    } catch {
      showToast('error', 'Nao foi possivel excluir o contrato.')
      setDeleting(false)
      setConfirmDelete(false)
    }
  }

  return (
    <div className="space-y-6">
      <ToastView />
      <Link to="/contratos" className="text-sm text-emerald-400 hover:underline">
        &larr; Voltar
      </Link>
      <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-semibold">{contrato.numero}</h1>
            <Badge label={contrato.status} />
          </div>
          <div className="flex gap-2">
            {hasRole('admin', 'gestor') && (
              <Link to={`/contratos/${contrato.id}/editar`}>
                <Button type="button" variant="ghost">Editar</Button>
              </Link>
            )}
            {hasRole('admin') && (
              <Button type="button" variant="danger" onClick={() => setConfirmDelete(true)}>
                Excluir
              </Button>
            )}
          </div>
        </div>
        <p className="mt-2 text-slate-300">{contrato.objeto}</p>
        <div className="mt-4 grid gap-2 text-sm sm:grid-cols-2">
          <p>
            <span className="text-slate-500">Orgao:</span> {contrato.orgao}
          </p>
          <p>
            <span className="text-slate-500">Valor:</span>{' '}
            {Number(contrato.valor).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
          </p>
          <p>
            <span className="text-slate-500">Vigencia:</span> {contrato.inicio} - {contrato.termino}
          </p>
          <p>
            <span className="text-slate-500">Secretaria:</span> {contrato.secretaria?.nome}
          </p>
          <p>
            <span className="text-slate-500">Fornecedor:</span> {contrato.fornecedor?.razao_social}
          </p>
          <p>
            <span className="text-slate-500">Alertas ativos:</span> {contrato.alertas_ativos ?? 0}
          </p>
        </div>
      </div>

      <section className="rounded-xl border border-slate-800 bg-slate-900/80 p-4">
        <h2 className="mb-3 font-medium">Documentos</h2>
        <form onSubmit={onUpload} className="mb-4 flex flex-wrap gap-2">
          <input type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} />
          <select
            className="rounded border border-slate-700 bg-slate-950 px-2 py-1 text-sm"
            value={tipo}
            onChange={(e) => setTipo(e.target.value)}
          >
            <option value="contrato">contrato</option>
            <option value="aditivo">aditivo</option>
            <option value="nota_fiscal">nota_fiscal</option>
            <option value="relatorio">relatorio</option>
          </select>
          <Button type="submit">Enviar</Button>
        </form>
        <ul className="space-y-2 text-sm">
          {docs.map((d) => (
            <li key={d.id} className="flex justify-between border-t border-slate-800 py-2">
              <span>
                {d.nome_arquivo} <Badge label={d.tipo} />
              </span>
              <button
                type="button"
                className="text-emerald-400 hover:underline"
                onClick={async () => {
                  const res = await api.get(`/api/v1/documentos/${d.id}/download`, {
                    responseType: 'blob',
                  })
                  const url = URL.createObjectURL(res.data)
                  const a = document.createElement('a')
                  a.href = url
                  a.download = d.nome_arquivo
                  a.click()
                  URL.revokeObjectURL(url)
                }}
              >
                Download
              </button>
            </li>
          ))}
        </ul>
      </section>

      <section className="rounded-xl border border-slate-800 bg-slate-900/80 p-4">
        <h2 className="mb-3 font-medium">Ocorrencias</h2>
        <ul className="space-y-2 text-sm">
          {ocorrencias.map((o) => (
            <li key={o.id} className="border-t border-slate-800 py-2">
              <div className="flex gap-2">
                <Badge label={o.status} />
                {o.tipo && <Badge label={o.tipo} />}
              </div>
              <p className="font-medium">{o.titulo}</p>
              <p className="text-slate-400">{o.descricao}</p>
            </li>
          ))}
          {ocorrencias.length === 0 && <p className="text-slate-500">Nenhuma ocorrencia registrada.</p>}
        </ul>
      </section>

      <ConfirmModal
        open={confirmDelete}
        title="Excluir contrato"
        message={`Confirma a exclusao do contrato ${contrato.numero}? Essa acao nao pode ser desfeita.`}
        confirmLabel="Excluir"
        loading={deleting}
        onConfirm={onDelete}
        onClose={() => setConfirmDelete(false)}
      />
    </div>
  )
}
