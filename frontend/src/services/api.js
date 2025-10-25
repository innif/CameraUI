import axios from 'axios'

// Create axios instance with base configuration
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor for error handling
api.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export default {
  // Recording API - mapped to /api/recordings/*
  recording: {
    getStatus() {
      return api.get('/api/recordings/status')
    },
    start() {
      return api.post('/api/recordings/start')
    },
    stop() {
      return api.post('/api/recordings/stop')
    },
    getCurrent() {
      return api.get('/api/recordings/current')
    },
    getPreview() {
      return api.get('/api/recordings/preview')
    },
    getNextScheduled() {
      return api.get('/api/recordings/next-scheduled')
    }
  },

  // Admin API - mapped to /api/admin/*
  admin: {
    getStatus() {
      return api.get('/api/admin/status')
    },
    setMute(muted) {
      return api.post('/api/admin/mute', { muted })
    },
    reloadCamera() {
      return api.post('/api/admin/camera/reload')
    },
    setLogo(visible) {
      return api.post('/api/admin/logo', { visible })
    },
    shutdown() {
      return api.post('/api/admin/shutdown')
    },
    checkAudio() {
      return api.get('/api/admin/audio/check')
    },
    getLogs() {
      return api.get('/api/admin/logs')
    },
    getLogFile(filename) {
      return api.get(`/api/admin/logs/${filename}`)
    },
    deleteLogs() {
      return api.delete('/api/admin/logs')
    }
  },

  // Videos API - TODO: Check if these routes exist in backend
  videos: {
    getAll() {
      return api.get('/api/recordings/videos')
    },
    getById(id) {
      return api.get(`/api/recordings/videos/${id}`)
    },
    getFrame(id, timestamp) {
      return api.get(`/api/recordings/videos/${id}/frame`, {
        params: { timestamp }
      })
    },
    exportSubclip(id, startTime, endTime) {
      return api.post(`/api/recordings/videos/${id}/export`, {
        start_time: startTime,
        end_time: endTime
      })
    },
    download(filename) {
      return api.get(`/videos/${filename}`, {
        responseType: 'blob'
      })
    },
    delete(id) {
      return api.delete(`/api/recordings/videos/${id}`)
    }
  }
}
