import { useEffect } from 'react'
import { useAuthStore } from '../store/auth'

export function useAuth() {
  const token = useAuthStore((s) => s.token)
  const user = useAuthStore((s) => s.user)
  const login = useAuthStore((s) => s.login)
  const logout = useAuthStore((s) => s.logout)
  const fetchMe = useAuthStore((s) => s.fetchMe)
  const hasRole = useAuthStore((s) => s.hasRole)

  useEffect(() => {
    if (token && !user) {
      fetchMe().catch(() => logout())
    }
  }, [token, user, fetchMe, logout])

  return {
    token,
    user,
    login,
    logout,
    isAuthenticated: Boolean(token),
    hasRole,
  }
}
