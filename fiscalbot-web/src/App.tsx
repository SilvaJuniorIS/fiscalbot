import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import Layout from './components/layout/Layout'
import { useAuth } from './hooks/useAuth'
import Alertas from './pages/Alertas'
import ContratoDetalhe from './pages/ContratoDetalhe'
import ContratoForm from './pages/ContratoForm'
import Contratos from './pages/Contratos'
import Dashboard from './pages/Dashboard'
import Fiscalizacao from './pages/Fiscalizacao'
import ImportacaoContratos from './pages/ImportacaoContratos'
import Login from './pages/Login'

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth()
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return <Layout>{children}</Layout>
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/"
          element={
            <PrivateRoute>
              <Dashboard />
            </PrivateRoute>
          }
        />
        <Route
          path="/contratos"
          element={
            <PrivateRoute>
              <Contratos />
            </PrivateRoute>
          }
        />
        <Route
          path="/contratos/novo"
          element={
            <PrivateRoute>
              <ContratoForm />
            </PrivateRoute>
          }
        />
        <Route
          path="/contratos/:id/editar"
          element={
            <PrivateRoute>
              <ContratoForm />
            </PrivateRoute>
          }
        />
        <Route
          path="/contratos/:id"
          element={
            <PrivateRoute>
              <ContratoDetalhe />
            </PrivateRoute>
          }
        />
        <Route
          path="/importacao/contratos"
          element={
            <PrivateRoute>
              <ImportacaoContratos />
            </PrivateRoute>
          }
        />
        <Route
          path="/alertas"
          element={
            <PrivateRoute>
              <Alertas />
            </PrivateRoute>
          }
        />
        <Route
          path="/fiscalizacao"
          element={
            <PrivateRoute>
              <Fiscalizacao />
            </PrivateRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
