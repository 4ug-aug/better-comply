import axios from 'axios'
import type { CreateClientConfig } from '@/queries/client.gen';

const ACCESS_KEY = 'bc_access_token'
const REFRESH_KEY = 'bc_refresh_token'

export const getAccessToken = (): string => localStorage.getItem(ACCESS_KEY) || ''
export const getRefreshToken = (): string => localStorage.getItem(REFRESH_KEY) || ''
export const setTokens = (access: string, refresh: string): void => {
  localStorage.setItem(ACCESS_KEY, access)
  localStorage.setItem(REFRESH_KEY, refresh)
}
export const clearTokens = (): void => {
  localStorage.removeItem(ACCESS_KEY)
  localStorage.removeItem(REFRESH_KEY)
}

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost/api',
})

api.interceptors.request.use((config) => {
  const url = config.url || ''
  const isPublicAuthEndpoint =
    url.startsWith('/auth/token') ||
    url.startsWith('/auth/refresh') ||
    url.startsWith('/auth/register') ||
    url.startsWith('/auth/verify-email')

  if (!isPublicAuthEndpoint) {
    const token = getAccessToken()
    if (token) {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      ;(config.headers as any).Authorization = `Bearer ${token}`
    }
  }
  return config
})

let isRefreshing = false
api.interceptors.response.use(
  (r) => r,
  async (error) => {
    const original = error.config as typeof error.config & { _retry?: boolean }
    if (error.response?.status === 401 && !original._retry && getRefreshToken()) {
      if (isRefreshing) throw error
      isRefreshing = true
      try {
        const { data } = await api.post('/auth/refresh', {
          refresh_token: getRefreshToken(),
        })
        setTokens(data.access_token, data.refresh_token)
        original._retry = true
        return api.request(original)
      } catch (_) {
        clearTokens()
        window.location.assign('/login')
        throw error
      } finally {
        isRefreshing = false
      }
    }
    throw error
  }
)

export const createClientConfig: CreateClientConfig = (config) => ({
  ...config,
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost/api',
  axios: api,
});

