import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Materials from './pages/Materials'
import MaterialLayout from './pages/MaterialLayout'
import NetworkPage from './pages/NetworkPage'
import FormulasPage from './pages/FormulasPage'
import EvidencePage from './pages/EvidencePage'
import MatchPeaksPage from './pages/MatchPeaksPage'
import TasksPage from './pages/TasksPage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="materials" element={<Materials />} />
          <Route path="tasks" element={<TasksPage />} />
          <Route path="materials/:id" element={<MaterialLayout />}>
            <Route index element={<Navigate to="network" replace />} />
            <Route path="network" element={<NetworkPage />} />
            <Route path="formulas" element={<FormulasPage />} />
            <Route path="evidence" element={<EvidencePage />} />
            <Route path="match-peaks" element={<MatchPeaksPage />} />
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
