import api from './api'
import type {
  Contrato,
  ContratoDashboard,
  ContratoListResult,
  ContratoPayload,
  Fornecedor,
  Secretaria,
  User,
} from '../types'

export async function fetchDashboard() {
  const { data } = await api.get<ContratoDashboard>(
    '/api/v1/contratos/dashboard'
  )

  return data
}

export async function fetchContratos(
  params?: Record<string, string | number | undefined>
): Promise<Contrato[]> {
  const { data } = await api.get<Contrato[] | { items: Contrato[] }>(
    '/api/v1/contratos',
    { params }
  )

  // Compatibilidade:
  // backend paginado OU lista simples

  if (Array.isArray(data)) {
    return data
  }

  if (data.items) {
    return data.items
  }

  return []
}

export async function fetchContratosPage(
  params?: Record<string, string | number | undefined>
): Promise<ContratoListResult> {
  const page = Number(params?.page || 1)
  const limit = Number(params?.limit || 20)
  const { data, headers } = await api.get<Contrato[] | { items: Contrato[]; total: number }>(
    '/api/v1/contratos',
    { params: { ...params, formato: 'lista' } }
  )
  const items = Array.isArray(data) ? data : data.items
  return {
    items,
    total: Number(headers['x-total-count'] || (Array.isArray(data) ? data.length : data.total || 0)),
    page,
    limit,
  }
}

export async function fetchContrato(id: number) {
  const { data } = await api.get<Contrato>(
    `/api/v1/contratos/${id}`
  )

  return data
}

export async function createContrato(payload: ContratoPayload) {
  const { data } = await api.post<Contrato>('/api/v1/contratos', payload)
  return data
}

export async function updateContrato(id: number, payload: Partial<ContratoPayload>) {
  const { data } = await api.put<Contrato>(`/api/v1/contratos/${id}`, payload)
  return data
}

export async function deleteContrato(id: number) {
  await api.delete(`/api/v1/contratos/${id}`)
}

export async function fetchSecretarias() {
  const { data } = await api.get<Secretaria[]>('/api/v1/secretarias', {
    params: { limit: 100, is_active: true },
  })
  return data
}

export async function fetchFornecedores() {
  const { data } = await api.get<Fornecedor[]>('/api/v1/fornecedores', {
    params: { limit: 100, is_active: true },
  })
  return data
}

export async function fetchUsuarios(params?: Record<string, string | number>) {
  const { data } = await api.get<User[]>('/api/v1/users', { params: { limit: 100, ...params } })
  return data
}
