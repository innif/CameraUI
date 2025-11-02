import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const isAuthenticated = ref(false)
  const authError = ref(null)

  // Check if user is already authenticated (from sessionStorage or localStorage)
  const checkAuth = () => {
    const sessionAuth = sessionStorage.getItem('auth')
    const localAuth = localStorage.getItem('auth')
    if (sessionAuth === 'true' || localAuth === 'true') {
      isAuthenticated.value = true
    }
  }

  // Attempt login with password
  const login = async (password, rememberMe = false) => {
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

        // Store auth based on "remember me" preference
        if (rememberMe) {
          localStorage.setItem('auth', 'true')
          localStorage.setItem('rememberMe', 'true')
        } else {
          sessionStorage.setItem('auth', 'true')
        }

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
    localStorage.removeItem('auth')
    localStorage.removeItem('rememberMe')
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
