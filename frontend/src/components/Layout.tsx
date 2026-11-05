import { useState } from "react"
import { Outlet } from "react-router-dom"
import { Sidebar } from "./Sidebar"
import { TopNav } from "./TopNav"

export function Layout() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)

  return (
    <div className="enterprise-shell">
      <Sidebar
        collapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
      />
      <div className="enterprise-main-column">
        <TopNav />
        <main className="enterprise-content-viewport">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

