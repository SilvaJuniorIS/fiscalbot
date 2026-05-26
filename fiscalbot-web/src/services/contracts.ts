import api from './api'
import type { Contract, ContractDashboard, ContractImportResult, ContractListResult } from '../types'

export async function importContracts(file: File) {
  const form = new FormData()
  form.append('file', file)
  const { data } = await api.post<ContractImportResult>('/api/v1/contracts/import', form)
  return data
}

export async function fetchContracts(params?: Record<string, string | number | boolean | undefined>) {
  const { data } = await api.get<ContractListResult>('/api/v1/contracts', { params })
  return data
}

export async function fetchContractsDashboard() {
  const { data } = await api.get<ContractDashboard>('/api/v1/contracts/dashboard')
  return data
}

export async function fetchContract(id: string) {
  const { data } = await api.get<Contract>(`/api/v1/contracts/${id}`)
  return data
}

export async function updateContract(id: string, payload: Partial<Contract>) {
  const { data } = await api.put<Contract>(`/api/v1/contracts/${id}`, payload)
  return data
}

export async function deleteContract(id: string) {
  await api.delete(`/api/v1/contracts/${id}`)
}

export async function downloadContractsExport(
  format: 'csv' | 'xlsx' | 'pdf',
  params?: Record<string, string | number | boolean | undefined>,
) {
  const { data } = await api.get<Blob>(`/api/v1/contracts/export/${format}`, {
    params,
    responseType: 'blob',
  })
  const url = URL.createObjectURL(data)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = `contratos.${format}`
  anchor.click()
  URL.revokeObjectURL(url)
}
