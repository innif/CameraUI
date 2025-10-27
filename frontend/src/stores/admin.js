import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'

export const useAdminStore = defineStore('admin', () => {
  // State
  const isMuted = ref(false)
  const obsStatus = ref(null)
  const filesInfo = ref(null)
  const audioCheckResult = ref(null)
  const logs = ref([])
  const loading = ref(false)
  const error = ref(null)

  // Actions
  async function fetchStatus() {
    try {
      loading.value = true
      error.value = null
      const response = await api.admin.getStatus()

      obsStatus.value = response.data.obs
      filesInfo.value = response.data.files

      return response.data
    } catch (err) {
      error.value = err.message
      console.error('Failed to fetch admin status:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function setMute(muted) {
    try {
      loading.value = true
      error.value = null
      const response = await api.admin.setMute(muted)

      if (response.data.success) {
        isMuted.value = response.data.muted
      }

      return response.data
    } catch (err) {
      error.value = err.message
      console.error('Failed to set mute:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function reloadCamera() {
    try {
      loading.value = true
      error.value = null
      const response = await api.admin.reloadCamera()
      return response.data
    } catch (err) {
      error.value = err.message
      console.error('Failed to reload camera:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function setLogoVisibility(visible) {
    try {
      loading.value = true
      error.value = null
      const response = await api.admin.setLogo(visible)
      return response.data
    } catch (err) {
      error.value = err.message
      console.error('Failed to set logo:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function shutdownSystem() {
    try {
      loading.value = true
      error.value = null
      const response = await api.admin.shutdown()
      return response.data
    } catch (err) {
      error.value = err.message
      console.error('Failed to shutdown:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function restartSystem() {
    try {
      loading.value = true
      error.value = null
      const response = await api.admin.restart()
      return response.data
    } catch (err) {
      error.value = err.message
      console.error('Failed to restart:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function checkAudio() {
    try {
      loading.value = true
      error.value = null
      const response = await api.admin.checkAudio()
      audioCheckResult.value = response.data
      return response.data
    } catch (err) {
      error.value = err.message
      console.error('Failed to check audio:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchLogs() {
    try {
      loading.value = true
      error.value = null
      const response = await api.admin.getLogs()
      logs.value = response.data.logs
      return response.data
    } catch (err) {
      error.value = err.message
      console.error('Failed to fetch logs:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteLogs() {
    try {
      loading.value = true
      error.value = null
      const response = await api.admin.deleteLogs()
      logs.value = []
      return response.data
    } catch (err) {
      error.value = err.message
      console.error('Failed to delete logs:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    // State
    isMuted,
    obsStatus,
    filesInfo,
    audioCheckResult,
    logs,
    loading,
    error,
    // Actions
    fetchStatus,
    setMute,
    reloadCamera,
    setLogoVisibility,
    shutdownSystem,
    restartSystem,
    checkAudio,
    fetchLogs,
    deleteLogs
  }
})
