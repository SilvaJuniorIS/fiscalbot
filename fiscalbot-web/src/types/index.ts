export type User = {
  id: number
  nome: string
  email: string
  role: string
  secretaria_id?: number | null
}

export type Secretaria = {
  id: number
  nome: string
  sigla?: string | null
}

export type Fornecedor = {
  id: number
  razao_social: string
  cnpj: string
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
  tags?: string | null
  secretaria_id: number
  fornecedor_id: number
  fiscal_responsavel_id?: number | null
  gestor_responsavel_id?: number | null
  secretaria?: { id: number; nome: string }
  fornecedor?: { id: number; razao_social: string; cnpj?: string }
  fiscal?: User | null
  gestor?: User | null
  alertas_ativos?: number
}

export type ContratoPayload = {
  numero: string
  orgao: string
  objeto: string
  valor: string
  inicio: string
  termino: string
  status?: string
  tags?: string | null
  secretaria_id: number
  fornecedor_id: number
  fiscal_responsavel_id?: number | null
  gestor_responsavel_id?: number | null
}

export type ContratoListResult = {
  items: Contrato[]
  total: number
  page: number
  limit: number
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

export type ImportacaoResultado = {
  importados: number
  ignorados: number
  erros: number
  atualizados: number
  total_processado?: number
  linhas_invalidas: { linha: number; erro: string }[]
  detalhes: { linha: number; numero: string; status: string; mensagem: string }[]
}
