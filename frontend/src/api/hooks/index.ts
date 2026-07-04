/**
 * React Query hooks for all domains
 * Pages always use hooks — never call API directly
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { authAPI, farmAPI, diseaseAPI, weatherAPI, marketAPI, schemeAPI, chatAPI, analyticsAPI, notificationAPI, irrigationAPI, cropAPI } from '../index'
import type { FarmCreate, FarmUpdate, FieldCreate, SoilReportCreate, ExpenseCreate, IrrigationRequest } from '../../types'
import { extractError } from '../api_base'
import toast from 'react-hot-toast'


// ─── Auth Hooks ───────────────────────────────────────────────
export const useMe = () =>
  useQuery({ queryKey: ['me'], queryFn: () => authAPI.me().then(r => r.data.data), staleTime: 5 * 60_000 })


// ─── Farm Hooks ───────────────────────────────────────────────
export const useFarms = (params?: { page?: number; search?: string }) =>
  useQuery({ queryKey: ['farms', params], queryFn: () => farmAPI.list(params).then(r => r.data.data) })

export const useFarm = (id: number) =>
  useQuery({ queryKey: ['farm', id], queryFn: () => farmAPI.get(id).then(r => r.data.data), enabled: !!id })

export const useCreateFarm = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (p: FarmCreate) => farmAPI.create(p).then(r => r.data.data),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['farms'] }); toast.success('Farm created! 🌾') },
    onError: (e) => toast.error(extractError(e)),
  })
}

export const useUpdateFarm = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: FarmUpdate }) => farmAPI.update(id, data).then(r => r.data.data),
    onSuccess: (_, { id }) => { qc.invalidateQueries({ queryKey: ['farm', id] }); toast.success('Farm updated') },
    onError: (e) => toast.error(extractError(e)),
  })
}

export const useDeleteFarm = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => farmAPI.delete(id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['farms'] }); toast.success('Farm removed') },
  })
}

export const useCreateField = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ farmId, data }: { farmId: number; data: FieldCreate }) => farmAPI.createField(farmId, data).then(r => r.data.data),
    onSuccess: (_, { farmId }) => qc.invalidateQueries({ queryKey: ['farm', farmId] }),
  })
}

export const useSoilReports = (farmId: number) =>
  useQuery({ queryKey: ['soil-reports', farmId], queryFn: () => farmAPI.listSoilReports(farmId).then(r => r.data.data), enabled: !!farmId })

export const useCreateSoilReport = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ farmId, data }: { farmId: number; data: SoilReportCreate }) => farmAPI.createSoilReport(farmId, data).then(r => r.data.data),
    onSuccess: (_, { farmId }) => { qc.invalidateQueries({ queryKey: ['soil-reports', farmId] }); toast.success('Soil report saved with AI analysis 🧪') },
    onError: (e) => toast.error(extractError(e)),
  })
}


// ─── Disease Hooks ────────────────────────────────────────────
export const useDiseaseHistory = (params?: { page?: number; farm_id?: number }) =>
  useQuery({ queryKey: ['disease-history', params], queryFn: () => diseaseAPI.history(params).then(r => r.data.data) })

export const useDetectDisease = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (formData: FormData) => diseaseAPI.detect(formData).then(r => r.data.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['disease-history'] }),
    onError: (e) => toast.error(extractError(e)),
  })
}


// ─── Weather Hooks ────────────────────────────────────────────
export const useWeather = (lat?: number, lon?: number) =>
  useQuery({
    queryKey: ['weather', lat, lon],
    queryFn: () => weatherAPI.current(lat!, lon!).then(r => r.data.data),
    enabled: !!lat && !!lon,
    staleTime: 30 * 60_000,
  })

export const useFarmWeather = (farmId?: number) =>
  useQuery({
    queryKey: ['farm-weather', farmId],
    queryFn: () => weatherAPI.forFarm(farmId!).then(r => r.data.data),
    enabled: !!farmId,
    staleTime: 30 * 60_000,
  })


// ─── Market Hooks ─────────────────────────────────────────────
export const useMarketPrices = (params?: { state?: string; crop_name?: string }) =>
  useQuery({ queryKey: ['market-prices', params], queryFn: () => marketAPI.prices(params).then(r => r.data.data), staleTime: 30 * 60_000 })

export const useMarketTrend = (cropName: string, state?: string) =>
  useQuery({ queryKey: ['market-trend', cropName, state], queryFn: () => marketAPI.trend(cropName, state).then(r => r.data.data), enabled: !!cropName })


// ─── Scheme Hooks ─────────────────────────────────────────────
export const useSchemes = (params?: { category?: string; state?: string; search?: string }) =>
  useQuery({ queryKey: ['schemes', params], queryFn: () => schemeAPI.list(params).then(r => r.data.data) })

export const useScheme = (id: number) =>
  useQuery({ queryKey: ['scheme', id], queryFn: () => schemeAPI.get(id).then(r => r.data.data), enabled: !!id })


// ─── Chat Hooks ───────────────────────────────────────────────
export const useChatSessions = () =>
  useQuery({ queryKey: ['chat-sessions'], queryFn: () => chatAPI.listSessions().then(r => r.data.data) })

export const useChatMessages = (sessionId: number) =>
  useQuery({ queryKey: ['chat-messages', sessionId], queryFn: () => chatAPI.getMessages(sessionId).then(r => r.data.data), enabled: !!sessionId })

export const useSendMessage = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ sessionId, content, language, is_voice, farm_id }: { sessionId: number; content: string; language?: string; is_voice?: boolean; farm_id?: number }) =>
      chatAPI.sendMessage(sessionId, { content, language, is_voice, farm_id }).then(r => r.data.data),
    onSuccess: (_, { sessionId }) => qc.invalidateQueries({ queryKey: ['chat-messages', sessionId] }),
    onError: (e) => toast.error(extractError(e)),
  })
}


// ─── Analytics Hooks ──────────────────────────────────────────
export const useAnalyticsDashboard = () =>
  useQuery({ queryKey: ['analytics-dashboard'], queryFn: () => analyticsAPI.dashboard().then(r => r.data.data) })

export const useExpenses = (params?: { farm_id?: number }) =>
  useQuery({ queryKey: ['expenses', params], queryFn: () => analyticsAPI.listExpenses(params).then(r => r.data.data) })

export const useAddExpense = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (p: ExpenseCreate) => analyticsAPI.addExpense(p).then(r => r.data.data),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['expenses'] }); toast.success('Expense recorded') },
  })
}


// ─── Notification Hooks ───────────────────────────────────────
export const useNotifications = (unreadOnly?: boolean) =>
  useQuery({ queryKey: ['notifications', unreadOnly], queryFn: () => notificationAPI.list(unreadOnly).then(r => r.data.data), refetchInterval: 60_000 })

export const useMarkAllRead = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: () => notificationAPI.markAllRead(),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['notifications'] }),
  })
}


// ─── Irrigation Hooks ─────────────────────────────────────────
export const useIrrigationSchedule = () =>
  useMutation({ mutationFn: (p: IrrigationRequest) => irrigationAPI.getSchedule(p).then(r => r.data.data) })


// ─── Crop Hooks ───────────────────────────────────────────────
export const useCrops = (params?: { search?: string; season?: string }) =>
  useQuery({ queryKey: ['crops', params], queryFn: () => cropAPI.list(params).then(r => r.data.data) })

export const useCropRecommendation = (farmId?: number) =>
  useQuery({ queryKey: ['crop-recommendation', farmId], queryFn: () => cropAPI.recommendForFarm(farmId!).then(r => r.data.data), enabled: !!farmId })
