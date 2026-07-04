/**
 * AppLayout — Sidebar + Topbar wrapper for all authenticated pages
 */

import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useAuthStore, useAppStore } from '../../store'
import { useNotifications } from '../../api/hooks'

const NAV_ITEMS = [
  { label: 'Dashboard',     path: '/dashboard',   icon: '🏠', section: 'main' },
  { label: 'My Farms',      path: '/farms',        icon: '🌾', section: 'main' },
  { label: 'Crop Doctor',   path: '/crop-doctor',  icon: '🔬', section: 'ai', badge: 'AI' },
  { label: 'AI Chatbot',    path: '/chatbot',      icon: '🤖', section: 'ai', badge: 'AI' },
  { label: 'Weather',       path: '/weather',      icon: '🌤️', section: 'tools' },
  { label: 'Irrigation',    path: '/irrigation',   icon: '💧', section: 'tools' },
  { label: 'Market',        path: '/market',       icon: '📈', section: 'tools' },
  { label: 'Gov. Schemes',  path: '/schemes',      icon: '🏛️', section: 'tools' },
  { label: 'Analytics',     path: '/analytics',    icon: '📊', section: 'insights' },
]

const SECTIONS: Record<string, string> = {
  main:     'Main',
  ai:       'AI Features',
  tools:    'Farm Tools',
  insights: 'Insights',
}

export default function AppLayout() {
  const user = useAuthStore(s => s.user)
  const logout = useAuthStore(s => s.logout)
  const toggleTheme = useAppStore(s => s.toggleTheme)
  const theme = useAppStore(s => s.theme)
  const navigate = useNavigate()

  const { data: notifData } = useNotifications()
  const unreadCount = notifData?.unread_count ?? 0

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const initials = user?.full_name?.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2) || 'U'

  // Group nav items by section
  const sections = Array.from(new Set(NAV_ITEMS.map(n => n.section)))

  return (
    <div className="app-layout">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-logo">
          <div className="sidebar-logo-icon">🌱</div>
          <div>
            <div className="sidebar-logo-text">ROOTGS</div>
            <div className="sidebar-logo-sub">AI AGRICULTURE OS</div>
          </div>
        </div>

        <nav className="sidebar-nav">
          {sections.map(section => (
            <div key={section}>
              <div className="sidebar-section-label">{SECTIONS[section]}</div>
              {NAV_ITEMS.filter(n => n.section === section).map(item => (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
                >
                  <span className="nav-item-icon">{item.icon}</span>
                  <span style={{ flex: 1 }}>{item.label}</span>
                  {item.badge && (
                    <span style={{ fontSize: '10px', background: 'rgba(102,187,106,0.2)', color: 'var(--secondary)', padding: '1px 6px', borderRadius: '9999px', fontWeight: 700 }}>
                      {item.badge}
                    </span>
                  )}
                </NavLink>
              ))}
            </div>
          ))}
        </nav>

        <div className="sidebar-footer">
          <NavLink to="/profile" className="sidebar-avatar">{initials}</NavLink>
          <div style={{ flex: 1, overflow: 'hidden' }}>
            <div style={{ fontSize: '13px', fontWeight: 600, color: 'white', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {user?.full_name}
            </div>
            <div style={{ fontSize: '11px', color: 'rgba(102,187,106,0.7)', textTransform: 'capitalize' }}>
              {user?.role?.replace('_', ' ')}
            </div>
          </div>
          <button className="btn btn-ghost btn-icon" onClick={toggleTheme} title="Toggle theme" style={{ color: 'rgba(255,255,255,0.5)', padding: '6px' }}>
            {theme === 'light' ? '🌙' : '☀️'}
          </button>
          <button className="btn btn-ghost btn-icon" onClick={handleLogout} title="Logout" style={{ color: 'rgba(255,255,255,0.5)', padding: '6px' }}>
            🚪
          </button>
        </div>
      </aside>

      {/* Topbar */}
      <header className="topbar">
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          <span className="topbar-title">
            {NAV_ITEMS.find(n => window.location.pathname.startsWith(n.path))?.label || 'ROOTGS'}
          </span>
          <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
            {new Date().toLocaleDateString('en-IN', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
          </span>
        </div>

        <div className="topbar-right">
          {/* Notification Bell */}
          <NavLink to="/dashboard" style={{ position: 'relative', display: 'flex', padding: '8px' }}>
            <span style={{ fontSize: '20px' }}>🔔</span>
            {unreadCount > 0 && (
              <span className="nav-badge" style={{ position: 'absolute', top: '2px', right: '2px', fontSize: '9px', padding: '1px 4px' }}>
                {unreadCount}
              </span>
            )}
          </NavLink>

          {/* User Avatar */}
          <NavLink to="/profile" className="sidebar-avatar" style={{ width: '36px', height: '36px' }}>
            {initials}
          </NavLink>
        </div>
      </header>

      {/* Main Content */}
      <main className="main-content">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, ease: 'easeOut' }}
          key={window.location.pathname}
        >
          <Outlet />
        </motion.div>
      </main>
    </div>
  )
}
