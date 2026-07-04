/**
 * api_base.ts — Axios instance with JWT interceptors
 * ALL API calls must go through this client.
 * Pages NEVER call fetch() directly.
 */

import axios, { AxiosError, AxiosResponse } from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || ''

export const apiClient = axios.create({
  baseURL: `${BASE_URL}/api/v1`,
  timeout: 60_000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// ─── Request Interceptor ─────────────────────────────────────
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('rootgs_access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// ─── Response Interceptor ────────────────────────────────────
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as any

    // Auto-refresh on 401
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      try {
        const refreshToken = localStorage.getItem('rootgs_refresh_token')
        if (!refreshToken) throw new Error('No refresh token')

        const res = await axios.post(`${BASE_URL}/api/v1/auth/refresh`, {
          refresh_token: refreshToken,
        })
        const newToken = res.data.data.access_token
        localStorage.setItem('rootgs_access_token', newToken)
        originalRequest.headers.Authorization = `Bearer ${newToken}`
        return apiClient(originalRequest)
      } catch {
        localStorage.clear()
        window.location.href = '/login'
        return Promise.reject(error)
      }
    }

    return Promise.reject(error)
  }
)

// ─── Helpers ──────────────────────────────────────────────────
export function extractError(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail)) return detail.map((d: any) => d.msg || d).join(', ')
    return error.response?.data?.message || error.message
  }
  if (error instanceof Error) return error.message
  return 'An unexpected error occurred'
}

export interface APIResponse<T = unknown> {
  success: boolean
  message: string
  data: T | null
  errors?: unknown
}

export interface PaginatedData<T> {
  data: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}
