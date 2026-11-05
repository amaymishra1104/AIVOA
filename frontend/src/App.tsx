import { Route, Routes } from "react-router-dom"
import { Layout } from "./components/Layout"
import { DashboardView } from "./components/DashboardView"
import { InvestigationsView } from "./components/InvestigationsView"
import { IngestionView } from "./components/IngestionView"
import { Workspace } from "./components/Workspace"
import { CapaView } from "./components/CapaView"
import { EvidenceView } from "./components/EvidenceView"
import { AuditView } from "./components/AuditView"
import { SettingsView } from "./components/SettingsView"

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<DashboardView />} />
        <Route path="/investigations" element={<InvestigationsView />} />
        <Route path="/ingest" element={<IngestionView />} />
        <Route path="/workspace" element={<Workspace />} />
        <Route path="/workspace/:id" element={<Workspace />} />
        <Route path="/i/:id" element={<Workspace />} />
        <Route path="/capa" element={<CapaView />} />
        <Route path="/evidence" element={<EvidenceView />} />
        <Route path="/audit" element={<AuditView />} />
        <Route path="/settings" element={<SettingsView />} />
      </Route>
    </Routes>
  )
}
