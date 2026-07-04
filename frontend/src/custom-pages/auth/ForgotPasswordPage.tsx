/** Forgot Password Page */
import { useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import { authAPI } from '../../api'
import { extractError } from '../../api/api_base'

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [sent, setSent] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      await authAPI.forgotPassword(email)
      setSent(true)
      toast.success('Reset instructions sent!')
    } catch (err) {
      toast.error(extractError(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--bg)', padding: '40px' }}>
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} style={{ width: '100%', maxWidth: '400px' }}>
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <div style={{ fontSize: '48px', marginBottom: '12px' }}>🔑</div>
          <h2>Reset Password</h2>
          <p style={{ color: 'var(--text-muted)' }}>Enter your email to receive reset instructions</p>
        </div>
        <div className="card card-lg">
          {sent ? (
            <div style={{ textAlign: 'center', padding: '20px' }}>
              <div style={{ fontSize: '48px', marginBottom: '12px' }}>📧</div>
              <h3>Email Sent!</h3>
              <p style={{ color: 'var(--text-muted)', marginBottom: '20px' }}>Check your inbox for password reset instructions.</p>
              <Link to="/login" className="btn btn-primary" style={{ width: '100%', display: 'flex' }}>Back to Login</Link>
            </div>
          ) : (
            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div className="form-group">
                <label className="form-label">Email Address</label>
                <input type="email" value={email} onChange={e => setEmail(e.target.value)} className="input" placeholder="your@email.com" id="forgot-email" required />
              </div>
              <button type="submit" id="forgot-submit" className="btn btn-primary" disabled={loading} style={{ width: '100%' }}>
                {loading ? 'Sending...' : 'Send Reset Link'}
              </button>
              <Link to="/login" style={{ textAlign: 'center', fontSize: '14px', color: 'var(--text-muted)' }}>← Back to Login</Link>
            </form>
          )}
        </div>
      </motion.div>
    </div>
  )
}
