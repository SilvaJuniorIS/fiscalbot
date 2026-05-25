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

export type Contract = {
  id: string
  status?: string | null
  numero_contrato?: string | null
  numero_aditivo?: string | null
  fornecedor?: string | null
  cnpj?: string | null
  secretaria?: string | null
  secretario?: string | null
  gestor?: string | null
  gestor_cpf?: string | null
  fiscal?: string | null
  fiscal_cpf?: string | null
  objeto?: string | null
  vigencia_texto?: string | null
  inicio_vigencia?: string | null
  fim_vigencia?: string | null
  data_os?: string | null
  processo_administrativo?: string | null
  processo_execucao?: string | null
  audesp_licitacao?: string | null
  audesp_ajuste?: string | null
  modalidade?: string | null
  valor_total?: string | null
  data_assinatura?: string | null
  data_publicacao?: string | null
  observacao?: string | null
  dias_para_vencimento?: number | null
  alerta_30: boolean
  alerta_15: boolean
  alerta_07: boolean
  alerta_01: boolean
  created_at: string
  updated_at: string
}

export type ContractListResult = {
  items: Contract[]
  total: number
  page: number
  limit: number
  pages: number
}

export type ContractDashboard = {
  contratos_ativos: number
  vencendo_em_30: number
  vencendo_em_15: number
  vencidos: number
  valor_total_contratado: string
}

export type ContractImportResult = {
  importados: number
  ignorados: number
  erros: number
  linhas_processadas: number
  linhas_com_erro: number
  detalhes_erro: { linha: number; erro: string }[]
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
