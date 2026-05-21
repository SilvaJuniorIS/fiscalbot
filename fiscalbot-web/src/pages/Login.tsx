import { useState } from 'react'
import type { FormEvent } from 'react'
import { Navigate } from 'react-router-dom'
import Button from '../components/ui/Button'
import { useAuth } from '../hooks/useAuth'

export default function Login() {
  const { login, isAuthenticated } = useAuth()
  const [email, setEmail] = useState('admin@fiscalbot.gov.br')
  const [password, setPassword] = useState('fiscalbot123')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  if (isAuthenticated) return <Navigate to="/" replace />

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      await login(email, password)
    } catch {
      setError('Credenciais invalidas')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-950 p-4">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900 p-8 shadow-xl"
      >
        <h1 className="text-2xl font-bold text-emerald-400">FiscalBot</h1>
        <p className="mt-1 text-sm text-slate-400">Gestao e fiscalizacao de contratos publicos</p>
        <div className="mt-6 space-y-3">
          <input
            className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="E-mail"
          />
          <input
            type="password"
            className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Senha"
          />
        </div>
        {error && <p className="mt-2 text-sm text-red-400">{error}</p>}
        <Button type="submit" disabled={loading} className="mt-4 w-full">
          {loading ? 'Entrando...' : 'Entrar'}
        </Button>
        <p className="mt-4 text-center text-xs text-slate-500">
          Demo: admin@fiscalbot.gov.br / fiscalbot123
        </p>
      </form>
    </div>
  )
}
