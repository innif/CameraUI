<template>
  <v-container class="container-max">
    <v-row>
      <v-col cols="12">
        <!-- Tabs -->
        <v-tabs
          v-model="activeTab"
          bg-color="transparent"
          class="modern-tabs mb-6"
          slider-color="primary"
        >
          <v-tab value="recording" class="tab-item">
            <v-icon start size="20">mdi-record-circle</v-icon>
            Aufnahme
          </v-tab>
          <v-tab value="archive" class="tab-item">
            <v-icon start size="20">mdi-video-box</v-icon>
            Videoarchiv
          </v-tab>
        </v-tabs>

        <v-window v-model="activeTab">
          <!-- Recording Tab -->
          <v-window-item value="recording">
            <!-- Instructions -->
            <v-expansion-panels class="mb-6 modern-panels" variant="accordion">
              <v-expansion-panel class="info-panel">
                <v-expansion-panel-title class="panel-title">
                  <div class="d-flex align-center">
                    <v-icon color="primary" class="mr-3">mdi-information</v-icon>
                    <span class="font-weight-medium">Anleitung</span>
                  </div>
                </v-expansion-panel-title>
                <v-expansion-panel-text>
                  <div class="instruction-text">
                    <h3 class="instruction-title">Willkommen bei ScheiniCam!</h3>
                    <p class="instruction-description">
                      Dieses System zeichnet automatisch Live-Auftritte auf.
                      Nach deinem Auftritt kannst du dein Video direkt hier herunterladen.
                    </p>
                    <h4 class="instruction-subtitle">So funktioniert's:</h4>
                    <ol class="instruction-list">
                      <li>Die Aufnahme läuft automatisch zu den konfigurierten Zeiten</li>
                      <li>Merke dir Start- und Endzeit deines Auftritts</li>
                      <li>Gehe nach dem Auftritt zum "Videoarchiv"-Tab</li>
                      <li>Wähle den Tag und stelle die Zeiten ein</li>
                      <li>Lade dein Video herunter</li>
                    </ol>
                  </div>
                </v-expansion-panel-text>
              </v-expansion-panel>
            </v-expansion-panels>

            <!-- Connection Status -->
            <v-alert
              v-if="!recordingStore.isConnected"
              type="warning"
              class="mb-6 modern-alert"
              variant="tonal"
              prominent
            >
              <template v-slot:prepend>
                <v-icon size="28">mdi-alert</v-icon>
              </template>
              <div class="font-weight-medium">OBS ist nicht verbunden</div>
              <div class="text-caption mt-1">Bitte warten oder Administrator kontaktieren.</div>
            </v-alert>

            <!-- Recording Status -->
            <v-card class="mb-6 modern-card status-card" elevation="0">
              <v-card-text class="pa-6">
                <div class="d-flex align-center justify-space-between mb-4">
                  <div>
                    <h3 class="status-title">Aufnahmestatus</h3>
                    <p class="status-description mt-1">{{ recordingStore.recordingStatus }}</p>
                  </div>
                  <v-chip
                    :color="recordingStore.isRecording ? 'error' : 'success'"
                    size="large"
                    class="status-chip"
                    variant="flat"
                  >
                    <v-icon start size="20">
                      {{ recordingStore.isRecording ? 'mdi-record-circle' : 'mdi-circle-outline' }}
                    </v-icon>
                    {{ recordingStore.isRecording ? 'Aufnahme läuft' : 'Bereit' }}
                  </v-chip>
                </div>

                <!-- Next Scheduled Recording Info -->
                <div v-if="!recordingStore.isRecording && recordingStore.nextScheduledRecording && recordingStore.nextScheduledRecording.formatted_message" class="next-recording-info">
                  <v-icon color="primary" size="20" class="mr-2">mdi-clock-outline</v-icon>
                  <span class="next-recording-text">
                    {{ recordingStore.nextScheduledRecording.formatted_message }}
                  </span>
                </div>

                <v-divider class="my-4"></v-divider>

                <v-btn
                  color="primary"
                  block
                  size="x-large"
                  class="action-btn"
                  @click="activeTab = 'archive'"
                  variant="flat"
                >
                  <v-icon start>mdi-download</v-icon>
                  Zum Videoarchiv
                </v-btn>
              </v-card-text>
            </v-card>

            <!-- Preview -->
            <v-card class="mb-6 modern-card preview-card" elevation="0">
              <v-card-title class="card-title">
                <v-icon color="primary" class="mr-2">mdi-camera</v-icon>
                Live-Vorschau
              </v-card-title>
              <v-card-text class="pa-4">
                <div v-if="recordingStore.previewImage" class="preview-container">
                  <img
                    :src="recordingStore.previewImage"
                    alt="Kamera-Vorschau"
                    class="preview-image"
                  />
                </div>
                <div v-else class="loading-container">
                  <v-progress-circular
                    indeterminate
                    color="primary"
                    size="48"
                  ></v-progress-circular>
                  <p class="loading-text mt-4">Lade Vorschau...</p>
                </div>
              </v-card-text>
            </v-card>

            <!-- Current Time -->
            <v-card class="modern-card time-card" elevation="0">
              <v-card-text class="text-center pa-8">
                <div class="time-display">{{ currentTime }}</div>
                <p class="time-label mt-2">Aktuelle Uhrzeit</p>
              </v-card-text>
            </v-card>
          </v-window-item>

          <!-- Archive Tab -->
          <v-window-item value="archive">
            <DownloadWizard />
          </v-window-item>
        </v-window>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRecordingStore } from '@/stores/recording'
import DownloadWizard from '@/components/DownloadWizard.vue'

const recordingStore = useRecordingStore()
const activeTab = ref('recording')
const currentTime = ref('')
let timeInterval = null
let previewInterval = null
let statusInterval = null

// Update current time
function updateTime() {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('de-DE', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// Update preview
async function updatePreview() {
  try {
    await recordingStore.fetchPreview()
  } catch (err) {
    console.error('Failed to update preview:', err)
  }
}

// Update status
async function updateStatus() {
  try {
    const wasRecording = recordingStore.isRecording
    await recordingStore.fetchStatus()

    // Check if recording stopped unexpectedly
    if (wasRecording && !recordingStore.isRecording) {
      console.warn('Recording stopped unexpectedly - interface status synchronized')
    }
  } catch (err) {
    console.error('Failed to update status:', err)
  }
}

// Update next scheduled recording
async function updateNextScheduled() {
  try {
    await recordingStore.fetchNextScheduled()
  } catch (err) {
    console.error('Failed to update next scheduled recording:', err)
  }
}

onMounted(async () => {
  // Initial fetch
  await recordingStore.fetchStatus()
  await recordingStore.fetchNextScheduled()
  await updatePreview()
  updateTime()

  // Set up intervals
  timeInterval = setInterval(updateTime, 1000)
  previewInterval = setInterval(updatePreview, 1000)
  statusInterval = setInterval(updateStatus, 2000) // Check status every 2 seconds
  setInterval(updateNextScheduled, 60000) // Update next scheduled every minute
})

onUnmounted(() => {
  if (timeInterval) clearInterval(timeInterval)
  if (previewInterval) clearInterval(previewInterval)
  if (statusInterval) clearInterval(statusInterval)
})
</script>

<style scoped>
/* Page Header */
.page-header {
  text-align: center;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, rgb(var(--v-theme-primary)) 0%, rgb(var(--v-theme-secondary)) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 0.5rem;
}

/* Mobile-responsive title sizing */
@media (max-width: 599px) {
  .page-title {
    font-size: 1.75rem;
  }
}

@media (max-width: 400px) {
  .page-title {
    font-size: 1.5rem;
  }
}

.page-subtitle {
  font-size: 1.1rem;
  opacity: 0.7;
}

@media (max-width: 599px) {
  .page-subtitle {
    font-size: 0.95rem;
  }
}

/* Modern Tabs */
.modern-tabs {
  border-radius: 12px;
  background: rgba(var(--v-theme-surface), 0.6);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(var(--v-theme-primary), 0.1);
}

.modern-tabs :deep(.v-tabs) {
  width: 100%;
}

.modern-tabs :deep(.v-slide-group__content) {
  width: 100%;
}

.tab-item {
  flex: 1;
  border-radius: 8px;
  transition: all 0.3s ease;
  text-transform: none;
  font-weight: 500;
  letter-spacing: 0;
  min-height: 48px;
}

.tab-item :deep(.v-btn__content) {
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Mobile tab optimizations */
@media (max-width: 599px) {
  .tab-item {
    min-height: 44px;
    font-size: 0.9rem;
    padding: 10px 12px;
  }

  .tab-item :deep(.v-icon) {
    font-size: 18px !important;
  }
}

/* Modern Cards */
.modern-card {
  border-radius: 16px;
  border: 1px solid rgba(var(--v-theme-primary), 0.1);
  background: rgba(var(--v-theme-surface), 0.8);
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

/* Only apply hover effects on devices that support hover */
@media (hover: hover) {
  .modern-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(var(--v-theme-primary), 0.15);
  }
}

.card-title {
  font-size: 1.25rem;
  font-weight: 600;
  padding: 1.25rem 1.5rem;
}

/* Mobile card padding adjustments */
@media (max-width: 599px) {
  .card-title {
    font-size: 1.1rem;
    padding: 1rem 1.25rem;
  }
}

/* Time Card */
.time-card {
  background: linear-gradient(135deg, rgba(var(--v-theme-primary), 0.1) 0%, rgba(var(--v-theme-secondary), 0.1) 100%);
}

.time-display {
  font-size: 4rem;
  font-weight: 700;
  background: linear-gradient(135deg, rgb(var(--v-theme-primary)) 0%, rgb(var(--v-theme-secondary)) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -2px;
}

/* Responsive time display */
@media (max-width: 599px) {
  .time-display {
    font-size: 2.5rem;
    letter-spacing: -1px;
  }
}

@media (max-width: 400px) {
  .time-display {
    font-size: 2rem;
  }
}

.time-label {
  font-size: 1rem;
  opacity: 0.7;
  font-weight: 500;
}

@media (max-width: 599px) {
  .time-label {
    font-size: 0.9rem;
  }
}

/* Preview */
.preview-container {
  width: 100%;
  display: flex;
  justify-content: center;
  border-radius: 12px;
  overflow: hidden;
}

.preview-image {
  width: 100%;
  height: auto;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.loading-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 4rem 2rem;
}

.loading-text {
  opacity: 0.7;
  font-weight: 500;
}

/* Status Card */
.status-title {
  font-size: 1.25rem;
  font-weight: 600;
}

.status-description {
  opacity: 0.7;
  font-size: 0.95rem;
}

.status-chip {
  font-weight: 600;
  padding: 0.75rem 1.25rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* Next Recording Info */
.next-recording-info {
  display: flex;
  align-items: center;
  padding: 1rem;
  margin-top: 1rem;
  background: rgba(var(--v-theme-primary), 0.08);
  border-radius: 12px;
  border: 1px solid rgba(var(--v-theme-primary), 0.15);
}

.next-recording-text {
  font-size: 1rem;
  font-weight: 500;
  color: rgb(var(--v-theme-primary));
}

/* Action Button */
.action-btn {
  border-radius: 12px;
  text-transform: none;
  font-weight: 600;
  font-size: 1rem;
  letter-spacing: 0;
  padding: 1.5rem;
  box-shadow: 0 4px 12px rgba(var(--v-theme-primary), 0.3);
  transition: all 0.3s ease;
}

@media (hover: hover) {
  .action-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(var(--v-theme-primary), 0.4);
  }
}

/* Mobile button optimizations */
@media (max-width: 599px) {
  .action-btn {
    font-size: 0.95rem;
    padding: 1.25rem;
  }
}

/* Instructions */
.modern-panels {
  border-radius: 12px;
  overflow: hidden;
}

.info-panel {
  background: rgba(var(--v-theme-surface), 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(var(--v-theme-primary), 0.1);
  border-radius: 12px;
}

.panel-title {
  font-size: 1rem;
}

.instruction-text {
  line-height: 1.8;
  padding: 0.5rem 0;
}

.instruction-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: rgb(var(--v-theme-primary));
}

.instruction-description {
  font-size: 1rem;
  opacity: 0.8;
  margin-bottom: 1.5rem;
}

.instruction-subtitle {
  font-size: 1.15rem;
  font-weight: 600;
  margin-top: 1.5rem;
  margin-bottom: 1rem;
}

.instruction-list {
  margin-left: 1.5rem;
  font-size: 0.95rem;
}

.instruction-list li {
  margin-bottom: 0.75rem;
  padding-left: 0.5rem;
}

/* Modern Alert */
.modern-alert {
  border-radius: 12px;
  border: 1px solid rgba(var(--v-theme-warning), 0.2);
}
</style>
