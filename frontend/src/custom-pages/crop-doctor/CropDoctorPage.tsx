/**
 * Crop Doctor Page — AI Disease Detection
 */

import { useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useDropzone } from 'react-dropzone'
import { useDetectDisease, useDiseaseHistory } from '../../api/hooks'
import type { DiseaseReport, DiseaseSeverity } from '../../types'

const SEVERITY_CONFIG: Record<DiseaseSeverity, { color: string; label: string; bg: string }> = {
  none:     { color: '#2E7D32', label: '✅ Healthy', bg: '#E8F5E9' },
  mild:     { color: '#558B2F', label: '🟡 Mild', bg: '#F9FBE7' },
  moderate: { color: '#E65100', label: '🟠 Moderate', bg: '#FFF3E0' },
  severe:   { color: '#B71C1C', label: '🔴 Severe', bg: '#FFEBEE' },
  critical: { color: '#880E4F', label: '☠️ Critical', bg: '#FCE4EC' },
}

function ConfidenceBar({ score }: { score: number }) {
  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
        <span style={{ fontSize: '13px', fontWeight: 600 }}>AI Confidence</span>
        <span style={{ fontSize: '13px', fontWeight: 700, color: score > 0.75 ? 'var(--success)' : 'var(--warning)' }}>
          {Math.round(score * 100)}%
        </span>
      </div>
      <div className="progress-bar">
        <motion.div
          className="progress-fill"
          initial={{ width: 0 }}
          animate={{ width: `${score * 100}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
          style={{ background: score > 0.75 ? 'var(--gradient-primary)' : 'linear-gradient(135deg, #F57F17, #E65100)' }}
        />
      </div>
    </div>
  )
}

function TreatmentCard({ title, items, icon }: { title: string; items: any[]; icon: string }) {
  if (!items || items.length === 0) return null
  return (
    <div>
      <h4 style={{ marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
        {icon} {title}
      </h4>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {items.map((item, i) => (
          <div key={i} style={{ padding: '12px', borderRadius: '10px', background: 'var(--bg)', border: '1px solid var(--border)' }}>
            <div style={{ fontWeight: 600, marginBottom: '4px' }}>{item.name}</div>
            {item.dosage && <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>💊 Dosage: {item.dosage}</div>}
            {item.frequency && <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>⏰ Frequency: {item.frequency}</div>}
            {item.notes && <div style={{ fontSize: '13px', color: 'var(--text-muted)', fontStyle: 'italic', marginTop: '4px' }}>📝 {item.notes}</div>}
          </div>
        ))}
      </div>
    </div>
  )
}

export default function CropDoctorPage() {
  const [preview, setPreview] = useState<string | null>(null)
  const [file, setFile] = useState<File | null>(null)
  const [result, setResult] = useState<DiseaseReport | null>(null)
  const [cropHint, setCropHint] = useState('')

  const detectMutation = useDetectDisease()
  const { data: history } = useDiseaseHistory({ page: 1 })

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const f = acceptedFiles[0]
    if (!f) return
    setFile(f)
    setPreview(URL.createObjectURL(f))
    setResult(null)
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'image/*': ['.jpg', '.jpeg', '.png', '.webp'] },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024,
  })

  const handleAnalyze = async () => {
    if (!file) return
    const formData = new FormData()
    formData.append('image', file)
    if (cropHint) formData.append('crop_hint', cropHint)

    const res = await detectMutation.mutateAsync(formData)
    if (res) setResult(res)
  }

  const sev = result ? SEVERITY_CONFIG[result.severity] : null

  return (
    <div>
      <div className="page-header">
        <div className="page-header-left">
          <h1 className="page-title">🔬 Crop Doctor</h1>
          <p className="page-subtitle">AI-powered disease detection — upload a photo, get instant diagnosis</p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
        {/* Upload Section */}
        <div>
          <div className="card">
            {/* Dropzone */}
            <div
              {...getRootProps()}
              className={`upload-zone ${isDragActive ? 'drag-over' : ''}`}
              style={{ cursor: 'pointer' }}
            >
              <input {...getInputProps()} id="disease-image-upload" />
              {preview ? (
                <div>
                  <img src={preview} alt="Preview" style={{ maxHeight: '240px', borderRadius: '12px', objectFit: 'contain', maxWidth: '100%' }} />
                  <p style={{ marginTop: '12px', color: 'var(--text-muted)', fontSize: '13px' }}>Click or drag to change image</p>
                </div>
              ) : (
                <div>
                  <div style={{ fontSize: '48px', marginBottom: '16px' }}>📷</div>
                  <h3 style={{ marginBottom: '8px' }}>
                    {isDragActive ? 'Drop your image here!' : 'Upload Crop Image'}
                  </h3>
                  <p style={{ color: 'var(--text-muted)', fontSize: '14px' }}>
                    Drag & drop or click to select<br />
                    <span style={{ fontSize: '12px' }}>JPG, PNG, WebP • Max 10MB</span>
                  </p>
                </div>
              )}
            </div>

            {/* Crop hint */}
            <div className="form-group" style={{ marginTop: '16px' }}>
              <label className="form-label">Crop Type (Optional — improves accuracy)</label>
              <input
                value={cropHint}
                onChange={e => setCropHint(e.target.value)}
                className="input"
                placeholder="e.g., Rice, Tomato, Wheat..."
                id="crop-hint"
              />
            </div>

            <button
              id="analyze-btn"
              className="btn btn-primary btn-lg"
              style={{ width: '100%', marginTop: '16px' }}
              disabled={!file || detectMutation.isPending}
              onClick={handleAnalyze}
            >
              {detectMutation.isPending ? (
                <><div className="spinner" style={{ width: '18px', height: '18px', borderWidth: '2px' }} /> Analyzing with AI...</>
              ) : (
                '🔬 Analyze Disease'
              )}
            </button>
          </div>

          {/* History */}
          {history?.data && history.data.length > 0 && (
            <div className="card" style={{ marginTop: '16px' }}>
              <h4 style={{ marginBottom: '12px' }}>📋 Recent Analyses</h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {history.data.slice(0, 5).map((r: any) => (
                  <div key={r.id || r.report_id} style={{
                    display: 'flex', gap: '12px', alignItems: 'center',
                    padding: '10px', borderRadius: '10px', background: 'var(--bg)',
                    border: '1px solid var(--border)',
                  }}>
                    <img src={r.image_url} alt="" style={{ width: '44px', height: '44px', borderRadius: '8px', objectFit: 'cover' }} />
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontWeight: 600, fontSize: '13px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {r.disease_name || 'Analysis'}
                      </div>
                      <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{r.crop_name}</div>
                    </div>
                    <span className={`badge ${r.severity === 'none' ? 'badge-success' : r.severity === 'severe' || r.severity === 'critical' ? 'badge-danger' : 'badge-warning'}`}>
                      {r.severity}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Results Section */}
        <div>
          <AnimatePresence mode="wait">
            {detectMutation.isPending && (
              <motion.div key="loading" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="card" style={{ textAlign: 'center', padding: '60px' }}>
                <div style={{ fontSize: '48px', marginBottom: '16px' }}>🔬</div>
                <h3 style={{ marginBottom: '8px' }}>AI Analysis in Progress...</h3>
                <p style={{ color: 'var(--text-muted)', marginBottom: '24px' }}>Our AI is examining your crop image</p>
                <div style={{ display: 'flex', gap: '8px', justifyContent: 'center' }}>
                  {['Scanning image', 'Detecting patterns', 'Generating treatment plan'].map((step, i) => (
                    <motion.div key={i} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.5 }}
                      style={{ padding: '6px 12px', borderRadius: '9999px', background: 'var(--primary-glow)', border: '1px solid var(--border-dark)', fontSize: '12px', fontWeight: 600, color: 'var(--primary)' }}>
                      {step}
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            )}

            {result && !detectMutation.isPending && (
              <motion.div key="result" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="card">
                {/* Header */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '20px', padding: '16px', borderRadius: '12px', background: sev?.bg }}>
                  <div style={{ fontSize: '32px' }}>
                    {result.severity === 'none' ? '✅' : result.severity === 'critical' ? '🚨' : '⚠️'}
                  </div>
                  <div>
                    <h3 style={{ color: sev?.color, margin: 0 }}>{result.disease_name || 'Analysis Complete'}</h3>
                    {result.disease_scientific_name && (
                      <p style={{ fontSize: '13px', color: 'var(--text-muted)', fontStyle: 'italic', margin: 0 }}>
                        {result.disease_scientific_name}
                      </p>
                    )}
                    <div style={{ marginTop: '4px' }}>
                      <span className={`badge ${result.severity === 'none' ? 'badge-success' : result.severity === 'severe' || result.severity === 'critical' ? 'badge-danger' : 'badge-warning'}`}>
                        {sev?.label}
                      </span>
                      {result.crop_name && <span className="badge badge-neutral" style={{ marginLeft: '6px' }}>{result.crop_name}</span>}
                    </div>
                  </div>
                </div>

                <ConfidenceBar score={result.confidence_score} />

                {/* Explainable AI */}
                {result.description && (
                  <div style={{ marginTop: '20px', padding: '16px', borderRadius: '12px', background: 'var(--bg)', border: '1px solid var(--border)' }}>
                    <h4 style={{ marginBottom: '8px' }}>🧠 AI Explanation</h4>
                    <p style={{ fontSize: '14px', lineHeight: 1.6, color: 'var(--text-secondary)', margin: 0 }}>{result.description}</p>
                    {result.reason && (
                      <div style={{ marginTop: '10px', padding: '10px', borderRadius: '8px', background: 'rgba(46,125,50,0.05)', borderLeft: '3px solid var(--primary)' }}>
                        <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--primary)', marginBottom: '4px' }}>WHY THIS DIAGNOSIS</div>
                        <p style={{ fontSize: '13px', color: 'var(--text-secondary)', margin: 0 }}>{result.reason}</p>
                      </div>
                    )}
                    {result.evidence && (
                      <div style={{ marginTop: '8px', fontSize: '12px', color: 'var(--text-muted)', display: 'flex', gap: '6px', alignItems: 'flex-start' }}>
                        <span>🔍</span>
                        <span><strong>Evidence:</strong> {result.evidence}</span>
                      </div>
                    )}
                  </div>
                )}

                {/* Treatments */}
                <div style={{ marginTop: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  <TreatmentCard title="Chemical Treatment" items={result.chemical_treatment ?? []} icon="💊" />
                  <TreatmentCard title="Organic Alternatives" items={result.organic_treatment ?? []} icon="🌿" />

                  {result.prevention_tips && result.prevention_tips.length > 0 && (
                    <div>
                      <h4 style={{ marginBottom: '10px' }}>🛡️ Prevention Tips</h4>
                      <ul style={{ paddingLeft: '20px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                        {result.prevention_tips.map((tip, i) => (
                          <li key={i} style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>{tip}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>

                {/* Meta */}
                <div style={{ marginTop: '16px', padding: '12px', borderRadius: '10px', background: 'var(--bg)', fontSize: '12px', color: 'var(--text-muted)', display: 'flex', gap: '16px' }}>
                  <span>⚡ {result.processing_time_ms}ms</span>
                  <span>🤖 {result.ai_model_used}</span>
                  {result.affected_area_percent && <span>📐 {result.affected_area_percent}% affected</span>}
                </div>
              </motion.div>
            )}

            {!result && !detectMutation.isPending && (
              <motion.div key="placeholder" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="card" style={{ textAlign: 'center', padding: '60px' }}>
                <div style={{ fontSize: '64px', marginBottom: '16px' }}>🌿</div>
                <h3 style={{ marginBottom: '8px', color: 'var(--text-muted)' }}>Ready to Diagnose</h3>
                <p style={{ color: 'var(--text-muted)', fontSize: '14px' }}>
                  Upload a photo of your crop to get instant AI disease detection with treatment recommendations.
                </p>
                <div style={{ marginTop: '24px', display: 'flex', gap: '12px', justifyContent: 'center', flexWrap: 'wrap' }}>
                  {['Rice Blast', 'Tomato Blight', 'Wheat Rust', 'Leaf Spot'].map(d => (
                    <span key={d} className="badge badge-neutral">{d}</span>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  )
}
