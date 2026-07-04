/**
 * Weather Intelligence Page
 */
import { useState } from 'react'
import { useFarms, useFarmWeather } from '../../api/hooks'

export default function WeatherPage() {
  const { data: farmsData } = useFarms()
  const farms = farmsData?.data ?? []
  const [selectedFarmId, setSelectedFarmId] = useState<number | null>(null)

  // Auto select first farm
  if (selectedFarmId === null && farms.length > 0) {
    setSelectedFarmId(farms[0].id)
  }

  const { data: weather, isLoading } = useFarmWeather(selectedFarmId ?? undefined)

  return (
    <div>
      <div className="page-header">
        <div className="page-header-left">
          <h1 className="page-title">🌤️ Weather Intelligence</h1>
          <p className="page-subtitle">Real-time localized forecasts and agricultural crop advisories</p>
        </div>
      </div>

      <div className="card" style={{ marginBottom: '24px' }}>
        <label className="form-label" style={{ marginBottom: '8px', display: 'block' }}>Select Farm to view weather forecast</label>
        <select
          className="input"
          value={selectedFarmId ?? ''}
          onChange={e => setSelectedFarmId(parseInt(e.target.value))}
          style={{ maxWidth: '300px' }}
        >
          <option value="" disabled>Choose a farm...</option>
          {farms.map(f => (
            <option key={f.id} value={f.id}>{f.name}</option>
          ))}
        </select>
      </div>

      {isLoading ? (
        <div className="skeleton" style={{ height: '300px', borderRadius: '16px' }} />
      ) : weather ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {/* Current weather and Crop Advisory */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '24px' }}>
            <div className="card" style={{ background: 'var(--gradient-hero)', color: 'white', border: 'none', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', textAlign: 'center' }}>
              <div style={{ fontSize: '64px' }}>{weather.current.icon}</div>
              <div style={{ fontSize: '3rem', fontWeight: 800 }}>{Math.round(weather.current.temperature)}°C</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 600, opacity: 0.9 }}>{weather.current.description}</div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', width: '100%', marginTop: '20px', borderTop: '1px solid rgba(255,255,255,0.2)', paddingTop: '16px' }}>
                <div>
                  <div style={{ fontSize: '11px', opacity: 0.7 }}>HUMIDITY</div>
                  <div style={{ fontSize: '15px', fontWeight: 700 }}>{weather.current.humidity}%</div>
                </div>
                <div>
                  <div style={{ fontSize: '11px', opacity: 0.7 }}>WIND</div>
                  <div style={{ fontSize: '15px', fontWeight: 700 }}>{weather.current.wind_speed} km/h</div>
                </div>
              </div>
            </div>

            <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
              <h3 style={{ marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>🤖 Farm Advisor Alert</h3>
              <p style={{ fontSize: '15px', lineHeight: 1.6, color: 'var(--text-secondary)' }}>
                {weather.crop_advisory}
              </p>
              {weather.alerts && weather.alerts.length > 0 && (
                <div className="alert alert-danger" style={{ marginTop: '16px' }}>
                  <strong>Alert:</strong> {weather.alerts.join(', ')}
                </div>
              )}
            </div>
          </div>

          {/* 7-Day Forecast */}
          <div className="card">
            <h3 style={{ marginBottom: '16px' }}>📅 7-Day Forecast & Daily Advisory</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {weather.forecast.map((day, idx) => (
                <div key={idx} style={{ display: 'grid', gridTemplateColumns: '120px 80px 100px 1fr', alignItems: 'center', padding: '14px', background: 'var(--bg)', borderRadius: '10px', border: '1px solid var(--border)' }}>
                  <div style={{ fontWeight: 600 }}>
                    {idx === 0 ? 'Today' : new Date(day.date).toLocaleDateString('en-IN', { weekday: 'long', month: 'short', day: 'numeric' })}
                  </div>
                  <div style={{ fontSize: '24px', textAlign: 'center' }}>{day.weather_code >= 95 ? '⛈️' : day.precipitation_sum > 5 ? '🌧️' : day.weather_code <= 1 ? '☀️' : '⛅'}</div>
                  <div>
                    <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>{Math.round(day.temp_max)}°</span> / <span style={{ color: 'var(--text-muted)' }}>{Math.round(day.temp_min)}°</span>
                  </div>
                  <div style={{ fontSize: '13px', color: 'var(--text-secondary)', fontStyle: day.crop_advisory ? 'italic' : 'normal' }}>
                    {day.crop_advisory || 'Conditions normal. Safe for standard farm operations.'}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
          <p>Please register a farm with location details to fetch personalized weather alerts.</p>
        </div>
      )}
    </div>
  )
}
