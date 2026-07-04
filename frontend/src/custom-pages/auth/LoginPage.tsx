/**
 * Login Page — Modern agriculture-themed auth screen
 */

import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'

import { authAPI } from '../../api'
import { useAuthStore } from '../../store'
import { extractError } from '../../api/api_base'

const schema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(1, 'Password is required'),
})

type FormData = z.infer<typeof schema>

export default function LoginPage() {
  const navigate = useNavigate()
  const setAuth = useAuthStore(s => s.setAuth)
  const [loading, setLoading] = useState(false)

  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  })

  const onSubmit = async (data: FormData) => {
    setLoading(true)
    try {
      const res = await authAPI.login(data)
      const { user, access_token, refresh_token } = res.data.data!
      setAuth(user, access_token, refresh_token)
      toast.success(`Welcome back, ${user.full_name}! 🌾`)
      navigate('/dashboard')
    } catch (e) {
      toast.error(extractError(e))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      minHeight: '100vh',
      display: 'grid',
      gridTemplateColumns: '1fr 1fr',
      background: 'var(--bg)',
    }}>
      {/* Left — Branding */}
      <div style={{
        background: 'var(--gradient-hero)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '60px',
        position: 'relative',
        overflow: 'hidden',
      }}>
        {/* Decorative circles */}
        {[...Array(3)].map((_, i) => (
          <div key={i} style={{
            position: 'absolute',
            borderRadius: '50%',
            background: 'rgba(102,187,106,0.08)',
            width: `${(i + 1) * 200}px`,
            height: `${(i + 1) * 200}px`,
            right: `${-i * 60}px`,
            top: `${50 - i * 30}px`,
          }} />
        ))}

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
          style={{ textAlign: 'center', position: 'relative', zIndex: 1 }}
        >
          <div style={{ fontSize: '80px', marginBottom: '24px' }}>🌱</div>
          <h1 style={{ color: 'white', fontSize: '3.5rem', fontWeight: 900, marginBottom: '16px', letterSpacing: '-0.02em' }}>
            ROOTGS
          </h1>
          <p style={{ color: 'rgba(255,255,255,0.75)', fontSize: '18px', maxWidth: '380px', lineHeight: 1.6 }}>
            An AI scientist living inside every farm.
          </p>

          <div style={{ marginTop: '48px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {[
              { icon: '🔬', text: 'AI Disease Detection' },
              { icon: '🌤️', text: '7-Day Weather Intelligence' },
              { icon: '📈', text: 'Real-time Market Prices' },
              { icon: '🏛️', text: 'Government Scheme Finder' },
            ].map((f, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 + i * 0.1 }}
                style={{
                  display: 'flex', alignItems: 'center', gap: '12px',
                  background: 'rgba(255,255,255,0.08)',
                  border: '1px solid rgba(255,255,255,0.12)',
                  borderRadius: '12px', padding: '12px 20px',
                }}
              >
                <span style={{ fontSize: '22px' }}>{f.icon}</span>
                <span style={{ color: 'rgba(255,255,255,0.85)', fontSize: '14px', fontWeight: 500 }}>{f.text}</span>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Right — Form */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '60px' }}>
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6 }}
          style={{ width: '100%', maxWidth: '420px' }}
        >
          <h2 style={{ marginBottom: '8px' }}>Welcome back 👋</h2>
          <p style={{ marginBottom: '36px', color: 'var(--text-muted)' }}>Sign in to your ROOTGS account</p>

          <form onSubmit={handleSubmit(onSubmit)} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div className="form-group">
              <label className="form-label">Email Address</label>
              <input
                {...register('email')}
                type="email"
                className={`input ${errors.email ? 'input-error' : ''}`}
                placeholder="farmer@example.com"
                id="login-email"
              />
              {errors.email && <span className="error-message">⚠️ {errors.email.message}</span>}
            </div>

            <div className="form-group">
              <label className="form-label">Password</label>
              <input
                {...register('password')}
                type="password"
                className={`input ${errors.password ? 'input-error' : ''}`}
                placeholder="Enter your password"
                id="login-password"
              />
              {errors.password && <span className="error-message">⚠️ {errors.password.message}</span>}
              <div style={{ textAlign: 'right', marginTop: '4px' }}>
                <Link to="/forgot-password" style={{ fontSize: '13px', color: 'var(--primary)' }}>
                  Forgot password?
                </Link>
              </div>
            </div>

            <button
              type="submit"
              id="login-submit"
              className="btn btn-primary btn-lg"
              disabled={loading}
              style={{ width: '100%', marginTop: '8px' }}
            >
              {loading ? (
                <><div className="spinner" style={{ width: '18px', height: '18px', borderWidth: '2px' }} /> Signing in...</>
              ) : (
                'Sign In 🌾'
              )}
            </button>
          </form>

          {/* Demo credentials */}
          <div style={{
            marginTop: '20px', padding: '16px', background: 'var(--primary-glow)',
            border: '1px solid var(--border-dark)', borderRadius: '12px',
          }}>
            <p style={{ fontSize: '13px', fontWeight: 600, color: 'var(--primary)', marginBottom: '8px' }}>
              🧪 Demo Credentials
            </p>
            <p style={{ fontSize: '12px', color: 'var(--text-muted)', margin: 0 }}>
              Email: <code>farmer@rootgs.demo</code><br />
              Password: <code>demo1234</code>
            </p>
          </div>

          <p style={{ textAlign: 'center', marginTop: '28px', fontSize: '14px', color: 'var(--text-muted)' }}>
            New to ROOTGS?{' '}
            <Link to="/register" style={{ color: 'var(--primary)', fontWeight: 600 }}>
              Create an account
            </Link>
          </p>
        </motion.div>
      </div>
    </div>
  )
}
