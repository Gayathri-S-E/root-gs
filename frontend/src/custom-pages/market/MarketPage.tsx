/**
 * Market Intelligence Page
 */
import { useState } from 'react'
import { useMarketPrices, useMarketTrend } from '../../api/hooks'

export default function MarketPage() {
  const [cropSearch, setCropSearch] = useState('')
  const [selectedCrop, setSelectedCrop] = useState<string | null>(null)
  const { data: prices, isLoading } = useMarketPrices({ crop_name: cropSearch || undefined })
  const { data: trend } = useMarketTrend(selectedCrop ?? '')

  return (
    <div>
      <div className="page-header">
        <div className="page-header-left">
          <h1 className="page-title">📈 Market Intelligence</h1>
          <p className="page-subtitle">Real-time local market crop prices and trend insights</p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '24px' }}>
        {/* Prices List */}
        <div className="card">
          <h3 style={{ marginBottom: '16px' }}>🌾 Current Mandi Prices</h3>
          <div style={{ marginBottom: '16px' }}>
            <input
              className="input"
              placeholder="🔍 Search crops (e.g. Paddy, Onion, Wheat)..."
              value={cropSearch}
              onChange={e => setCropSearch(e.target.value)}
              id="market-search"
            />
          </div>

          {isLoading ? (
            <div className="skeleton" style={{ height: '300px', borderRadius: '12px' }} />
          ) : prices && prices.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {prices.map(item => (
                <div
                  key={item.id}
                  onClick={() => setSelectedCrop(item.crop_name)}
                  style={{
                    display: 'grid', gridTemplateColumns: '1.5fr 2fr 1fr 1fr',
                    alignItems: 'center', padding: '12px', background: 'var(--bg)',
                    borderRadius: '8px', border: `1px solid ${selectedCrop === item.crop_name ? 'var(--primary)' : 'var(--border)'}`,
                    cursor: 'pointer', transition: 'all 0.15s',
                  }}
                >
                  <div style={{ fontWeight: 700 }}>{item.crop_name}</div>
                  <div style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>🏪 {item.market_name}</div>
                  <div style={{ fontWeight: 600 }}>₹{item.modal_price}</div>
                  <span className="badge badge-neutral" style={{ fontSize: '10px' }}>/ {item.unit}</span>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '20px' }}>No price records found.</p>
          )}
        </div>

        {/* Trend analysis */}
        <div>
          {trend && selectedCrop ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
              <div className="card" style={{ background: 'var(--gradient-hero)', color: 'white', border: 'none' }}>
                <h3 style={{ color: 'white', marginBottom: '12px' }}>📊 Price Trend: {selectedCrop}</h3>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                  <div>
                    <div style={{ fontSize: '11px', opacity: 0.8 }}>TREND DIRECTION</div>
                    <div style={{ fontSize: '24px', fontWeight: 800, textTransform: 'uppercase' }}>
                      {trend.trend_direction === 'up' ? '📈 Bullish (Up)' : trend.trend_direction === 'down' ? '📉 Bearish (Down)' : 'Stable'}
                    </div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '11px', opacity: 0.8 }}>PERCENTAGE CHANGE</div>
                    <div style={{ fontSize: '24px', fontWeight: 800, color: trend.trend_direction === 'up' ? 'lightgreen' : trend.trend_direction === 'down' ? '#EF9A9A' : 'white' }}>
                      {trend.trend_percentage}%
                    </div>
                  </div>
                </div>
                {trend.best_sell_day && (
                  <div style={{ background: 'rgba(255,255,255,0.15)', padding: '10px', borderRadius: '8px', fontSize: '13px' }}>
                    💡 <strong>Sell recommendation:</strong> Strong market demand expected around {new Date(trend.best_sell_day).toLocaleDateString()}.
                  </div>
                )}
              </div>

              {/* Price list history */}
              <div className="card">
                <h3 style={{ marginBottom: '16px' }}>📈 Price History (Last 7 reports)</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  {trend.prices?.map((price, idx) => (
                    <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', padding: '10px', background: 'var(--bg)', borderRadius: '6px' }}>
                      <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>{trend.dates[idx]}</span>
                      <strong style={{ color: 'var(--text-primary)' }}>₹{price}</strong>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="card" style={{ textAlign: 'center', padding: '60px' }}>
              <div style={{ fontSize: '64px', marginBottom: '16px' }}>📊</div>
              <h3>Price Trend Insight</h3>
              <p style={{ color: 'var(--text-muted)' }}>Click on a crop price listing to view historical price charts and trend analysis.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
