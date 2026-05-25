import { Link } from 'react-router-dom'
import hero from '../assets/hero.png'

const metrics = [
  ['42', 'contratos importados'],
  ['9', 'vencendo em 30 dias'],
  ['R$ 8,4 mi', 'valor contratado'],
]

const rows = [
  ['18/23', 'Espaco 2 Tecnologia', 'Administracao', '5 dias', 'critico'],
  ['12/24', 'LECASA Participacoes', 'Saude', '310 dias', 'ativo'],
  ['07/25', 'Servicos Urbanos RGS', 'Obras', '24 dias', 'alerta'],
]

export default function Vitrine() {
  return (
    <main className="min-h-screen bg-[#07120f] text-slate-100">
      <section className="relative overflow-hidden border-b border-emerald-900/50">
        <img
          src={hero}
          alt=""
          className="pointer-events-none absolute right-6 top-6 hidden h-52 opacity-30 lg:block"
        />
        <div className="mx-auto grid min-h-[86vh] max-w-7xl gap-10 px-6 py-8 lg:grid-cols-[0.9fr_1.1fr] lg:items-center">
          <div className="max-w-2xl">
            <p className="text-sm font-medium uppercase tracking-[0.22em] text-emerald-300">
              FiscalBot
            </p>
            <h1 className="mt-4 max-w-3xl text-5xl font-semibold leading-tight text-white md:text-7xl">
              Gestao de Contratos
            </h1>
            <p className="mt-5 max-w-xl text-lg leading-8 text-slate-300">
              Importe planilhas XLS/XLSX, normalize dados fiscais, acompanhe vencimentos e gere
              uma visao executiva dos contratos publicos em poucos cliques.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link
                to="/login"
                className="rounded-lg bg-emerald-500 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-emerald-400"
              >
                Acessar demo
              </Link>
              <a
                href="#modulos"
                className="rounded-lg border border-slate-600 px-5 py-3 text-sm font-semibold text-slate-100 transition hover:border-emerald-400 hover:text-emerald-200"
              >
                Ver recursos
              </a>
            </div>
          </div>

          <div className="relative">
            <div className="rounded-lg border border-emerald-800/70 bg-slate-950 shadow-2xl shadow-emerald-950/70">
              <div className="flex items-center justify-between border-b border-slate-800 px-5 py-4">
                <div>
                  <p className="text-xs uppercase text-slate-500">Painel</p>
                  <p className="font-semibold text-white">Contratos monitorados</p>
                </div>
                <span className="rounded-full bg-emerald-950 px-3 py-1 text-xs text-emerald-200">
                  Online
                </span>
              </div>
              <div className="grid gap-3 p-5 sm:grid-cols-3">
                {metrics.map(([value, label]) => (
                  <div key={label} className="rounded-lg border border-slate-800 bg-slate-900 p-4">
                    <p className="text-2xl font-semibold text-emerald-300">{value}</p>
                    <p className="mt-1 text-xs text-slate-400">{label}</p>
                  </div>
                ))}
              </div>
              <div className="px-5 pb-5">
                <div className="overflow-hidden rounded-lg border border-slate-800">
                  <table className="w-full text-left text-sm">
                    <thead className="bg-slate-900 text-xs uppercase text-slate-500">
                      <tr>
                        <th className="px-4 py-3">Contrato</th>
                        <th className="px-4 py-3">Fornecedor</th>
                        <th className="px-4 py-3">Secretaria</th>
                        <th className="px-4 py-3">Prazo</th>
                        <th className="px-4 py-3">Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {rows.map(([numero, fornecedor, secretaria, prazo, status]) => (
                        <tr key={numero} className="border-t border-slate-800">
                          <td className="px-4 py-3 text-emerald-300">{numero}</td>
                          <td className="px-4 py-3 text-slate-300">{fornecedor}</td>
                          <td className="px-4 py-3 text-slate-400">{secretaria}</td>
                          <td className="px-4 py-3 text-slate-300">{prazo}</td>
                          <td className="px-4 py-3">
                            <span className="rounded-full bg-slate-800 px-2 py-1 text-xs text-slate-200">
                              {status}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="modulos" className="mx-auto max-w-7xl px-6 py-14">
        <div className="grid gap-4 md:grid-cols-3">
          {[
            ['Importacao inteligente', 'Limpeza de cabecalhos, datas, moeda, CPF, CNPJ e periodo de vigencia.'],
            ['Alertas de vencimento', 'Controle de 30, 15, 7 e 1 dia para reduzir renovacoes esquecidas.'],
            ['Dashboard executivo', 'Cards, filtros e tabela priorizada por risco para tomada de decisao.'],
          ].map(([title, text]) => (
            <article key={title} className="rounded-lg border border-slate-800 bg-slate-950 p-5">
              <h2 className="text-lg font-semibold text-white">{title}</h2>
              <p className="mt-2 text-sm leading-6 text-slate-400">{text}</p>
            </article>
          ))}
        </div>
      </section>
    </main>
  )
}
