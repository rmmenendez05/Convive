import { Navigate, Route, Routes } from 'react-router'
import Layout from './components/Layout'
import RutaProtegida, { SoloVisitantes } from './components/RutaProtegida'
import { AuthProvider } from './context/AuthContext'
import { LangProvider } from './context/LangContext'
import Bienvenida from './pages/Bienvenida'
import Login from './pages/Login'
import Piso from './pages/Piso'
import Registro from './pages/Registro'

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<SoloVisitantes><Login /></SoloVisitantes>} />
      <Route path="/registro" element={<SoloVisitantes><Registro /></SoloVisitantes>} />
      <Route path="/bienvenida" element={<RutaProtegida sinPiso><Bienvenida /></RutaProtegida>} />
      <Route path="/piso" element={<RutaProtegida conPiso><Piso /></RutaProtegida>} />
      <Route path="*" element={<RutaProtegida conPiso><Navigate to="/piso" replace /></RutaProtegida>} />
    </Routes>
  )
}

export default function App() {
  return (
    <LangProvider>
      <AuthProvider>
        <Layout>
          <AppRoutes />
        </Layout>
      </AuthProvider>
    </LangProvider>
  )
}
