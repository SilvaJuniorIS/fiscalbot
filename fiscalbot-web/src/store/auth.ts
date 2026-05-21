import { create } from 'zustand'
import api from '../services/api'
import type { User } from '../types'

type AuthState = {
  token: string | null
  user: User | null
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  fetchMe: () => Promise<void>
  hasRole: (...roles: string[]) => boolean
}

export const useAuthStore = create<AuthState>((set, get) => ({
  token: localStorage.getItem('fiscalbot_token'),
  user: null,
  login: async (email, password) => {
    const form = new URLSearchParams({ username: email, password })
    const { data } = await api.post('/api/v1/auth/login', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
    localStorage.setItem('fiscalbot_token', data.access_token)
    set({ token: data.access_token })
    const me = await api.get<User>('/api/v1/auth/me')
    set({ user: me.data })
  },
  logout: () => {
    localStorage.removeItem('fiscalbot_token')
    set({ token: null, user: null })
  },
  fetchMe: async () => {
    const { data } = await api.get<User>('/api/v1/auth/me')
    set({ user: data })
  },
  hasRole: (...roles) => {
    const role = get().user?.role
    return role ? roles.includes(role) : false
  },
}))
