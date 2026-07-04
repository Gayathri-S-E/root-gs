/** Farm List Page */
import { useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useFarms, useDeleteFarm } from '../../api/hooks'
import type { Farm } from '../../types'

export default function FarmListPage() {
  const [search, setSearch] = useState('')
  const { data, isLoading } = useFarms({ search: search || undefined })
  const deleteFarm = useDeleteFarm()
  const farms = data?.data ?? []

  return (
    <div>
      <div className="page-header">
        <div className="page-header-left">
          <h1 className="page-title">🌾 My Farms</h1>
          <p className="page-subtitle">{farms.length} farm(s) registered</p>
        </div>
        <Link to="/farms/new" id="add-farm-btn" className="btn btn-primary btn-lg">+ Add New Farm</Link>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <input className="input" placeholder="🔍 Search farms by name..." value={search} onChange={e => setSearch(e.target.value)} id="farm-search" style={{ maxWidth: '400px' }} />
      </div>

      {isLoading ? (
        <div className="grid-3">
          {Array.from({ length: 6 }).map((_, i) => <div key={i} className="skeleton" style={{ height: '200px', borderRadius: '16px' }} />)}
        </div>
      ) : farms.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '80px' }}>
          <div style={{ fontSize: '64px', marginBottom: '16px' }}>🌱</div>
          <h3 style={{ marginBottom: '8px' }}>No farms yet</h3>
          <p style={{ color: 'var(--text-muted)', marginBottom: '24px' }}>Start by adding your first farm to get AI recommendations.</p>
          <Link to="/farms/new" className="btn btn-primary btn-lg">Add Your First Farm</Link>
        </div>
      ) : (
        <div className="grid-3">
          {farms.map((farm: Farm, i) => (
            <motion.div key={farm.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }} className="card" style={{ cursor: 'pointer', padding: '0', overflow: 'hidden' }}>
              {/* Cover */}
              <div style={{ height: '100px', background: 'var(--gradient-hero)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '40px', position: 'relative' }}>
                🌾
                <div style={{ position: 'absolute', top: '12px', right: '12px' }}>
                  <span className={`badge ${farm.health_score > 70 ? 'badge-success' : 'badge-warning'}`}>
                    💚 {farm.health_score}% Health
                  </span>
                </div>
              </div>
              <div style={{ padding: '16px' }}>
                <h4 style={{ marginBottom: '6px' }}>{farm.name}</h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', marginBottom: '16px' }}>
                  <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>📍 {farm.district}, {farm.state}</div>
                  <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>📐 {farm.total_area_acres} acres • {farm.soil_type} soil</div>
                  <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>💧 {farm.irrigation_type} irrigation</div>
                </div>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <Link to={`/farms/${farm.id}`} className="btn btn-primary btn-sm" style={{ flex: 1, textAlign: 'center' }}>View Details</Link>
                  <button className="btn btn-secondary btn-sm" onClick={() => deleteFarm.mutate(farm.id)} style={{ color: 'var(--danger)' }}>🗑️</button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  )
}
