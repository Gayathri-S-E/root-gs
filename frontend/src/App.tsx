import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useEffect } from 'react'
import { useAuthStore, useAppStore } from './store'

// Layout
import AppLayout from './components/Layout/AppLayout'

// Auth Pages
import LoginPage from './custom-pages/auth/LoginPage'
import RegisterPage from './custom-pages/auth/RegisterPage'
import ForgotPasswordPage from './custom-pages/auth/ForgotPasswordPage'

// App Pages
import DashboardPage from './custom-pages/dashboard/DashboardPage'
import FarmListPage from './custom-pages/farm/FarmListPage'
import FarmDetailPage from './custom-pages/farm/FarmDetailPage'
import CreateFarmPage from './custom-pages/farm/CreateFarmPage'
import CropDoctorPage from './custom-pages/crop-doctor/CropDoctorPage'
import ChatbotPage from './custom-pages/chatbot/ChatbotPage'
import WeatherPage from './custom-pages/weather/WeatherPage'
import IrrigationPage from './custom-pages/irrigation/IrrigationPage'
import MarketPage from './custom-pages/market/MarketPage'
import SchemesPage from './custom-pages/schemes/SchemesPage'
import AnalyticsPage from './custom-pages/analytics/AnalyticsPage'
import ProfilePage from './custom-pages/profile/ProfilePage'
import AdminPage from './custom-pages/admin/AdminPage'


function PrivateRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore(s => s.isAuthenticated)
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />
}

function PublicRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore(s => s.isAuthenticated)
  return isAuthenticated ? <Navigate to="/dashboard" replace /> : <>{children}</>
}

export default function App() {
  const theme = useAppStore(s => s.theme)

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
  }, [theme])

  return (
    <BrowserRouter>
      <Routes>
        {/* Public Routes */}
        <Route path="/login"    element={<PublicRoute><LoginPage /></PublicRoute>} />
        <Route path="/register" element={<PublicRoute><RegisterPage /></PublicRoute>} />
        <Route path="/forgot-password" element={<PublicRoute><ForgotPasswordPage /></PublicRoute>} />

        {/* Protected Routes */}
        <Route path="/" element={<PrivateRoute><AppLayout /></PrivateRoute>}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard"  element={<DashboardPage />} />
          <Route path="farms"      element={<FarmListPage />} />
          <Route path="farms/new"  element={<CreateFarmPage />} />
          <Route path="farms/:id"  element={<FarmDetailPage />} />
          <Route path="crop-doctor"  element={<CropDoctorPage />} />
          <Route path="chatbot"      element={<ChatbotPage />} />
          <Route path="weather"      element={<WeatherPage />} />
          <Route path="irrigation"   element={<IrrigationPage />} />
          <Route path="market"       element={<MarketPage />} />
          <Route path="schemes"      element={<SchemesPage />} />
          <Route path="analytics"    element={<AnalyticsPage />} />
          <Route path="profile"      element={<ProfilePage />} />
          <Route path="admin"        element={<AdminPage />} />
        </Route>

        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
