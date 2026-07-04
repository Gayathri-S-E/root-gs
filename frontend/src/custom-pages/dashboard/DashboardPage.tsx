/**
 * Farmer Dashboard — The main home page
 * Shows: hero banner, weather, farm health, quick actions, AI suggestions, tasks
 */

import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { useAuthStore } from '../../store'
import { useFarms, useWeather, useNotifications, useAnalyticsDashboard } from '../../api/hooks'

const QUICK_ACTIONS = [
  { icon: '🔬', label: 'Scan Crop', path: '/crop-doctor', color: '#E8F5E9', border: '#A5D6A7' },
  { icon: '🤖', label: 'Ask AI', path: '/chatbot', color: '#E3F2FD', border: '#90CAF9' },
  { icon: '💧', label: 'Irrigation', path: '/irrigation', color: '#E8EAF6', border: '#9FA8DA' },
  { icon: '📈', label: 'Market', path: '/market', color: '#FFF8E1', border: '#FFE082' },
  { icon: '🏛️', label: 'Schemes', path: '/schemes', color: '#FCE4EC', border: '#F48FB1' },
  { icon: '📊', label: 'Analytics', path: '/analytics', color: '#F3E5F5', border: '#CE93D8' },
]

function StatCard({ icon, label, value, sub, trend }: {
  icon: string; label: string; value: string; sub?: string; trend?: 'up' | 'down' | 'neutral'
}) {
  return (
    <motion.div
      className="stat-card"
      whileHover={{ y: -3 }}
      transition={{ type: 'spring', stiffness: 400, damping: 30 }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div className="stat-label">{label}</div>
        <div className="stat-icon">{icon}</div>
      </div>
      <div className="stat-value">{value}</div>
      {sub && (
        <div className={`stat-sub ${trend === 'up' ? 'stat-up' : trend === 'down' ? 'stat-down' : ''}`}>
          {trend === 'up' && '↑ '}{trend === 'down' && '↓ '}{sub}
        </div>
      )}
    </motion.div>
  )
}

function SkeletonCard() {
  return <div className="skeleton" style={{ height: '120px', borderRadius: '16px' }} />
}

export default function DashboardPage() {
  const user = useAuthStore(s => s.user)
  const { data: farmsData, isLoading: farmsLoading } = useFarms()
  const { data: analytics } = useAnalyticsDashboard()
  const { data: notifData } = useNotifications()

  // Use default location if no farms with GPS
  const { data: weather } = useWeather(
    farmsData?.data?.[0]?.latitude ?? 13.0827,
    farmsData?.data?.[0]?.longitude ?? 80.2707
  )

  const farms = farmsData?.data ?? []
  const unreadCount = notifData?.unread_count ?? 0
  const totalExpenses = analytics?.total_expenses ?? 0
  const farmCount = analytics?.farm_count ?? 0

  const avgHealth = farms.length > 0
    ? Math.round(farms.reduce((s, f) => s + f.health_score, 0) / farms.length)
    : 0

  const greeting = () => {
    const h = new Date().getHours()
    if (h < 12) return 'Good morning'
    if (h < 17) return 'Good afternoon'
    return 'Good evening'
  }

  return (
    <div>
      {/* Hero Banner */}
      <motion.div
        className="hero-banner"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div style={{ position: 'relative', zIndex: 1 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '20px' }}>
            <div>
              <h1 className="hero-title">
                {greeting()}, {user?.full_name?.split(' ')[0]}! 🌾
              </h1>
              <p className="hero-subtitle">
                Your AI agriculture assistant is ready. Today is a great day to check your crops.
              </p>
            </div>

            {/* Weather Widget */}
            {weather?.current && (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.3 }}
                style={{
                  background: 'rgba(255,255,255,0.15)',
                  backdropFilter: 'blur(10px)',
                  borderRadius: '16px',
                  padding: '16px 24px',
                  border: '1px solid rgba(255,255,255,0.2)',
                  textAlign: 'center',
                  minWidth: '180px',
                }}
              >
                <div style={{ fontSize: '36px' }}>{weather.current.icon}</div>
                <div style={{ fontSize: '2rem', fontWeight: 800, color: 'white', lineHeight: 1 }}>
                  {Math.round(weather.current.temperature)}°C
                </div>
                <div style={{ color: 'rgba(255,255,255,0.75)', fontSize: '13px', marginTop: '4px' }}>
                  {weather.current.description} • {weather.current.humidity}% humidity
                </div>
              </motion.div>
            )}
          </div>

          {/* Weather crop advisory */}
          {weather?.crop_advisory && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
              style={{
                marginTop: '20px',
                background: 'rgba(255,255,255,0.12)',
                borderRadius: '10px',
                padding: '12px 16px',
                fontSize: '14px',
                color: 'rgba(255,255,255,0.9)',
                border: '1px solid rgba(255,255,255,0.15)',
              }}
            >
              🌤️ <strong>Today's Crop Advisory:</strong> {weather.crop_advisory}
            </motion.div>
          )}
        </div>
      </motion.div>

      {/* Stats Row */}
      <div className="grid-4" style={{ marginBottom: '24px' }}>
        {farmsLoading ? (
          Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} />)
        ) : (
          <>
            <StatCard icon="🌾" label="My Farms" value={`${farmCount}`} sub="Active farms" />
            <StatCard icon="💚" label="Farm Health" value={`${avgHealth}%`} sub="Average score" trend={avgHealth > 70 ? 'up' : 'down'} />
            <StatCard icon="💰" label="Total Expenses" value={`₹${totalExpenses.toLocaleString('en-IN')}`} sub="This season" />
            <StatCard icon="🔔" label="Alerts" value={`${unreadCount}`} sub="Unread notifications" trend={unreadCount > 0 ? 'down' : 'neutral'} />
          </>
        )}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '24px' }}>
        {/* Quick Actions */}
        <motion.div className="card" initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.2 }}>
          <h3 style={{ marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            ⚡ Quick Actions
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px' }}>
            {QUICK_ACTIONS.map((action, i) => (
              <Link
                key={i}
                to={action.path}
                style={{
                  display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px',
                  padding: '16px 8px', borderRadius: '12px',
                  background: action.color, border: `1px solid ${action.border}`,
                  textDecoration: 'none', transition: 'all 0.2s',
                }}
                onMouseEnter={e => (e.currentTarget.style.transform = 'translateY(-2px)')}
                onMouseLeave={e => (e.currentTarget.style.transform = 'translateY(0)')}
              >
                <span style={{ fontSize: '28px' }}>{action.icon}</span>
                <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-primary)', textAlign: 'center' }}>
                  {action.label}
                </span>
              </Link>
            ))}
          </div>
        </motion.div>

        {/* AI Assistant CTA */}
        <motion.div
          className="card"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
          style={{ background: 'var(--gradient-dark)', border: 'none', color: 'white', position: 'relative', overflow: 'hidden' }}
        >
          <div style={{
            position: 'absolute', top: '-30px', right: '-30px',
            width: '150px', height: '150px', borderRadius: '50%',
            background: 'rgba(102,187,106,0.15)',
          }} />
          <div style={{ position: 'relative', zIndex: 1 }}>
            <div style={{ fontSize: '40px', marginBottom: '12px' }}>🤖</div>
            <h3 style={{ color: 'white', marginBottom: '8px' }}>Ask ROOTGS AI</h3>
            <p style={{ color: 'rgba(255,255,255,0.7)', fontSize: '14px', marginBottom: '20px' }}>
              Get expert advice on crops, diseases, weather, and more. Available 24/7 in English & Tamil.
            </p>
            <Link to="/chatbot" className="btn btn-primary" style={{ display: 'inline-flex' }}>
              Start Conversation →
            </Link>
          </div>
        </motion.div>
      </div>

      {/* My Farms */}
      <motion.div className="card" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h3>🌾 My Farms</h3>
          <Link to="/farms/new" className="btn btn-primary btn-sm">+ Add Farm</Link>
        </div>

        {farmsLoading ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {[1, 2].map(i => <div key={i} className="skeleton" style={{ height: '70px', borderRadius: '12px' }} />)}
          </div>
        ) : farms.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
            <div style={{ fontSize: '48px', marginBottom: '12px' }}>🌱</div>
            <p>You haven't added any farms yet.</p>
            <Link to="/farms/new" className="btn btn-primary" style={{ marginTop: '16px', display: 'inline-flex' }}>
              Add Your First Farm
            </Link>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {farms.slice(0, 3).map(farm => (
              <Link
                key={farm.id}
                to={`/farms/${farm.id}`}
                style={{
                  display: 'flex', alignItems: 'center', gap: '16px',
                  padding: '16px', borderRadius: '12px',
                  background: 'var(--bg)', border: '1px solid var(--border)',
                  textDecoration: 'none', transition: 'all 0.2s',
                }}
                onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--primary)'; e.currentTarget.style.background = 'var(--primary-glow)'; }}
                onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border)'; e.currentTarget.style.background = 'var(--bg)'; }}
              >
                <div style={{ width: '48px', height: '48px', borderRadius: '12px', background: 'var(--primary-glow)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '24px', flexShrink: 0 }}>🌾</div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 700, color: 'var(--text-primary)', marginBottom: '4px' }}>{farm.name}</div>
                  <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
                    {farm.total_area_acres} acres • {farm.soil_type} soil • {farm.district}, {farm.state}
                  </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '18px', fontWeight: 800, color: farm.health_score > 70 ? 'var(--success)' : 'var(--warning)' }}>
                    {farm.health_score}%
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Health</div>
                </div>
              </Link>
            ))}
            {farms.length > 3 && (
              <Link to="/farms" style={{ textAlign: 'center', color: 'var(--primary)', fontSize: '14px', fontWeight: 600 }}>
                View all {farms.length} farms →
              </Link>
            )}
          </div>
        )}
      </motion.div>

      {/* Weather Forecast */}
      {weather?.forecast && (
        <motion.div className="card" style={{ marginTop: '24px' }} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5 }}>
          <h3 style={{ marginBottom: '16px' }}>🌤️ 7-Day Forecast</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: '8px', overflowX: 'auto' }}>
            {weather.forecast.map((day, i) => (
              <div key={i} style={{
                textAlign: 'center', padding: '12px 8px',
                borderRadius: '12px',
                background: i === 0 ? 'var(--primary-glow)' : 'var(--bg)',
                border: `1px solid ${i === 0 ? 'var(--primary)' : 'var(--border)'}`,
                minWidth: '80px',
              }}>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>
                  {i === 0 ? 'Today' : new Date(day.date).toLocaleDateString('en-IN', { weekday: 'short' })}
                </div>
                <div style={{ fontSize: '22px', margin: '6px 0' }}>
                  {day.weather_code >= 95 ? '⛈️' : day.precipitation_sum > 5 ? '🌧️' : day.weather_code <= 1 ? '☀️' : '⛅'}
                </div>
                <div style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text-primary)' }}>{Math.round(day.temp_max)}°</div>
                <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{Math.round(day.temp_min)}°</div>
                {day.precipitation_sum > 0 && (
                  <div style={{ fontSize: '10px', color: '#0277BD', marginTop: '2px' }}>💧{Math.round(day.precipitation_sum)}mm</div>
                )}
              </div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  )
}
