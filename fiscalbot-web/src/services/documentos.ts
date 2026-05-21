import api from './api'
import type { Anexo } from '../types'

export async function listDocumentos(contratoId: number) {
  const { data } = await api.get<Anexo[]>(`/api/v1/contratos/${contratoId}/documentos`)
  return data
}

export async function uploadDocumento(contratoId: number, file: File, tipo: string) {
  const form = new FormData()
  form.append('file', file)
  form.append('tipo', tipo)
  const { data } = await api.post<Anexo>(`/api/v1/contratos/${contratoId}/documentos`, form)
  return data
}

export function downloadUrl(anexoId: number) {
  const base = import.meta.env.VITE_API_URL || 'http://localhost:8000'
  const token = localStorage.getItem('fiscalbot_token')
  return `${base}/api/v1/documentos/${anexoId}/download?token=${token}`
}
