import api from './api'
import type { ImportacaoResultado } from '../types'

export async function importarContratos(file: File, modo: 'append' | 'overwrite') {
  const form = new FormData()
  form.append('file', file)
  const { data } = await api.post<{ task_id: string; status: string }>(
    '/api/v1/importacao/contratos',
    form,
    { params: { modo } },
  )
  return data
}

export async function fetchImportacaoStatus(taskId: string) {
  const { data } = await api.get<{
    task_id: string
    status: string
    resultado?: ImportacaoResultado
    erro?: string
  }>(`/api/v1/importacao/contratos/${taskId}`)
  return data
}

export async function downloadRelatorio(taskId: string) {
  const response = await api.get(`/api/v1/importacao/contratos/${taskId}/relatorio.csv`, {
    responseType: 'blob',
  })
  const url = URL.createObjectURL(response.data)
  const a = document.createElement('a')
  a.href = url
  a.download = `relatorio_importacao_${taskId}.csv`
  a.click()
  URL.revokeObjectURL(url)
}

export async function downloadTemplate() {
  const response = await api.get('/api/v1/importacao/contratos/template.csv', {
    responseType: 'blob',
  })
  const url = URL.createObjectURL(response.data)
  const a = document.createElement('a')
  a.href = url
  a.download = 'contratos_importacao.csv'
  a.click()
  URL.revokeObjectURL(url)
}
