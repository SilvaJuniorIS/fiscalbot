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
  const [modo, setModo] = useState<'ignorar' | 'atualizar'>('ignorar')

  function selectFile(selected?: File | null) {
    if (uploading) return
    setFile(null)
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
    const preview = !result?.simulacao
    if (!file) {
      showToast('error', 'Selecione uma planilha para importar.')
      return
    }
    setUploading(true)
    setProgress(35)
    try {
      const imported = await importContracts(file, modo, preview)
      setProgress(100)
      setResult(imported)
      showToast('success', preview ? 'Previa pronta. Nenhum dado foi gravado.' : `Concluido: ${imported.importados} novos e ${imported.atualizados} atualizados.`)
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
        <label className="mb-4 block text-sm text-slate-300">
          Ao encontrar um registro existente
          <select className="input mt-2" value={modo} disabled={uploading} onChange={(e) => {
            setModo(e.target.value as 'ignorar' | 'atualizar'); setResult(null); setProgress(0)
          }}>
            <option value="ignorar">Ignorar duplicados (recomendado)</option>
            <option value="atualizar">Atualizar registros identificados com seguranca</option>
          </select>
          <p className="mt-2 text-xs text-slate-400">A atualizacao preserva campos existentes quando a celula esta vazia. Repeticoes ambiguas serao ignoradas.</p>
        </label>
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
            disabled={uploading}
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
            <p className="mt-1 text-xs text-slate-400">{progress === 100 ? (result?.simulacao ? 'Previa pronta; confira antes de confirmar' : 'Concluido') : 'Processando planilha...'}</p>
          </div>
        )}

        <div className="mt-4 flex justify-end">
          <Button type="button" onClick={onSubmit} disabled={uploading || (!!result && !result.simulacao)}>
            {uploading ? 'Processando...' : result?.simulacao ? 'Confirmar importacao das linhas validas' : result ? 'Importacao concluida' : 'Analisar planilha'}
          </Button>
        </div>
      </section>

      {result && (
        <section className="space-y-4">
          <p className="text-sm text-slate-300">{result.simulacao ? 'SIMULACAO: os numeros abaixo mostram o que sera gravado. Confira erros e duplicados.' : 'Importacao concluida.'}</p>
          <div className="grid gap-4 sm:grid-cols-3">
            <Card title={result.simulacao ? 'Novos previstos' : 'Importados'} value={result.importados} />
            <Card title="Atualizados" value={result.atualizados ?? 0} />
            <Card title="Duplicados identificados" value={result.duplicados ?? 0} />
            <Card title="Ignorados" value={result.ignorados} />
            <Card title="Erros" value={result.erros} />
            <Card title="Processadas" value={result.linhas_processadas} />
          </div>
          {result.simulacao && (
            <div className="overflow-x-auto rounded border border-slate-800">
              <p className="p-3 text-sm text-slate-400">Amostra das primeiras 50 linhas validas; totais consideram toda a primeira aba.</p>
              <table className="w-full text-left text-sm"><thead><tr>
                {['Linha', 'Acao', 'Tipo', 'Numero', 'Fornecedor', 'Vencimento'].map(label => <th className="p-2" key={label}>{label}</th>)}
              </tr></thead><tbody>{(result.previa ?? []).map(row => <tr className="border-t border-slate-800" key={row.linha}>
                <td className="p-2">{row.linha}</td><td>{row.acao.replaceAll('_', ' ')}</td><td>{row.tipo}</td><td>{row.numero}</td><td>{row.fornecedor}</td><td>{row.vencimento || 'Sem data'}</td>
              </tr>)}</tbody></table>
            </div>
          )}
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
