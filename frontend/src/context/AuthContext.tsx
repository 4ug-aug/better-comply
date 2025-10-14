import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { api, clearTokens, setTokens } from '@/api/axios-base'

type User = {
  id: number
  username: string
  email: string
  is_verified: boolean
  is_admin: boolean
}

type AuthContextValue = {
  user: User | null
  loading: boolean
  login: (username: string, password: string) => Promise<void>
  logout: () => void
  refreshMe: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export const useAuth = (): AuthContextValue => {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  const refreshMe = useCallback(async () => {
    try {
      const { data } = await api.get<User>('/auth/me')
      setUser(data)
    } catch {
      setUser(null)
    }
  }, [])

  useEffect(() => {
    ;(async () => {
      setLoading(true)
      await refreshMe()
      setLoading(false)
    })()
  }, [refreshMe])

  const login = useCallback(async (username: string, password: string) => {
    const form = new URLSearchParams()
    form.set('username', username)
    form.set('password', password)
    const { data } = await api.post<{ access_token: string; refresh_token: string }>(
      '/auth/token',
      form,
      { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
    )
    setTokens(data.access_token, data.refresh_token)
    await refreshMe()
  }, [refreshMe])

  const logout = useCallback(() => {
    clearTokens()
    setUser(null)
  }, [])

  const value = useMemo<AuthContextValue>(() => ({ user, loading, login, logout, refreshMe }), [user, loading, login, logout, refreshMe])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}


