/** Create Farm Page */
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useCreateFarm } from '../../api/hooks'

const schema = z.object({
  name: z.string().min(2, 'Farm name required'),
  total_area_acres: z.number().min(0.1, 'Area must be positive'),
  soil_type: z.enum(['clay', 'sandy', 'loamy', 'silty', 'peaty', 'chalky', 'clay_loam']),
  irrigation_type: z.enum(['drip', 'sprinkler', 'flood', 'furrow', 'rainfed', 'none']),
  village: z.string().optional(),
  district: z.string().optional(),
  state: z.string().optional(),
  latitude: z.number().optional(),
  longitude: z.number().optional(),
  description: z.string().optional(),
})
type FormData = z.infer<typeof schema>

export default function CreateFarmPage() {
  const navigate = useNavigate()
  const createFarm = useCreateFarm()

  const { register, handleSubmit, setValue, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { soil_type: 'loamy', irrigation_type: 'rainfed' },
  })

  const onSubmit = async (data: FormData) => {
    const farm = await createFarm.mutateAsync(data)
    if (farm) navigate(`/farms/${farm.id}`)
  }

  const getGPS = () => {
    navigator.geolocation?.getCurrentPosition(pos => {
      setValue('latitude', pos.coords.latitude)
      setValue('longitude', pos.coords.longitude)
    })
  }

  return (
    <div style={{ maxWidth: '700px', margin: '0 auto' }}>
      <div className="page-header">
        <div className="page-header-left">
          <h1 className="page-title">🌾 Add New Farm</h1>
          <p className="page-subtitle">Register your farm to unlock AI recommendations</p>
        </div>
      </div>

      <motion.div className="card card-lg" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <form onSubmit={handleSubmit(onSubmit)} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div className="form-group">
            <label className="form-label">Farm Name *</label>
            <input {...register('name')} className={`input ${errors.name ? 'input-error' : ''}`} placeholder="e.g., Krishnamurthy Paddy Farm" id="farm-name" />
            {errors.name && <span className="error-message">⚠️ {errors.name.message}</span>}
          </div>

          <div className="grid-2">
            <div className="form-group">
              <label className="form-label">Total Area (Acres) *</label>
              <input {...register('total_area_acres', { valueAsNumber: true })} type="number" step="0.1" className={`input ${errors.total_area_acres ? 'input-error' : ''}`} placeholder="e.g., 5.5" id="farm-area" />
              {errors.total_area_acres && <span className="error-message">⚠️ {errors.total_area_acres.message}</span>}
            </div>

            <div className="form-group">
              <label className="form-label">Soil Type *</label>
              <select {...register('soil_type')} className="input" id="farm-soil">
                <option value="loamy">🟫 Loamy (Best)</option>
                <option value="clay">🟤 Clay</option>
                <option value="sandy">🏖️ Sandy</option>
                <option value="silty">⚫ Silty</option>
                <option value="clay_loam">🟫 Clay Loam</option>
                <option value="peaty">🌿 Peaty</option>
                <option value="chalky">⬜ Chalky</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Irrigation Type *</label>
            <select {...register('irrigation_type')} className="input" id="farm-irrigation">
              <option value="drip">💧 Drip (Most Efficient)</option>
              <option value="sprinkler">🌧️ Sprinkler</option>
              <option value="flood">🌊 Flood</option>
              <option value="furrow">🌾 Furrow</option>
              <option value="rainfed">🌧️ Rainfed</option>
              <option value="none">❌ None</option>
            </select>
          </div>

          <div className="grid-3">
            <div className="form-group">
              <label className="form-label">Village</label>
              <input {...register('village')} className="input" placeholder="Village name" id="farm-village" />
            </div>
            <div className="form-group">
              <label className="form-label">District</label>
              <input {...register('district')} className="input" placeholder="District" id="farm-district" />
            </div>
            <div className="form-group">
              <label className="form-label">State</label>
              <input {...register('state')} className="input" placeholder="State" id="farm-state" />
            </div>
          </div>

          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <label className="form-label">GPS Location</label>
              <button type="button" className="btn btn-secondary btn-sm" onClick={getGPS} id="gps-btn">📍 Use My Location</button>
            </div>
            <div className="grid-2">
              <input {...register('latitude', { valueAsNumber: true })} type="number" step="0.000001" className="input" placeholder="Latitude" id="farm-lat" />
              <input {...register('longitude', { valueAsNumber: true })} type="number" step="0.000001" className="input" placeholder="Longitude" id="farm-lon" />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Description</label>
            <textarea {...register('description')} className="input" placeholder="Additional details about your farm..." id="farm-desc" rows={3} />
          </div>

          <button type="submit" id="create-farm-submit" className="btn btn-primary btn-lg" disabled={createFarm.isPending} style={{ width: '100%' }}>
            {createFarm.isPending ? '⏳ Creating Farm...' : '🌾 Create Farm'}
          </button>
        </form>
      </motion.div>
    </div>
  )
}
