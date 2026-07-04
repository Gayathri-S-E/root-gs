/**
 * Farm Detail Page
 * Shows farm info, fields list, soil reports, and AI crop recommendation.
 */
import { useParams, Link } from 'react-router-dom'
import { useState } from 'react'
import { motion } from 'framer-motion'
import { useFarm, useSoilReports, useCreateSoilReport, useCreateField, useCropRecommendation } from '../../api/hooks'

export default function FarmDetailPage() {
  const { id } = useParams<{ id: string }>()
  const farmId = parseInt(id || '0')
  const { data: farm, isLoading } = useFarm(farmId)
  const { data: soilReports } = useSoilReports(farmId)
  const { data: aiRec } = useCropRecommendation(farmId)
  const createSoilReport = useCreateSoilReport()
  const createField = useCreateField()

  const [fieldName, setFieldName] = useState('')
  const [fieldArea, setFieldArea] = useState('')
  const [ph, setPh] = useState('')
  const [nitrogen, setNitrogen] = useState('')
  const [phosphorus, setPhosphorus] = useState('')
  const [potassium, setPotassium] = useState('')

  if (isLoading) return <div className="skeleton" style={{ height: '400px', borderRadius: '16px' }} />
  if (!farm) return <div className="card"><h3>Farm not found</h3><Link to="/farms" className="btn btn-primary">Back to Farms</Link></div>

  const handleAddField = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!fieldName || !fieldArea) return
    await createField.mutateAsync({
      farmId,
      data: { name: fieldName, area_acres: parseFloat(fieldArea) }
    })
    setFieldName('')
    setFieldArea('')
  }

  const handleAddSoilReport = async (e: React.FormEvent) => {
    e.preventDefault()
    await createSoilReport.mutateAsync({
      farmId,
      data: {
        ph: ph ? parseFloat(ph) : undefined,
        nitrogen: nitrogen ? parseFloat(nitrogen) : undefined,
        phosphorus: phosphorus ? parseFloat(phosphorus) : undefined,
        potassium: potassium ? parseFloat(potassium) : undefined,
      }
    })
    setPh('')
    setNitrogen('')
    setPhosphorus('')
    setPotassium('')
  }

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px' }}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
        {/* Farm Info */}
        <motion.div className="card" initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }}>
          <h2 style={{ marginBottom: '12px' }}>🌾 {farm.name}</h2>
          <p style={{ color: 'var(--text-muted)', marginBottom: '16px' }}>{farm.description || 'No description provided.'}</p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
            <div style={{ background: 'var(--bg)', padding: '12px', borderRadius: '8px' }}>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>SIZE</div>
              <div style={{ fontSize: '18px', fontWeight: 700 }}>{farm.total_area_acres} Acres</div>
            </div>
            <div style={{ background: 'var(--bg)', padding: '12px', borderRadius: '8px' }}>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>SOIL TYPE</div>
              <div style={{ fontSize: '18px', fontWeight: 700, textTransform: 'capitalize' }}>{farm.soil_type.replace('_', ' ')}</div>
            </div>
            <div style={{ background: 'var(--bg)', padding: '12px', borderRadius: '8px' }}>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>IRRIGATION</div>
              <div style={{ fontSize: '18px', fontWeight: 700, textTransform: 'capitalize' }}>{farm.irrigation_type}</div>
            </div>
          </div>
        </motion.div>

        {/* Fields */}
        <div className="card">
          <h3 style={{ marginBottom: '16px' }}>📐 Fields & Plots</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '20px' }}>
            {farm.fields?.length === 0 ? (
              <p style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>No fields defined yet.</p>
            ) : (
              farm.fields?.map(field => (
                <div key={field.id} style={{ display: 'flex', justifyContent: 'space-between', padding: '12px', background: 'var(--bg)', borderRadius: '8px', border: '1px solid var(--border)' }}>
                  <div>
                    <span style={{ fontWeight: 600 }}>{field.name}</span>
                    <span style={{ marginLeft: '12px', fontSize: '13px', color: 'var(--text-muted)' }}>{field.area_acres} Acres</span>
                  </div>
                  <span className="badge badge-neutral" style={{ textTransform: 'capitalize' }}>{field.soil_type}</span>
                </div>
              ))
            )}
          </div>
          <form onSubmit={handleAddField} style={{ display: 'flex', gap: '12px' }}>
            <input className="input" placeholder="Field Name (e.g. South Plot)" value={fieldName} onChange={e => setFieldName(e.target.value)} required />
            <input className="input" type="number" step="0.1" placeholder="Size (Acres)" value={fieldArea} onChange={e => setFieldArea(e.target.value)} required style={{ width: '120px' }} />
            <button type="submit" className="btn btn-primary">Add Field</button>
          </form>
        </div>

        {/* Soil Reports */}
        <div className="card">
          <h3 style={{ marginBottom: '16px' }}>🧪 Soil Reports</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '20px' }}>
            {soilReports?.length === 0 ? (
              <p style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>No soil test reports uploaded.</p>
            ) : (
              soilReports?.map(report => (
                <div key={report.id} style={{ padding: '16px', background: 'var(--bg)', borderRadius: '12px', border: '1px solid var(--border)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span style={{ fontWeight: 700, fontSize: '13px' }}>Report #{report.id}</span>
                    <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{new Date(report.created_at).toLocaleDateString()}</span>
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px', marginBottom: '12px' }}>
                    <div><span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>pH: </span><strong>{report.ph || 'N/A'}</strong></div>
                    <div><span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>N: </span><strong>{report.nitrogen || 'N/A'} kg/ha</strong></div>
                    <div><span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>P: </span><strong>{report.phosphorus || 'N/A'} kg/ha</strong></div>
                    <div><span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>K: </span><strong>{report.potassium || 'N/A'} kg/ha</strong></div>
                  </div>
                  {report.ai_recommendation && (
                    <div style={{ background: 'var(--bg-card)', padding: '10px', borderRadius: '8px', borderLeft: '3px solid var(--primary)', fontSize: '13px' }}>
                      <strong>AI Suggestion:</strong> {report.ai_recommendation}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
          <form onSubmit={handleAddSoilReport} style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr) auto', gap: '10px', alignItems: 'center' }}>
            <input className="input" type="number" step="0.1" placeholder="pH" value={ph} onChange={e => setPh(e.target.value)} />
            <input className="input" type="number" placeholder="Nitrogen" value={nitrogen} onChange={e => setNitrogen(e.target.value)} />
            <input className="input" type="number" placeholder="Phosphorus" value={phosphorus} onChange={e => setPhosphorus(e.target.value)} />
            <input className="input" type="number" placeholder="Potassium" value={potassium} onChange={e => setPotassium(e.target.value)} />
            <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>kg/ha</span>
            <button type="submit" className="btn btn-primary">Save Report</button>
          </form>
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
        {/* Health Scores */}
        <div className="card">
          <h3 style={{ marginBottom: '16px' }}>📊 Farm Sustainability</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px', fontSize: '13px' }}>
                <span>Water Efficiency</span>
                <strong>{farm.water_usage_score}%</strong>
              </div>
              <div className="progress-bar"><div className="progress-fill" style={{ width: `${farm.water_usage_score}%` }}></div></div>
            </div>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px', fontSize: '13px' }}>
                <span>Carbon Management</span>
                <strong>{farm.carbon_score}%</strong>
              </div>
              <div className="progress-bar"><div className="progress-fill" style={{ width: `${farm.carbon_score}%` }}></div></div>
            </div>
          </div>
        </div>

        {/* AI Crop Recommendation */}
        <div className="card" style={{ background: 'var(--gradient-hero)', color: 'white', border: 'none' }}>
          <div style={{ fontSize: '32px', marginBottom: '12px' }}>🧠</div>
          <h3 style={{ color: 'white', marginBottom: '8px' }}>AI Crop Doctor Insight</h3>
          {aiRec ? (
            <div>
              <p style={{ color: 'rgba(255,255,255,0.9)', fontWeight: 600, fontSize: '15px', marginBottom: '10px' }}>
                Recommended Crop: {aiRec.recommendation}
              </p>
              <p style={{ color: 'rgba(255,255,255,0.85)', fontSize: '13px', marginBottom: '12px' }}>
                {aiRec.reason}
              </p>
              <div style={{ fontSize: '12px', background: 'rgba(255,255,255,0.15)', padding: '8px', borderRadius: '6px' }}>
                <strong>Evidence:</strong> {aiRec.evidence}
              </div>
            </div>
          ) : (
            <p style={{ color: 'rgba(255,255,255,0.85)', fontSize: '13px' }}>No recommendations generated. Add soil parameters or check back later.</p>
          )}
        </div>
      </div>
    </div>
  )
}
