/**
 * TypeScript types for all ROOTGS domains
 */

// ─── Auth ─────────────────────────────────────────────────────
export interface LoginPayload {
  email: string
  password: string
}

export interface RegisterPayload {
  email: string
  phone?: string
  full_name: string
  password: string
  role?: UserRole
  preferred_language?: string
}

export type UserRole = 'farmer' | 'agriculture_officer' | 'agronomist' | 'admin' | 'researcher'

export interface FarmerProfile {
  id: number
  district?: string
  state?: string
  total_land_acres?: number
  farming_experience_years?: number
  primary_crops?: string
  bio?: string
  gemini_api_key?: string
}

export interface FarmerProfileUpdate {
  district?: string
  state?: string
  pin_code?: string
  total_land_acres?: number
  farming_experience_years?: number
  primary_crops?: string
  bio?: string
  fcm_token?: string
  gemini_api_key?: string
}

export interface UserOut {
  id: number
  email: string
  phone?: string
  full_name: string
  role: UserRole
  is_active: boolean
  is_verified: boolean
  profile_image?: string
  preferred_language: string
  created_at: string
  farmer_profile?: FarmerProfile
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  user: UserOut
}

// ─── Farm ─────────────────────────────────────────────────────
export type SoilType = 'clay' | 'sandy' | 'loamy' | 'silty' | 'peaty' | 'chalky' | 'clay_loam'
export type IrrigationType = 'drip' | 'sprinkler' | 'flood' | 'furrow' | 'rainfed' | 'none'

export interface FarmCreate {
  name: string
  description?: string
  latitude?: number
  longitude?: number
  address?: string
  village?: string
  district?: string
  state?: string
  pin_code?: string
  total_area_acres: number
  soil_type?: SoilType
  irrigation_type?: IrrigationType
}

export interface FarmUpdate extends Partial<FarmCreate> {
  cover_image?: string
}

export interface Field {
  id: number
  farm_id: number
  name: string
  area_acres: number
  soil_type: SoilType
  coordinates?: string
  current_crop?: string
  notes?: string
  created_at: string
}

export interface FieldCreate {
  name: string
  area_acres: number
  soil_type?: SoilType
  coordinates?: string
  current_crop?: string
}

export interface SoilReport {
  id: number
  farm_id: number
  ph?: number
  nitrogen?: number
  phosphorus?: number
  potassium?: number
  organic_matter?: number
  moisture?: number
  ai_recommendation?: string
  suitable_crops?: string
  created_at: string
}

export interface SoilReportCreate {
  field_id?: number
  ph?: number
  nitrogen?: number
  phosphorus?: number
  potassium?: number
  organic_matter?: number
  moisture?: number
  lab_name?: string
  sample_date?: string
}

export interface Farm {
  id: number
  owner_id: number
  name: string
  description?: string
  latitude?: number
  longitude?: number
  address?: string
  village?: string
  district?: string
  state?: string
  total_area_acres: number
  soil_type: SoilType
  irrigation_type: IrrigationType
  health_score: number
  water_usage_score: number
  carbon_score: number
  cover_image?: string
  is_active: boolean
  created_at: string
  fields: Field[]
}

// ─── Disease ──────────────────────────────────────────────────
export type DiseaseSeverity = 'none' | 'mild' | 'moderate' | 'severe' | 'critical'

export interface TreatmentItem {
  name: string
  dosage?: string
  frequency?: string
  notes?: string
}

export interface DiseaseReport {
  report_id: number
  crop_name?: string
  disease_name?: string
  disease_scientific_name?: string
  confidence_score: number
  severity: DiseaseSeverity
  affected_area_percent?: number
  description?: string
  reason?: string
  evidence?: string
  risk_level?: string
  chemical_treatment?: TreatmentItem[]
  organic_treatment?: TreatmentItem[]
  prevention_tips?: string[]
  medicine_dosage?: string
  estimated_loss_percent?: number
  alternative_diagnosis?: Array<{ disease: string; confidence: number }>
  image_url: string
  processing_time_ms?: number
  ai_model_used?: string
}

// ─── Weather ──────────────────────────────────────────────────
export interface WeatherCurrent {
  temperature: number
  feels_like: number
  humidity: number
  wind_speed: number
  wind_direction: number
  pressure: number
  visibility: number
  uv_index: number
  weather_code: number
  description: string
  icon: string
  is_day: boolean
  precipitation: number
}

export interface WeatherForecastDay {
  date: string
  temp_max: number
  temp_min: number
  precipitation_sum: number
  wind_speed_max: number
  weather_code: number
  description: string
  sunrise: string
  sunset: string
  uv_index_max: number
  crop_advisory?: string
}

export interface WeatherResponse {
  latitude: number
  longitude: number
  location_name?: string
  current: WeatherCurrent
  forecast: WeatherForecastDay[]
  alerts: string[]
  crop_advisory?: string
}

// ─── Market ───────────────────────────────────────────────────
export interface MarketPrice {
  id: number
  crop_name: string
  market_name: string
  state: string
  district?: string
  price_date: string
  min_price: number
  max_price: number
  modal_price: number
  unit: string
}

export interface MarketTrend {
  crop_name: string
  market_name: string
  dates: string[]
  prices: number[]
  trend_direction: 'up' | 'down' | 'stable'
  trend_percentage: number
  best_sell_day?: string
  price_prediction_next_week?: number
}

// ─── Government Schemes ───────────────────────────────────────
export interface GovernmentScheme {
  id: number
  name: string
  scheme_code?: string
  authority: string
  state?: string
  category: string
  description: string
  benefits?: string
  eligibility?: string
  required_documents?: string
  application_url?: string
  deadline?: string
  max_benefit_amount?: number
  is_active: boolean
}

// ─── Chat ─────────────────────────────────────────────────────
export interface ChatMessage {
  id: number
  session_id: number
  role: 'user' | 'assistant'
  content: string
  language: string
  reasoning?: string
  confidence?: number
  is_voice: boolean
  created_at: string
}

export interface ChatSession {
  id: number
  user_id: number
  title: string
  language: string
  is_active: boolean
  created_at: string
  messages: ChatMessage[]
}

// ─── Analytics ────────────────────────────────────────────────
export interface AnalyticsDashboard {
  farm_count: number
  total_expenses: number
  total_revenue: number
  farms: Array<{
    farm_id: number
    farm_name: string
    health_score: number
    water_usage_score: number
    carbon_score: number
    total_expenses: number
  }>
}

export interface Expense {
  id: number
  farm_id: number
  category: string
  description: string
  amount: number
  expense_date: string
  created_at: string
}

export interface ExpenseCreate {
  farm_id: number
  crop_cycle_id?: number
  category: string
  description: string
  amount: number
  expense_date: string
}

// ─── Notifications ────────────────────────────────────────────
export interface Notification {
  id: number
  title: string
  body: string
  type: string
  is_read: boolean
  action_url?: string
  created_at: string
}

// ─── Tasks ────────────────────────────────────────────────────
export interface Task {
  id: number
  user_id: number
  farm_id?: number
  title: string
  description?: string
  due_date?: string
  status: 'pending' | 'in_progress' | 'completed' | 'skipped'
  priority: 'low' | 'medium' | 'high' | 'urgent'
  category?: string
  is_ai_generated: boolean
  created_at: string
}

export interface TaskCreate {
  title: string
  description?: string
  farm_id?: number
  due_date?: string
  priority?: string
  category?: string
}

// ─── Irrigation ───────────────────────────────────────────────
export interface IrrigationRequest {
  farm_id: number
  crop_name: string
  area_acres: number
  soil_type: string
  current_stage: string
  last_irrigation_days?: number
  rainfall_last_7_days_mm?: number
}

export interface IrrigationSchedule {
  recommended: boolean
  water_required_liters: number
  next_irrigation_date: string
  frequency_days: number
  method: string
  reason: string
  confidence: number
  daily_schedule: Array<{ date: string; irrigate: boolean; water_liters: number; time?: string }>
  water_saving_tips: string[]
  water_saving_score: number
}
