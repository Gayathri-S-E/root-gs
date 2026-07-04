/**
 * api/index.ts — All API call functions
 * Pages NEVER import apiClient directly. Always use these functions.
 */

import { apiClient } from './api_base'
import type { APIResponse, PaginatedData } from './api_base'
import type {
  LoginPayload, RegisterPayload, TokenResponse, UserOut, FarmerProfileUpdate,
  Farm, FarmCreate, FarmUpdate, Field, FieldCreate, SoilReport, SoilReportCreate,
  DiseaseReport, WeatherResponse, MarketPrice, MarketTrend, GovernmentScheme,
  ChatSession, ChatMessage, AnalyticsDashboard, Expense, ExpenseCreate,
  Notification, Task, TaskCreate, IrrigationSchedule, IrrigationRequest,
} from '../types'


// ─── Auth ────────────────────────────────────────────────────
export const authAPI = {
  login: (p: LoginPayload) =>
    apiClient.post<APIResponse<TokenResponse>>('/auth/login', p),

  register: (p: RegisterPayload) =>
    apiClient.post<APIResponse<TokenResponse>>('/auth/register', p),

  me: () =>
    apiClient.get<APIResponse<UserOut>>('/auth/me'),

  updateMe: (p: Partial<UserOut>) =>
    apiClient.put<APIResponse<UserOut>>('/auth/me', p),

  updateFarmerProfile: (p: FarmerProfileUpdate) =>
    apiClient.put<APIResponse<unknown>>('/auth/me/farmer-profile', p),

  forgotPassword: (email: string) =>
    apiClient.post<APIResponse<null>>('/auth/forgot-password', { email }),

  resetPassword: (token: string, newPassword: string) =>
    apiClient.post<APIResponse<null>>('/auth/reset-password', { token, new_password: newPassword }),

  changePassword: (currentPassword: string, newPassword: string) =>
    apiClient.post<APIResponse<null>>('/auth/change-password', {
      current_password: currentPassword, new_password: newPassword,
    }),
}

// ─── Farms ───────────────────────────────────────────────────
export const farmAPI = {
  list: (params?: { page?: number; search?: string; state?: string }) =>
    apiClient.get<APIResponse<PaginatedData<Farm>>>('/farms', { params }),

  get: (id: number) =>
    apiClient.get<APIResponse<Farm>>(`/farms/${id}`),

  create: (p: FarmCreate) =>
    apiClient.post<APIResponse<Farm>>('/farms', p),

  update: (id: number, p: FarmUpdate) =>
    apiClient.put<APIResponse<Farm>>(`/farms/${id}`, p),

  delete: (id: number) =>
    apiClient.delete<APIResponse<null>>(`/farms/${id}`),

  createField: (farmId: number, p: FieldCreate) =>
    apiClient.post<APIResponse<Field>>(`/farms/${farmId}/fields`, p),

  listFields: (farmId: number) =>
    apiClient.get<APIResponse<Field[]>>(`/farms/${farmId}/fields`),

  createSoilReport: (farmId: number, p: SoilReportCreate) =>
    apiClient.post<APIResponse<SoilReport>>(`/farms/${farmId}/soil-reports`, p),

  listSoilReports: (farmId: number) =>
    apiClient.get<APIResponse<SoilReport[]>>(`/farms/${farmId}/soil-reports`),
}

// ─── Disease ─────────────────────────────────────────────────
export const diseaseAPI = {
  detect: (formData: FormData) =>
    apiClient.post<APIResponse<DiseaseReport>>('/disease/detect', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),

  history: (params?: { page?: number; farm_id?: number }) =>
    apiClient.get<APIResponse<PaginatedData<DiseaseReport>>>('/disease/history', { params }),

  getReport: (id: number) =>
    apiClient.get<APIResponse<DiseaseReport>>(`/disease/${id}`),
}

// ─── Weather ─────────────────────────────────────────────────
export const weatherAPI = {
  current: (lat: number, lon: number) =>
    apiClient.get<APIResponse<WeatherResponse>>('/weather/current', { params: { lat, lon } }),

  forFarm: (farmId: number) =>
    apiClient.get<APIResponse<WeatherResponse>>(`/weather/farm/${farmId}`),
}

// ─── Market ──────────────────────────────────────────────────
export const marketAPI = {
  prices: (params?: { state?: string; crop_name?: string }) =>
    apiClient.get<APIResponse<MarketPrice[]>>('/market/prices', { params }),

  trend: (cropName: string, state?: string) =>
    apiClient.get<APIResponse<MarketTrend>>(`/market/prices/${cropName}/trend`, {
      params: { state },
    }),

  addPrice: (p: Omit<MarketPrice, 'id'>) =>
    apiClient.post<APIResponse<MarketPrice>>('/market/prices', p),
}

// ─── Schemes ─────────────────────────────────────────────────
export const schemeAPI = {
  list: (params?: { category?: string; state?: string; search?: string }) =>
    apiClient.get<APIResponse<GovernmentScheme[]>>('/schemes', { params }),

  get: (id: number) =>
    apiClient.get<APIResponse<GovernmentScheme>>(`/schemes/${id}`),

  checkEligibility: (p: { scheme_id: number; farmer_state: string; land_acres: number }) =>
    apiClient.post<APIResponse<unknown>>('/schemes/check-eligibility', p),
}

// ─── Chat ────────────────────────────────────────────────────
export const chatAPI = {
  createSession: (title?: string, language?: string) =>
    apiClient.post<APIResponse<ChatSession>>('/chat/sessions', { title: title || 'New Conversation', language: language || 'en' }),

  listSessions: () =>
    apiClient.get<APIResponse<ChatSession[]>>('/chat/sessions'),

  sendMessage: (sessionId: number, p: { content: string; language?: string; is_voice?: boolean; farm_id?: number }) =>
    apiClient.post<APIResponse<ChatMessage>>(`/chat/sessions/${sessionId}/messages`, p),

  getMessages: (sessionId: number) =>
    apiClient.get<APIResponse<ChatMessage[]>>(`/chat/sessions/${sessionId}/messages`),

  deleteSession: (sessionId: number) =>
    apiClient.delete<APIResponse<null>>(`/chat/sessions/${sessionId}`),
}

// ─── Analytics ───────────────────────────────────────────────
export const analyticsAPI = {
  dashboard: () =>
    apiClient.get<APIResponse<AnalyticsDashboard>>('/analytics/dashboard'),

  addExpense: (p: ExpenseCreate) =>
    apiClient.post<APIResponse<Expense>>('/analytics/expenses', p),

  listExpenses: (params?: { farm_id?: number; category?: string }) =>
    apiClient.get<APIResponse<Expense[]>>('/analytics/expenses', { params }),
}

// ─── Notifications ───────────────────────────────────────────
export const notificationAPI = {
  list: (unreadOnly?: boolean) =>
    apiClient.get<APIResponse<{ notifications: Notification[]; unread_count: number }>>('/notifications', {
      params: { unread_only: unreadOnly },
    }),

  markRead: (id: number) =>
    apiClient.post<APIResponse<null>>(`/notifications/${id}/read`),

  markAllRead: () =>
    apiClient.post<APIResponse<null>>('/notifications/read-all'),
}

// ─── Irrigation ──────────────────────────────────────────────
export const irrigationAPI = {
  getSchedule: (p: IrrigationRequest) =>
    apiClient.post<APIResponse<IrrigationSchedule>>('/irrigation/schedule', p),
}

// ─── Crops ───────────────────────────────────────────────────
export const cropAPI = {
  list: (params?: { search?: string; season?: string; category?: string }) =>
    apiClient.get<APIResponse<unknown[]>>('/crops', { params }),

  get: (id: number) =>
    apiClient.get<APIResponse<unknown>>(`/crops/${id}`),

  recommendForFarm: (farmId: number) =>
    apiClient.get<APIResponse<unknown>>(`/crops/recommend/for-farm/${farmId}`),
}

// ─── Admin ───────────────────────────────────────────────────
export const adminAPI = {
  stats: () =>
    apiClient.get<APIResponse<unknown>>('/admin/stats'),

  listUsers: (params?: { role?: string; page?: number }) =>
    apiClient.get<APIResponse<unknown[]>>('/admin/users', { params }),

  toggleUser: (userId: number) =>
    apiClient.patch<APIResponse<null>>(`/admin/users/${userId}/toggle-active`),
}
