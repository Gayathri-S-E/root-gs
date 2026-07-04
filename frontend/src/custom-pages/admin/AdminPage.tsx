/**
 * Admin Panel Dashboard
 */
import { useQuery } from '@tanstack/react-query'
import { adminAPI } from '../../api'

export default function AdminPage() {
  const { data: stats } = useQuery({ queryKey: ['admin-stats'], queryFn: () => adminAPI.stats().then(r => r.data.data) })
  const { data: users } = useQuery({ queryKey: ['admin-users'], queryFn: () => adminAPI.listUsers().then(r => r.data.data) })

  return (
    <div>
      <div className="page-header">
        <div className="page-header-left">
          <h1 className="page-title">⚙️ Admin Control Panel</h1>
          <p className="page-subtitle">ROOTGS platform monitoring and user moderation dashboard</p>
        </div>
      </div>

      <div className="grid-3" style={{ marginBottom: '24px' }}>
        <div className="card">
          <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>TOTAL REGISTERED USERS</div>
          <div style={{ fontSize: '2.5rem', fontWeight: 800 }}>{(stats as any)?.total_users || 0}</div>
        </div>
        <div className="card">
          <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>ACTIVE FARMS</div>
          <div style={{ fontSize: '2.5rem', fontWeight: 800 }}>{(stats as any)?.total_farms || 0}</div>
        </div>
        <div className="card">
          <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>AI DISEASE REPORTS</div>
          <div style={{ fontSize: '2.5rem', fontWeight: 800 }}>{(stats as any)?.total_disease_reports || 0}</div>
        </div>
      </div>

      <div className="card">
        <h3 style={{ marginBottom: '16px' }}>👥 User Directory Management</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {(users as any)?.map((u: any) => (
            <div key={u.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px', background: 'var(--bg)', borderRadius: '8px', border: '1px solid var(--border)' }}>
              <div>
                <span style={{ fontWeight: 700 }}>{u.full_name}</span>
                <span style={{ marginLeft: '12px', fontSize: '12px', color: 'var(--text-muted)' }}>{u.email}</span>
                <span className="badge badge-primary" style={{ marginLeft: '12px', textTransform: 'capitalize' }}>{u.role}</span>
              </div>
              <span className={`badge ${u.is_active ? 'badge-success' : 'badge-danger'}`}>
                {u.is_active ? 'Active' : 'Banned'}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
