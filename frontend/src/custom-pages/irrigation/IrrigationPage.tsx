/**
 * Smart Irrigation Page
 */
import { useState } from 'react'
import { useFarms, useIrrigationSchedule } from '../../api/hooks'
import type { IrrigationSchedule } from '../../types'

export default function IrrigationPage() {
  const { data: farmsData } = useFarms()
  const farms = farmsData?.data ?? []

  const [selectedFarmId, setSelectedFarmId] = useState<number | null>(null)
  const [cropName, setCropName] = useState('')
  const [stage, setStage] = useState('growing')
  const [lastDays, setLastDays] = useState('0')
  const [schedule, setSchedule] = useState<IrrigationSchedule | null>(null)

  const irrigationMutation = useIrrigationSchedule()

  const handleCalculate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedFarmId || !cropName) return

    const farm = farms.find(f => f.id === selectedFarmId)
    if (!farm) return

    const result = await irrigationMutation.mutateAsync({
      farm_id: selectedFarmId,
      crop_name: cropName,
      area_acres: farm.total_area_acres,
      soil_type: farm.soil_type,
      current_stage: stage,
      last_irrigation_days: parseInt(lastDays),
    })

    if (result) setSchedule(result)
  }

  return (
    <div>
      <div className="page-header">
        <div className="page-header-left">
          <h1 className="page-title">💧 Smart Irrigation Planner</h1>
          <p className="page-subtitle">AI-calculated crop water demands and optimized scheduling</p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.5fr', gap: '24px' }}>
        {/* Input Details */}
        <div className="card">
          <h3 style={{ marginBottom: '16px' }}>💧 Calculator</h3>
          <form onSubmit={handleCalculate} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div className="form-group">
              <label className="form-label">Select Farm</label>
              <select
                className="input"
                value={selectedFarmId ?? ''}
                onChange={e => setSelectedFarmId(parseInt(e.target.value))}
                required
                id="irrigation-farm"
              >
                <option value="" disabled>Choose a farm...</option>
                {farms.map(f => (
                  <option key={f.id} value={f.id}>{f.name} ({f.total_area_acres} Acres)</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Crop Name</label>
              <input
                className="input"
                placeholder="e.g. Rice, Wheat, Tomato"
                value={cropName}
                onChange={e => setCropName(e.target.value)}
                required
                id="irrigation-crop"
              />
            </div>

            <div className="form-group">
              <label className="form-label">Current Growth Stage</label>
              <select className="input" value={stage} onChange={e => setStage(e.target.value)} id="irrigation-stage">
                <option value="sowing">Sowing / Initial</option>
                <option value="vegetative">Vegetative (Growing)</option>
                <option value="flowering">Flowering</option>
                <option value="harvesting">Harvesting Stage</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Days since last watering</label>
              <input
                type="number"
                className="input"
                value={lastDays}
                onChange={e => setLastDays(e.target.value)}
                required
                id="irrigation-days"
              />
            </div>

            <button type="submit" id="irrigation-submit" className="btn btn-primary btn-lg" disabled={irrigationMutation.isPending}>
              {irrigationMutation.isPending ? 'Calculating...' : '💧 Generate Schedule'}
            </button>
          </form>
        </div>

        {/* Schedule Output */}
        <div>
          {schedule ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
              {/* Score and recommendations */}
              <div className="card" style={{ background: 'var(--gradient-hero)', color: 'white', border: 'none' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                  <h3 style={{ color: 'white', margin: 0 }}>Smart Irrigation Recommendation</h3>
                  <div style={{ background: 'rgba(255,255,255,0.2)', padding: '6px 12px', borderRadius: '20px', fontSize: '13px', fontWeight: 600 }}>
                    Water Saving Score: {schedule.water_saving_score}/100
                  </div>
                </div>
                <div style={{ fontSize: '15px', lineHeight: 1.6, marginBottom: '16px' }}>
                  {schedule.reason}
                </div>
                <div style={{ background: 'rgba(255,255,255,0.15)', padding: '12px', borderRadius: '8px' }}>
                  🚿 <strong>Water Needed today:</strong> {schedule.recommended ? `${schedule.water_required_liters.toLocaleString()} Liters` : 'No watering required today.'}
                </div>
              </div>

              {/* 7-Day Action Plan */}
              <div className="card">
                <h3 style={{ marginBottom: '16px' }}>📅 7-Day Watering Timeline</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  {schedule.daily_schedule?.map((day, idx) => (
                    <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px', background: day.irrigate ? 'var(--primary-glow)' : 'var(--bg)', borderRadius: '8px', border: `1px solid ${day.irrigate ? 'var(--primary)' : 'var(--border)'}` }}>
                      <div>
                        <span style={{ fontWeight: 600 }}>{new Date(day.date).toLocaleDateString('en-IN', { weekday: 'long', month: 'short', day: 'numeric' })}</span>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        {day.irrigate ? (
                          <>
                            <span className="badge badge-primary">💧 Irrigate</span>
                            <span style={{ fontSize: '13px', fontWeight: 600 }}>{day.water_liters.toLocaleString()} L</span>
                          </>
                        ) : (
                          <span className="badge badge-neutral">☀️ Dry</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Water saving tips */}
              <div className="card">
                <h3 style={{ marginBottom: '12px' }}>💡 Efficiency Tips</h3>
                <ul style={{ paddingLeft: '20px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {schedule.water_saving_tips?.map((tip, idx) => (
                    <li key={idx} style={{ color: 'var(--text-secondary)' }}>{tip}</li>
                  ))}
                </ul>
              </div>
            </div>
          ) : (
            <div className="card" style={{ textAlign: 'center', padding: '60px' }}>
              <div style={{ fontSize: '64px', marginBottom: '16px' }}>💧</div>
              <h3>Water Calculator Output</h3>
              <p style={{ color: 'var(--text-muted)' }}>Fill in the details on the left and submit to view personalized crop water cycles.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
