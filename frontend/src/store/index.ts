/**
 * Zustand Auth Store — global user state
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { UserOut } from '../types'

interface AuthState {
  user: UserOut | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean

  setAuth: (user: UserOut, access: string, refresh: string) => void
  updateUser: (user: Partial<UserOut>) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,

      setAuth: (user, accessToken, refreshToken) => {
        localStorage.setItem('rootgs_access_token', accessToken)
        localStorage.setItem('rootgs_refresh_token', refreshToken)
        set({ user, accessToken, refreshToken, isAuthenticated: true })
      },

      updateUser: (partial) =>
        set((state) => ({
          user: state.user ? { ...state.user, ...partial } : null,
        })),

      logout: () => {
        localStorage.removeItem('rootgs_access_token')
        localStorage.removeItem('rootgs_refresh_token')
        set({ user: null, accessToken: null, refreshToken: null, isAuthenticated: false })
      },
    }),
    {
      name: 'rootgs-auth',
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)

/**
 * App-level store (theme, sidebar, notifications)
 */

interface AppState {
  theme: 'light' | 'dark'
  sidebarOpen: boolean
  unreadNotifications: number

  toggleTheme: () => void
  toggleSidebar: () => void
  setSidebarOpen: (open: boolean) => void
  setUnreadNotifications: (count: number) => void
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      theme: 'light',
      sidebarOpen: true,
      unreadNotifications: 0,

      toggleTheme: () =>
        set((state) => {
          const newTheme = state.theme === 'light' ? 'dark' : 'light'
          document.documentElement.setAttribute('data-theme', newTheme)
          return { theme: newTheme }
        }),

      toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
      setSidebarOpen: (open) => set({ sidebarOpen: open }),
      setUnreadNotifications: (count) => set({ unreadNotifications: count }),
    }),
    {
      name: 'rootgs-app',
      partialize: (state) => ({ theme: state.theme }),
    }
  )
)
