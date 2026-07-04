/**
 * Register Page
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
  full_name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Invalid email'),
  phone: z.string().optional(),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  role: z.enum(['farmer', 'agriculture_officer', 'agronomist', 'researcher']),
})

type FormData = z.infer<typeof schema>

export default function RegisterPage() {
  const navigate = useNavigate()
  const setAuth = useAuthStore(s => s.setAuth)
  const [loading, setLoading] = useState(false)

  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { role: 'farmer' },
  })

  const onSubmit = async (data: FormData) => {
    setLoading(true)
    try {
      const res = await authAPI.register(data)
      const { user, access_token, refresh_token } = res.data.data!
      setAuth(user, access_token, refresh_token)
      toast.success('Welcome to ROOTGS! 🌱')
      navigate('/dashboard')
    } catch (e) {
      toast.error(extractError(e))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '40px', background: 'var(--bg)' }}>
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} style={{ width: '100%', maxWidth: '460px' }}>
        <div style={{ textAlign: 'center', marginBottom: '36px' }}>
          <div style={{ fontSize: '48px', marginBottom: '12px' }}>🌱</div>
          <h1 style={{ fontSize: '2rem', marginBottom: '8px' }}>Join ROOTGS</h1>
          <p style={{ color: 'var(--text-muted)' }}>Start your AI-powered farming journey</p>
        </div>

        <div className="card card-lg">
          <form onSubmit={handleSubmit(onSubmit)} style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
            <div className="form-group">
              <label className="form-label">Full Name *</label>
              <input {...register('full_name')} className={`input ${errors.full_name ? 'input-error' : ''}`} placeholder="Your full name" id="reg-name" />
              {errors.full_name && <span className="error-message">⚠️ {errors.full_name.message}</span>}
            </div>

            <div className="form-group">
              <label className="form-label">Email Address *</label>
              <input {...register('email')} type="email" className={`input ${errors.email ? 'input-error' : ''}`} placeholder="email@example.com" id="reg-email" />
              {errors.email && <span className="error-message">⚠️ {errors.email.message}</span>}
            </div>

            <div className="form-group">
              <label className="form-label">Phone Number</label>
              <input {...register('phone')} type="tel" className="input" placeholder="+91 9876543210" id="reg-phone" />
            </div>

            <div className="form-group">
              <label className="form-label">I am a *</label>
              <select {...register('role')} className="input" id="reg-role">
                <option value="farmer">👨‍🌾 Farmer</option>
                <option value="agriculture_officer">🏛️ Agriculture Officer</option>
                <option value="agronomist">🔬 Agronomist</option>
                <option value="researcher">📚 Researcher</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Password *</label>
              <input {...register('password')} type="password" className={`input ${errors.password ? 'input-error' : ''}`} placeholder="Min. 8 characters" id="reg-password" />
              {errors.password && <span className="error-message">⚠️ {errors.password.message}</span>}
            </div>

            <button type="submit" id="reg-submit" className="btn btn-primary btn-lg" disabled={loading} style={{ width: '100%', marginTop: '8px' }}>
              {loading ? <><div className="spinner" style={{ width: '16px', height: '16px', borderWidth: '2px' }} /> Creating account...</> : 'Create Account 🌾'}
            </button>
          </form>

          <p style={{ textAlign: 'center', marginTop: '20px', fontSize: '14px', color: 'var(--text-muted)' }}>
            Already have an account?{' '}
            <Link to="/login" style={{ color: 'var(--primary)', fontWeight: 600 }}>Sign in</Link>
          </p>
        </div>
      </motion.div>
    </div>
  )
}
