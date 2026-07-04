/**
 * Profile Page
 */
import { useForm } from 'react-hook-form'
import { useMe, useMe as useMeQuery } from '../../api/hooks'
import { authAPI } from '../../api'
import toast from 'react-hot-toast'

export default function ProfilePage() {
  const { data: user, refetch } = useMe()
  const { register, handleSubmit } = useForm({
    values: {
      full_name: user?.full_name || '',
      preferred_language: user?.preferred_language || 'en',
      district: user?.farmer_profile?.district || '',
      state: user?.farmer_profile?.state || '',
      total_land_acres: user?.farmer_profile?.total_land_acres || 0,
      farming_experience_years: user?.farmer_profile?.farming_experience_years || 0,
      bio: user?.farmer_profile?.bio || '',
      gemini_api_key: user?.farmer_profile?.gemini_api_key || '',
    }
  })

  const onSubmit = async (data: any) => {
    try {
      await authAPI.updateMe({
        full_name: data.full_name,
        preferred_language: data.preferred_language,
      })
      await authAPI.updateFarmerProfile({
        district: data.district,
        state: data.state,
        total_land_acres: parseFloat(data.total_land_acres),
        farming_experience_years: parseInt(data.farming_experience_years),
        bio: data.bio,
        gemini_api_key: data.gemini_api_key,
      })
      toast.success('Profile saved successfully! 💾')
      refetch()
    } catch {
      toast.error('Failed to update profile settings')
    }
  }

  return (
    <div style={{ maxWidth: '600px', margin: '0 auto' }}>
      <div className="page-header">
        <div className="page-header-left">
          <h1 className="page-title">⚙️ Farmer Profile</h1>
          <p className="page-subtitle">Manage your personal settings and agriculture metrics</p>
        </div>
      </div>

      <div className="card">
        <form onSubmit={handleSubmit(onSubmit)} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div className="form-group">
            <label className="form-label">Full Name</label>
            <input {...register('full_name')} className="input" placeholder="Name" id="profile-name" required />
          </div>

          <div className="form-group">
            <label className="form-label">Preferred Language</label>
            <select {...register('preferred_language')} className="input" id="profile-lang">
              <option value="en">🇬🇧 English</option>
              <option value="ta">🇮🇳 Tamil (தமிழ்)</option>
            </select>
          </div>

          <hr style={{ border: 'none', borderTop: '1px solid var(--border)' }} />
          <h3>🌾 Farm Bio Parameters</h3>

          <div className="grid-2">
            <div className="form-group">
              <label className="form-label">State</label>
              <input {...register('state')} className="input" placeholder="State" id="profile-state" />
            </div>
            <div className="form-group">
              <label className="form-label">District</label>
              <input {...register('district')} className="input" placeholder="District" id="profile-district" />
            </div>
          </div>

          <div className="grid-2">
            <div className="form-group">
              <label className="form-label">Total Land Size (Acres)</label>
              <input {...register('total_land_acres')} type="number" step="0.1" className="input" id="profile-land" />
            </div>
            <div className="form-group">
              <label className="form-label">Years of Experience</label>
              <input {...register('farming_experience_years')} type="number" className="input" id="profile-experience" />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Farmer Bio</label>
            <textarea {...register('bio')} className="input" placeholder="Describe your farm products or agricultural history..." id="profile-bio" rows={3} />
          </div>

          <hr style={{ border: 'none', borderTop: '1px solid var(--border)', margin: '20px 0' }} />
          <h3>🔑 API Configuration</h3>

          <div className="form-group">
            <label className="form-label">Google Gemini API Key</label>
            <input
              {...register('gemini_api_key')}
              type="password"
              className="input"
              placeholder="AIzaSy..."
              id="profile-gemini-key"
            />
            <p style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>
              Enter your Google Gemini API key to unlock full AI capabilities in the Chatbot and Crop Doctor.
            </p>
          </div>

          <button type="submit" id="profile-submit" className="btn btn-primary btn-lg" style={{ marginTop: '10px' }}>
            Save Settings 🌾
          </button>
        </form>
      </div>
    </div>
  )
}
