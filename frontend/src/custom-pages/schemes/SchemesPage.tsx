/**
 * Government Schemes Page
 */
import { useState } from 'react'
import { useSchemes, useMe } from '../../api/hooks'
import { schemeAPI } from '../../api'
import toast from 'react-hot-toast'

export default function SchemesPage() {
  const [search, setSearch] = useState('')
  const { data: schemes, isLoading } = useSchemes({ search: search || undefined })
  const { data: user } = useMe()

  const [checkingSchemeId, setCheckingSchemeId] = useState<number | null>(null)
  const [eligibilityResult, setEligibilityResult] = useState<any | null>(null)

  const handleCheckEligibility = async (schemeId: number) => {
    if (!user || !user.farmer_profile) {
      toast.error('Please complete your farmer profile first')
      return
    }

    setCheckingSchemeId(schemeId)
    setEligibilityResult(null)
    try {
      const res = await schemeAPI.checkEligibility({
        scheme_id: schemeId,
        farmer_state: user.farmer_profile.state || 'Tamil Nadu',
        land_acres: user.farmer_profile.total_land_acres || 2.5,
      })
      setEligibilityResult(res.data.data)
    } catch {
      toast.error('Failed to analyze eligibility')
    } finally {
      setCheckingSchemeId(null)
    }
  }

  return (
    <div>
      <div className="page-header">
        <div className="page-header-left">
          <h1 className="page-title">🏛️ Government Schemes</h1>
          <p className="page-subtitle">Eligibility analyzer and documents guide for Indian government schemes</p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '24px' }}>
        {/* Schemes List */}
        <div className="card">
          <h3 style={{ marginBottom: '16px' }}>📜 Available Schemes</h3>
          <div style={{ marginBottom: '16px' }}>
            <input
              className="input"
              placeholder="🔍 Search schemes (e.g. Kisan Samman, PM-FBY)..."
              value={search}
              onChange={e => setSearch(e.target.value)}
              id="scheme-search"
            />
          </div>

          {isLoading ? (
            <div className="skeleton" style={{ height: '300px', borderRadius: '12px' }} />
          ) : schemes && schemes.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {schemes.map(scheme => (
                <div key={scheme.id} style={{ padding: '16px', background: 'var(--bg)', borderRadius: '12px', border: '1px solid var(--border)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                    <h4 style={{ margin: 0 }}>{scheme.name}</h4>
                    <span className="badge badge-primary">{scheme.category}</span>
                  </div>
                  <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '12px' }}>{scheme.description}</p>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>🏛️ {scheme.authority}</span>
                    <button
                      className="btn btn-secondary btn-sm"
                      onClick={() => handleCheckEligibility(scheme.id)}
                      disabled={checkingSchemeId === scheme.id}
                    >
                      {checkingSchemeId === scheme.id ? 'Checking...' : 'Check Eligibility 📝'}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '20px' }}>No schemes found.</p>
          )}
        </div>

        {/* Eligibility Checker Result */}
        <div>
          {eligibilityResult ? (
            <div className="card animate-fade-in" style={{ border: `2px solid ${eligibilityResult.eligible ? 'var(--success)' : 'var(--danger)'}` }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
                <span style={{ fontSize: '32px' }}>{eligibilityResult.eligible ? '✅' : '❌'}</span>
                <div>
                  <h3 style={{ margin: 0 }}>{eligibilityResult.eligible ? 'Eligible' : 'Not Eligible'}</h3>
                  <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{eligibilityResult.scheme_name}</span>
                </div>
              </div>

              {eligibilityResult.reasons && eligibilityResult.reasons.length > 0 && (
                <div style={{ marginBottom: '16px' }}>
                  <h4 style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '6px' }}>REASONS / CRITERIA</h4>
                  <ul style={{ paddingLeft: '20px', fontSize: '13px', color: 'var(--text-secondary)' }}>
                    {eligibilityResult.reasons.map((reason: string, idx: number) => (
                      <li key={idx}>{reason}</li>
                    ))}
                  </ul>
                </div>
              )}

              <div style={{ padding: '12px', borderRadius: '8px', background: 'var(--bg)', fontSize: '13px' }}>
                <strong>Next Steps:</strong> {eligibilityResult.next_steps}
              </div>
            </div>
          ) : (
            <div className="card" style={{ textAlign: 'center', padding: '60px' }}>
              <div style={{ fontSize: '64px', marginBottom: '16px' }}>🏛️</div>
              <h3>Eligibility Advisor</h3>
              <p style={{ color: 'var(--text-muted)' }}>
                Click "Check Eligibility" on any scheme to analyze matching requirements against your farmer profile parameters.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
