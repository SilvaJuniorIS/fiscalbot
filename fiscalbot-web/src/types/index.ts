export type User = {
  id: number
  nome: string
  email: string
  role: string
  secretaria_id?: number | null
}

export type Contrato = {
  id: number
  numero: string
  orgao: string
  objeto: string
  valor: string
  inicio: string
  termino: string
  status: string
  secretaria?: { id: number; nome: string }
  fornecedor?: { id: number; razao_social: string }
  alertas_ativos?: number
}

export type ContratoDashboard = {
  ativos: number
  vencendo_30: number
  valor_total: string
  em_risco: number
  por_secretaria: { nome: string; total: number }[]
  por_status: { status: string; total: number }[]
}

export type Alerta = {
  id: number
  contrato_id: number
  tipo: string
  titulo: string
  mensagem: string
  data_referencia: string
  status: string
}

export type AlertaResumo = {
  urgentes: number
  atencao: number
  info: number
  total_nao_lidos: number
}

export type Anexo = {
  id: number
  nome_arquivo: string
  tipo: string
  versao: number
  url: string
  created_at: string
}

export type Ocorrencia = {
  id: number
  titulo: string
  descricao: string
  tipo: string | null
  status: string
  data_ocorrencia: string
}

export type FiscalizacaoResumo = {
  vistorias_mes: number
  ocorrencias_abertas: number
  conformes: number
  com_ressalva: number
  com_pendencia: number
}
