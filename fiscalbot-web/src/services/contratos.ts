import api from './api'
import type { Contrato, ContratoDashboard } from '../types'

export async function fetchDashboard() {
  const { data } = await api.get<ContratoDashboard>(
    '/api/v1/contratos/dashboard'
  )

  return data
}

export async function fetchContratos(
  params?: Record<string, string | number>
) {
  const { data } = await api.get(
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

export async function fetchContrato(id: number) {
  const { data } = await api.get<Contrato>(
    `/api/v1/contratos/${id}`
  )

  return data
}