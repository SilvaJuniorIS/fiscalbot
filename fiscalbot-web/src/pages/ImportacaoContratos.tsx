import { useEffect, useState } from 'react'
import Button from '../components/ui/Button'
import Card from '../components/ui/Card'
import { downloadRelatorio, downloadTemplate, fetchImportacaoStatus, importarContratos } from '../services/importacao'
import { useToast } from '../hooks/useToast'
import type { ImportacaoResultado } from '../types'

export default function ImportacaoContratos() {
  const { showToast, ToastView } = useToast()
  const [file, setFile] = useState<File | null>(null)
  const [modo, setModo] = useState<'append' | 'overwrite'>('append')
  const [taskId, setTaskId] = useState('')
  const [status, setStatus] = useState('')
  const [resultado, setResultado] = useState<ImportacaoResultado | null>(null)
  const [preview, setPreview] = useState<string[][]>([])
  const [uploading, setUploading] = useState(false)

  useEffect(() => {
    if (!taskId || resultado) return
    const timer = window.setInterval(async () => {
      const current = await fetchImportacaoStatus(taskId)
      setStatus(current.status)
      if (current.erro) {
        showToast('error', current.erro)
        window.clearInterval(timer)
        return
      }
      if (current.resultado) {
        setResultado(current.resultado)
        setStatus('success')
        window.clearInterval(timer)
      }
    }, 1800)
    return () => window.clearInterval(timer)
  }, [taskId, resultado])

  async function onFile(selected: File | null) {
    setFile(selected)
    setPreview([])
    setResultado(null)
    setTaskId('')
    if (!selected) return
    if (selected.name.endsWith('.csv')) {
      const text = await selected.text()
      setPreview(text.split(/\r?\n/).filter(Boolean).slice(0, 6).map((line) => line.split(',')))
    }
  }

  async function onSubmit() {
    if (!file) {
      showToast('error', 'Selecione um arquivo .csv ou .xlsx.')
      return
    }
    setUploading(true)
    try {
      const task = await importarContratos(file, modo)
      setTaskId(task.task_id)
      setStatus(task.status)
      showToast('success', 'Importacao enviada para processamento.')
    } catch {
      showToast('error', 'Nao foi possivel iniciar a importacao.')
    } finally {
      setUploading(false)
    }
  }

  const progress = resultado ? 100 : taskId ? 65 : uploading ? 35 : 0

  return (
    <div className="space-y-6">
      <ToastView />
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">Importar contratos</h1>
          <p className="text-sm text-slate-400">Envie CSV ou Excel e acompanhe o processamento em segundo plano.</p>
        </div>
        <Button variant="ghost" onClick={downloadTemplate}>Baixar template</Button>
      </div>

      <section className="rounded-lg border border-slate-800 bg-slate-900/80 p-5">
        <div
          className="flex min-h-40 cursor-pointer flex-col items-center justify-center rounded-lg border border-dashed border-slate-600 bg-slate-950 p-6 text-center"
          onDragOver={(e) => e.preventDefault()}
          onDrop={(e) => {
            e.preventDefault()
            onFile(e.dataTransfer.files?.[0] || null)
          }}
        >
          <input
            id="arquivo-importacao"
            type="file"
            accept=".csv,.xlsx"
            className="hidden"
            onChange={(e) => onFile(e.target.files?.[0] || null)}
          />
          <label htmlFor="arquivo-importacao" className="cursor-pointer text-emerald-300">
            {file ? file.name : 'Arraste o arquivo aqui ou clique para selecionar'}
          </label>
          <p className="mt-2 text-xs text-slate-500">Colunas: numero, orgao, objeto, valor, inicio, termino, secretaria, fornecedor, cnpj.</p>
        </div>

        <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
          <select className="input max-w-xs" value={modo} onChange={(e) => setModo(e.target.value as 'append' | 'overwrite')}>
            <option value="append">Append: ignorar duplicados</option>
            <option value="overwrite">Overwrite: atualizar duplicados</option>
          </select>
          <Button onClick={onSubmit} disabled={uploading || Boolean(taskId && !resultado)}>
            {uploading ? 'Enviando...' : 'Importar contratos'}
          </Button>
        </div>

        {progress > 0 && (
          <div className="mt-4">
            <div className="h-2 overflow-hidden rounded bg-slate-800">
              <div className="h-full bg-emerald-500 transition-all" style={{ width: `${progress}%` }} />
            </div>
            <p className="mt-1 text-xs text-slate-400">Status: {status || 'aguardando'}</p>
          </div>
        )}
      </section>

      {preview.length > 0 && (
        <section className="overflow-x-auto rounded-lg border border-slate-800 bg-slate-900/80 p-4">
          <h2 className="mb-3 text-sm font-medium text-slate-300">Preview</h2>
          <table className="w-full text-xs">
            <tbody>
              {preview.map((row, i) => (
                <tr key={i} className="border-t border-slate-800">
                  {row.map((cell, j) => <td key={j} className="whitespace-nowrap px-3 py-2">{cell}</td>)}
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}

      {resultado && (
        <section className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-4">
            <Card title="Importados" value={resultado.importados} />
            <Card title="Atualizados" value={resultado.atualizados} />
            <Card title="Ignorados" value={resultado.ignorados} />
            <Card title="Erros" value={resultado.erros} />
          </div>
          <div className="rounded-lg border border-slate-800 bg-slate-900/80 p-4">
            <div className="flex items-center justify-between gap-3">
              <h2 className="text-sm font-medium text-slate-300">Linhas invalidas</h2>
              <Button variant="ghost" onClick={() => downloadRelatorio(taskId)}>Baixar relatorio CSV</Button>
            </div>
            <ul className="mt-3 space-y-2 text-sm text-slate-400">
              {resultado.linhas_invalidas.slice(0, 20).map((item) => (
                <li key={`${item.linha}-${item.erro}`}>Linha {item.linha}: {item.erro}</li>
              ))}
              {resultado.linhas_invalidas.length === 0 && <li>Nenhuma linha invalida.</li>}
            </ul>
          </div>
        </section>
      )}
    </div>
  )
}
