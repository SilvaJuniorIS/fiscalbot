import { useState } from 'react'
import Button from '../components/ui/Button'
import Card from '../components/ui/Card'
import { useToast } from '../hooks/useToast'
import { importContracts } from '../services/contracts'
import type { ContractImportResult } from '../types'

export default function ImportacaoContratos() {
  const { showToast, ToastView } = useToast()
  const [file, setFile] = useState<File | null>(null)
  const [dragging, setDragging] = useState(false)
  const [progress, setProgress] = useState(0)
  const [result, setResult] = useState<ContractImportResult | null>(null)
  const [uploading, setUploading] = useState(false)

  function selectFile(selected?: File | null) {
    setResult(null)
    setProgress(0)
    if (!selected) {
      setFile(null)
      return
    }
    if (!/\.(xls|xlsx)$/i.test(selected.name)) {
      showToast('error', 'Selecione uma planilha .xls ou .xlsx.')
      return
    }
    setFile(selected)
  }

  async function onSubmit() {
    if (!file) {
      showToast('error', 'Selecione uma planilha para importar.')
      return
    }
    setUploading(true)
    setProgress(35)
    try {
      const imported = await importContracts(file)
      setProgress(100)
      setResult(imported)
      showToast('success', `Importacao concluida: ${imported.importados} contratos importados.`)
    } catch {
      setProgress(0)
      showToast('error', 'Nao foi possivel importar a planilha.')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="space-y-6">
      <ToastView />
      <div>
        <h1 className="text-2xl font-semibold">Importar Planilha</h1>
        <p className="text-sm text-slate-400">Envie arquivos XLS ou XLSX para limpar, padronizar e registrar contratos.</p>
      </div>

      <section className="rounded-lg border border-slate-800 bg-slate-900/80 p-5">
        <div
          className={`flex min-h-48 cursor-pointer flex-col items-center justify-center rounded-lg border border-dashed p-6 text-center transition ${
            dragging ? 'border-emerald-400 bg-emerald-950/20' : 'border-slate-600 bg-slate-950'
          }`}
          onDragOver={(event) => {
            event.preventDefault()
            setDragging(true)
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={(event) => {
            event.preventDefault()
            setDragging(false)
            selectFile(event.dataTransfer.files?.[0])
          }}
        >
          <input
            id="contracts-upload"
            type="file"
            accept=".xls,.xlsx"
            className="hidden"
            onChange={(event) => selectFile(event.target.files?.[0])}
          />
          <label htmlFor="contracts-upload" className="cursor-pointer text-emerald-300">
            {file ? file.name : 'Arraste a planilha aqui ou clique para selecionar'}
          </label>
          <p className="mt-2 text-xs text-slate-500">A importacao remove acentos, quebras, duplicacoes de cabecalho e linhas de secao.</p>
        </div>

        {progress > 0 && (
          <div className="mt-4">
            <div className="h-2 overflow-hidden rounded bg-slate-800">
              <div className="h-full bg-emerald-500 transition-all" style={{ width: `${progress}%` }} />
            </div>
            <p className="mt-1 text-xs text-slate-400">{progress === 100 ? 'Concluido' : 'Processando planilha...'}</p>
          </div>
        )}

        <div className="mt-4 flex justify-end">
          <Button type="button" onClick={onSubmit} disabled={uploading}>
            {uploading ? 'Importando...' : 'Importar'}
          </Button>
        </div>
      </section>

      {result && (
        <section className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-4">
            <Card title="Importados" value={result.importados} />
            <Card title="Ignorados" value={result.ignorados} />
            <Card title="Erros" value={result.erros} />
            <Card title="Processadas" value={result.linhas_processadas} />
          </div>
          <div className="rounded-lg border border-slate-800 bg-slate-900/80 p-4">
            <h2 className="text-sm font-medium text-slate-300">Erros e linhas ignoradas</h2>
            <ul className="mt-3 space-y-2 text-sm text-slate-400">
              {result.detalhes_erro.slice(0, 30).map((item) => (
                <li key={`${item.linha}-${item.erro}`}>Linha {item.linha}: {item.erro}</li>
              ))}
              {result.detalhes_erro.length === 0 && <li>{result.ignorados} linhas ignoradas sem erro.</li>}
            </ul>
          </div>
        </section>
      )}
    </div>
  )
}
