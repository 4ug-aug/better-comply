import React from 'react'
import './App.css'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider, useAuth } from '@/context/AuthContext'
import AppLayout from '@/layouts/AppLayout'
import Login from '@/pages/Login'
import Dashboard from '@/pages/Dashboard'
// Scheduling page kept as redirect route only; not imported to avoid unused warnings
import SubscriptionsPage from '@/features/Subscriptions/pages/SubscriptionsPage'
import SubscriptionDetailPage from '@/features/Subscriptions/pages/SubscriptionDetailPage'
import CreateSubscriptionPage from '@/features/Subscriptions/pages/CreateSubscriptionPage'
import SourcesPage from '@/features/Sources/pages/SourcesPage'
import CreateSourcePage from '@/features/Sources/pages/CreateSourcePage'
import SourceDetailPage from '@/features/Sources/pages/SourceDetailPage'
import ObservabilityPage from '@/features/Observability/pages/ObservabilityPage'


const RequireAuth: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, loading } = useAuth()
  if (loading) return null
  if (!user) return <Navigate to="/login" replace />
  return <>{children}</>
}

function App() {
  return (
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route
              path="/"
              element={
                <RequireAuth>
                  <AppLayout />
                </RequireAuth>
              }
            >
              <Route index element={<Dashboard />} />
              <Route path="/subscriptions" element={<SubscriptionsPage />} />
              <Route path="/subscriptions/new" element={<CreateSubscriptionPage />} />
              <Route path="/subscriptions/:id" element={<SubscriptionDetailPage />} />
              <Route path="/sources" element={<SourcesPage />} />
              <Route path="/sources/new" element={<CreateSourcePage />} />
              <Route path="/sources/:id" element={<SourceDetailPage />} />
              <Route path="/observability" element={<ObservabilityPage />} />
              <Route path="/scheduling" element={<Navigate to="/subscriptions" replace />} />
            </Route>
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
  )
}

export default App
