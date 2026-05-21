import api from './api'
import type { Alerta, AlertaResumo } from '../types'

export async function fetchAlertas(params?: { lido?: boolean; resolvido?: boolean }) {
  const { data } = await api.get<Alerta[]>('/api/v1/alertas', { params })
  return data
}

export async function fetchResumo() {
  const { data } = await api.get<AlertaResumo>('/api/v1/alertas/resumo')
  return data
}

export async function marcarLido(id: number) {
  await api.put(`/api/v1/alertas/${id}/lido`)
}

export async function resolver(id: number) {
  await api.put(`/api/v1/alertas/${id}/resolver`)
}
