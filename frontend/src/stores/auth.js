import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const isAuthenticated = ref(false)
  const authError = ref(null)

  // Check if user is already authenticated (from sessionStorage)
  const checkAuth = () => {
    const auth = sessionStorage.getItem('auth')
    if (auth === 'true') {
      isAuthenticated.value = true
    }
  }

  // Attempt login with password
  const login = async (password) => {
    authError.value = null

    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ password })
      })

      const data = await response.json()

      if (response.ok && data.success) {
        isAuthenticated.value = true
        sessionStorage.setItem('auth', 'true')
        return true
      } else {
        authError.value = 'Falsches Passwort'
        return false
      }
    } catch (error) {
      authError.value = 'Verbindungsfehler'
      console.error('Login error:', error)
      return false
    }
  }

  // Logout
  const logout = () => {
    isAuthenticated.value = false
    sessionStorage.removeItem('auth')
  }

  // Initialize auth state
  checkAuth()

  return {
    isAuthenticated,
    authError,
    login,
    logout,
    checkAuth
  }
})
