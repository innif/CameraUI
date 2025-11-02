import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useRecordingStore = defineStore('recording', () => {
  // State
  const isRecording = ref(false)
  const isConnected = ref(false)
  const currentFile = ref(null)
  const previewImage = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const nextScheduledRecording = ref(null)

  // Computed
  const recordingStatus = computed(() => {
    if (!isConnected.value) return 'Nicht verbunden'
    if (error.value) return 'Fehler'
    if (isRecording.value) return 'Aufnahme läuft'
    return 'Bereit'
  })

  const hasError = computed(() => {
    return !isConnected.value || error.value !== null
  })

  // Actions
  async function fetchStatus() {
    try {
      loading.value = true
      error.value = null
      const response = await api.recording.getStatus()

      const wasRecording = isRecording.value
      isRecording.value = response.data.is_recording
      isConnected.value = response.data.is_connected

      // If recording status changed unexpectedly, log it
      if (wasRecording && !response.data.is_recording) {
        console.warn('Recording stopped unexpectedly')
        currentFile.value = null
      }

      // Update current file if recording
      if (response.data.is_recording && response.data.current_file) {
        currentFile.value = response.data.current_file
      } else if (!response.data.is_recording) {
        currentFile.value = null
      }

      return response.data
    } catch (err) {
      error.value = err.message
      console.error('Failed to fetch recording status:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function startRecording() {
    try {
      loading.value = true
      error.value = null
      const response = await api.recording.start()

      if (response.data.success) {
        isRecording.value = true
        await fetchCurrentFile()
      }

      return response.data
    } catch (err) {
      error.value = err.message
      console.error('Failed to start recording:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function stopRecording() {
    try {
      loading.value = true
      error.value = null
      const response = await api.recording.stop()

      if (response.data.success) {
        isRecording.value = false
        currentFile.value = null
      }

      return response.data
    } catch (err) {
      error.value = err.message
      console.error('Failed to stop recording:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchCurrentFile() {
    try {
      const response = await api.recording.getCurrent()
      currentFile.value = response.data
      return response.data
    } catch (err) {
      console.error('Failed to fetch current file:', err)
      throw err
    }
  }

  async function fetchPreview() {
    try {
      const response = await api.recording.getPreview()

      if (response.data.success && response.data.image) {
        previewImage.value = response.data.image
      }

      return response.data
    } catch (err) {
      console.error('Failed to fetch preview:', err)
      throw err
    }
  }

  async function fetchNextScheduled() {
    try {
      const response = await api.recording.getNextScheduled()
      nextScheduledRecording.value = response.data
      return response.data
    } catch (err) {
      console.error('Failed to fetch next scheduled recording:', err)
      throw err
    }
  }

  return {
    // State
    isRecording,
    isConnected,
    currentFile,
    previewImage,
    loading,
    error,
    nextScheduledRecording,
    // Computed
    recordingStatus,
    hasError,
    // Actions
    fetchStatus,
    startRecording,
    stopRecording,
    fetchCurrentFile,
    fetchPreview,
    fetchNextScheduled
  }
})
