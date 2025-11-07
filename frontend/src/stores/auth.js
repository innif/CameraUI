import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const isAuthenticated = ref(false)
  const authError = ref(null)
  const loginCooldown = ref(0)
  const failedAttempts = ref(0)
  let cooldownTimer = null

  // Check if user is already authenticated (from sessionStorage or localStorage)
  const checkAuth = () => {
    const sessionAuth = sessionStorage.getItem('auth')
    const localAuth = localStorage.getItem('auth')
    if (sessionAuth === 'true' || localAuth === 'true') {
      isAuthenticated.value = true
    }
  }

  // Start cooldown timer
  const startCooldown = (seconds) => {
    loginCooldown.value = seconds

    // Clear existing timer if any
    if (cooldownTimer) {
      clearInterval(cooldownTimer)
    }

    cooldownTimer = setInterval(() => {
      loginCooldown.value -= 1
      if (loginCooldown.value <= 0) {
        clearInterval(cooldownTimer)
        cooldownTimer = null
      }
    }, 1000)
  }

  // Calculate cooldown duration based on failed attempts
  const getCooldownDuration = () => {
    if (failedAttempts.value === 0) return 0
    if (failedAttempts.value === 1) return 2
    if (failedAttempts.value === 2) return 5
    if (failedAttempts.value === 3) return 10
    return 30 // After 4+ failed attempts
  }

  // Attempt login with password
  const login = async (password, rememberMe = false) => {
    // Check if in cooldown period
    if (loginCooldown.value > 0) {
      authError.value = `Bitte warte ${loginCooldown.value} Sekunden`
      return false
    }

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

        // Reset failed attempts on successful login
        failedAttempts.value = 0

        // Store auth based on "remember me" preference
        if (rememberMe) {
          localStorage.setItem('auth', 'true')
          localStorage.setItem('rememberMe', 'true')
        } else {
          sessionStorage.setItem('auth', 'true')
        }

        return true
      } else {
        // Increment failed attempts
        failedAttempts.value += 1

        // Start cooldown
        const cooldownDuration = getCooldownDuration()
        if (cooldownDuration > 0) {
          startCooldown(cooldownDuration)
          authError.value = `Falsches Passwort. Warte ${cooldownDuration} Sekunden bis zum nächsten Versuch.`
        } else {
          authError.value = 'Falsches Passwort'
        }

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
    loginCooldown,
    failedAttempts,
    login,
    logout,
    checkAuth
  }
})
