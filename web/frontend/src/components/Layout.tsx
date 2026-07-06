import { Outlet, NavLink } from 'react-router-dom'
import { FlaskConical, LayoutDashboard, Beaker, Activity } from 'lucide-react'

export default function Layout() {
  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className="w-56 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <h1 className="text-sm font-bold text-gray-800 flex items-center gap-2">
            <FlaskConical size={18} className="text-blue-600" />
            TOF-SIMS Network
          </h1>
          <p className="text-xs text-gray-400 mt-1">Formula Network v3.0</p>
        </div>
        <nav className="flex-1 p-3 space-y-1">
          <NavLink
            to="/"
            end
            className={({ isActive }) =>
              `flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
                isActive ? 'bg-blue-50 text-blue-700 font-medium' : 'text-gray-600 hover:bg-gray-100'
              }`
            }
          >
            <LayoutDashboard size={16} />
            Dashboard
          </NavLink>
          <NavLink
            to="/materials"
            className={({ isActive }) =>
              `flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
                isActive ? 'bg-blue-50 text-blue-700 font-medium' : 'text-gray-600 hover:bg-gray-100'
              }`
            }
          >
            <Beaker size={16} />
            Materials
          </NavLink>
        </nav>
        <div className="p-3 border-t border-gray-200 text-xs text-gray-400">
          v0.3.0
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto">
        <div className="p-6">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
