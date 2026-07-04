/**
 * Analytics Page
 */
import { useState } from 'react'
import { useAnalyticsDashboard, useExpenses, useAddExpense, useFarms } from '../../api/hooks'

export default function AnalyticsPage() {
  const { data: dashboard, isLoading: dashLoading } = useAnalyticsDashboard()
  const { data: farmsData } = useFarms()
  const farms = farmsData?.data ?? []

  const [farmId, setFarmId] = useState('')
  const [category, setCategory] = useState('seeds')
  const [amount, setAmount] = useState('')
  const [desc, setDesc] = useState('')

  const addExpenseMutation = useAddExpense()
  const { data: expenses, isLoading: expLoading } = useExpenses({ farm_id: farmId ? parseInt(farmId) : undefined })

  const handleAddExpense = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!farmId || !amount || !desc) return

    await addExpenseMutation.mutateAsync({
      farm_id: parseInt(farmId),
      category,
      amount: parseFloat(amount),
      description: desc,
      expense_date: new Date().toISOString().split('T')[0]
    })

    setAmount('')
    setDesc('')
  }

  return (
    <div>
      <div className="page-header">
        <div className="page-header-left">
          <h1 className="page-title">📊 Farm Analytics</h1>
          <p className="page-subtitle">Yield predictions, expense tracking, and farm profitability dashboard</p>
        </div>
      </div>

      {dashLoading ? (
        <div className="skeleton" style={{ height: '140px', borderRadius: '16px', marginBottom: '24px' }} />
      ) : (
        <div className="grid-3" style={{ marginBottom: '24px' }}>
          <div className="card" style={{ background: 'var(--gradient-hero)', color: 'white', border: 'none' }}>
            <div style={{ fontSize: '11px', opacity: 0.8 }}>TOTAL EXPENSES</div>
            <div style={{ fontSize: '2.5rem', fontWeight: 800 }}>₹{dashboard?.total_expenses?.toLocaleString()}</div>
            <div style={{ fontSize: '12px', opacity: 0.8, marginTop: '8px' }}>Across {dashboard?.farm_count} registered plots</div>
          </div>
          <div className="card">
            <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>PROJECTED REVENUE</div>
            <div style={{ fontSize: '2.5rem', fontWeight: 800 }}>₹{(dashboard?.total_revenue || 0).toLocaleString()}</div>
            <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '8px' }}>Based on modal crop cycle predictions</div>
          </div>
          <div className="card">
            <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>NET YIELD MARGIN</div>
            <div style={{ fontSize: '2.5rem', fontWeight: 800 }}>0.00%</div>
            <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '8px' }}>Optimized water & soil balance index</div>
          </div>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.5fr', gap: '24px' }}>
        {/* Record Expense */}
        <div className="card">
          <h3 style={{ marginBottom: '16px' }}>💰 Record Expense</h3>
          <form onSubmit={handleAddExpense} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div className="form-group">
              <label className="form-label">Select Farm</label>
              <select className="input" value={farmId} onChange={e => setFarmId(e.target.value)} required id="expense-farm">
                <option value="" disabled>Choose farm...</option>
                {farms.map(f => (
                  <option key={f.id} value={f.id}>{f.name}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Expense Category</label>
              <select className="input" value={category} onChange={e => setCategory(e.target.value)} id="expense-category">
                <option value="seeds">Seeds</option>
                <option value="fertilizer">Fertilizer</option>
                <option value="pesticide">Pesticide</option>
                <option value="labor">Labor</option>
                <option value="irrigation">Irrigation</option>
                <option value="equipment">Equipment</option>
                <option value="transport">Transport</option>
                <option value="other">Other</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Amount (₹)</label>
              <input type="number" className="input" placeholder="e.g. 5000" value={amount} onChange={e => setAmount(e.target.value)} required id="expense-amount" />
            </div>

            <div className="form-group">
              <label className="form-label">Description</label>
              <input className="input" placeholder="e.g. purchased organic compost" value={desc} onChange={e => setDesc(e.target.value)} required id="expense-desc" />
            </div>

            <button type="submit" id="expense-submit" className="btn btn-primary btn-lg" disabled={addExpenseMutation.isPending}>
              {addExpenseMutation.isPending ? 'Saving...' : '💰 Record Expense'}
            </button>
          </form>
        </div>

        {/* Expenses List */}
        <div className="card">
          <h3 style={{ marginBottom: '16px' }}>📋 Expense History</h3>
          {expLoading ? (
            <div className="skeleton" style={{ height: '200px', borderRadius: '12px' }} />
          ) : expenses && expenses.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {expenses.map(exp => (
                <div key={exp.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px', background: 'var(--bg)', borderRadius: '8px', border: '1px solid var(--border)' }}>
                  <div>
                    <div style={{ fontWeight: 600 }}>{exp.description}</div>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                      Category: <span style={{ textTransform: 'capitalize' }}>{exp.category}</span> • Date: {exp.expense_date}
                    </div>
                  </div>
                  <strong style={{ color: 'var(--danger)', fontSize: '16px' }}>- ₹{exp.amount}</strong>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '20px' }}>No expenses logged yet.</p>
          )}
        </div>
      </div>
    </div>
  )
}
