import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'
import ConfirmModal from '../components/ui/ConfirmModal'
import { useAuth } from '../hooks/useAuth'
import { useToast } from '../hooks/useToast'
import { deleteContract, fetchContract } from '../services/contracts'
import type { Contract } from '../types'

const labels: Record<keyof Contract, string> = {
  id: 'ID',
  status: 'Status',
  numero_contrato: 'Contrato',
  numero_aditivo: 'Aditivo',
  fornecedor: 'Fornecedor',
  cnpj: 'CNPJ',
  secretaria: 'Secretaria',
  secretario: 'Secretario',
  gestor: 'Gestor',
  gestor_cpf: 'CPF do gestor',
  fiscal: 'Fiscal',
  fiscal_cpf: 'CPF do fiscal',
  objeto: 'Objeto',
  vigencia_texto: 'Vigencia original',
  inicio_vigencia: 'Inicio da vigencia',
  fim_vigencia: 'Fim da vigencia',
  data_os: 'Data OS',
  processo_administrativo: 'Processo administrativo',
  processo_execucao: 'Processo de execucao',
  audesp_licitacao: 'Audesp licitacao',
  audesp_ajuste: 'Audesp ajuste',
  modalidade: 'Modalidade',
  valor_total: 'Valor total',
  data_assinatura: 'Data de assinatura',
  data_publicacao: 'Data de publicacao',
  observacao: 'Observacao',
  dias_para_vencimento: 'Dias para vencimento',
  alerta_30: 'Alerta 30',
  alerta_15: 'Alerta 15',
  alerta_07: 'Alerta 7',
  alerta_01: 'Alerta 1',
  created_at: 'Criado em',
  updated_at: 'Atualizado em',
}

export default function ContratoDetalhe() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { hasRole } = useAuth()
  const { showToast, ToastView } = useToast()
  const [contract, setContract] = useState<Contract | null>(null)
  const [confirmDelete, setConfirmDelete] = useState(false)
  const [deleting, setDeleting] = useState(false)

  useEffect(() => {
    if (id) fetchContract(id).then(setContract)
  }, [id])

  if (!contract) return <p className="text-slate-400">Carregando...</p>

  async function onDelete() {
    if (!contract) return
    setDeleting(true)
    try {
      await deleteContract(contract.id)
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

      <section className="rounded-lg border border-slate-800 bg-slate-900/80 p-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="text-2xl font-semibold">{contract.numero_contrato || 'Contrato'}</h1>
            <Badge label={contract.status || 'sem_status'} />
          </div>
          <div className="flex gap-2">
            {hasRole('admin', 'gestor') && (
              <Button type="button" variant="ghost" onClick={() => showToast('success', 'Edicao manual sera aberta na proxima etapa.')}>
                Editar
              </Button>
            )}
            <Button type="button" variant="ghost" onClick={() => window.print()}>
              Exportar PDF
            </Button>
            {hasRole('admin') && (
              <Button type="button" variant="danger" onClick={() => setConfirmDelete(true)}>
                Excluir
              </Button>
            )}
          </div>
        </div>
        <p className="mt-3 text-slate-300">{contract.objeto}</p>
      </section>

      <section className="grid gap-3 md:grid-cols-2">
        {(Object.keys(labels) as (keyof Contract)[]).map((key) => (
          <div key={key} className="rounded-lg border border-slate-800 bg-slate-900/70 p-4">
            <p className="text-xs uppercase text-slate-500">{labels[key]}</p>
            <p className="mt-1 break-words text-sm text-slate-200">{String(contract[key] ?? '-')}</p>
          </div>
        ))}
      </section>

      <ConfirmModal
        open={confirmDelete}
        title="Excluir contrato"
        message={`Confirma a exclusao do contrato ${contract.numero_contrato || contract.id}?`}
        confirmLabel="Excluir"
        loading={deleting}
        onConfirm={onDelete}
        onClose={() => setConfirmDelete(false)}
      />
    </div>
  )
}
