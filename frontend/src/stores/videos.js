import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useVideosStore = defineStore('videos', () => {
  // State
  const videos = ref([])
  const selectedVideo = ref(null)
  const previewFrame = ref(null)
  const exportedFile = ref(null)
  const loading = ref(false)
  const exporting = ref(false)
  const error = ref(null)

  // Computed
  const videosList = computed(() => {
    return videos.value.map(video => ({
      ...video,
      displayName: formatVideoName(video)
    }))
  })

  // Helper functions
  function formatVideoName(video) {
    if (!video || !video.start_time) return 'Unbekannt'

    const date = new Date(video.start_time)
    const dateStr = date.toLocaleDateString('de-DE')
    const timeStr = date.toLocaleTimeString('de-DE', {
      hour: '2-digit',
      minute: '2-digit'
    })

    return `${dateStr} - ${timeStr} Uhr`
  }

  function formatFileSize(bytes) {
    if (!bytes) return '0 B'

    const units = ['B', 'KB', 'MB', 'GB', 'TB']
    let size = bytes
    let unitIndex = 0

    while (size >= 1024 && unitIndex < units.length - 1) {
      size /= 1024
      unitIndex++
    }

    return `${size.toFixed(2)} ${units[unitIndex]}`
  }

  // Actions
  async function fetchVideos() {
    try {
      loading.value = true
      error.value = null
      const response = await api.videos.getAll()
      videos.value = response.data
      return response.data
    } catch (err) {
      error.value = err.message
      console.error('Failed to fetch videos:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function selectVideo(videoId) {
    try {
      loading.value = true
      error.value = null
      const response = await api.videos.getById(videoId)
      selectedVideo.value = response.data
      return response.data
    } catch (err) {
      error.value = err.message
      console.error('Failed to select video:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchFrame(videoId, timestamp) {
    try {
      const response = await api.videos.getFrame(videoId, timestamp)

      if (response.data.success && response.data.frame) {
        previewFrame.value = response.data.frame
      }

      return response.data
    } catch (err) {
      console.error('Failed to fetch frame:', err)
      throw err
    }
  }

  async function exportSubclip(videoId, startTime, endTime) {
    try {
      exporting.value = true
      error.value = null

      const response = await api.videos.exportSubclip(videoId, startTime, endTime)

      if (response.data.success) {
        exportedFile.value = response.data.file
      }

      return response.data
    } catch (err) {
      error.value = err.message
      console.error('Failed to export subclip:', err)
      throw err
    } finally {
      exporting.value = false
    }
  }

  async function downloadVideo(filename) {
    try {
      const response = await api.videos.download(filename)

      // Create blob and trigger download
      const blob = new Blob([response.data])
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)

      return true
    } catch (err) {
      error.value = err.message
      console.error('Failed to download video:', err)
      throw err
    }
  }

  async function deleteVideo(videoId) {
    try {
      loading.value = true
      error.value = null
      const response = await api.videos.delete(videoId)

      // Remove from local list
      videos.value = videos.value.filter(v => v.id !== videoId)

      return response.data
    } catch (err) {
      error.value = err.message
      console.error('Failed to delete video:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  function clearExportedFile() {
    exportedFile.value = null
  }

  return {
    // State
    videos,
    selectedVideo,
    previewFrame,
    exportedFile,
    loading,
    exporting,
    error,
    // Computed
    videosList,
    // Actions
    fetchVideos,
    selectVideo,
    fetchFrame,
    exportSubclip,
    downloadVideo,
    deleteVideo,
    clearExportedFile,
    // Helpers
    formatFileSize
  }
})
