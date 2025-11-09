<template>
  <div>
    <v-stepper v-model="step" :alt-labels="!isMobile" :mobile="isMobile">
      <v-stepper-header>
        <v-stepper-item
          :complete="step > 1"
          :value="1"
          :title="isMobile ? 'Wählen' : 'Aufnahme wählen'"
          icon="mdi-calendar"
          color="primary"
        ></v-stepper-item>

        <v-divider></v-divider>

        <v-stepper-item
          :complete="step > 2"
          :value="2"
          :title="isMobile ? 'Start' : 'Startzeit'"
          icon="mdi-clock-start"
          color="primary"
        ></v-stepper-item>

        <v-divider></v-divider>

        <v-stepper-item
          :complete="step > 3"
          :value="3"
          :title="isMobile ? 'Ende' : 'Endzeit'"
          icon="mdi-clock-end"
          color="primary"
        ></v-stepper-item>

        <v-divider></v-divider>

        <v-stepper-item
          :value="4"
          title="Download"
          icon="mdi-download"
          color="primary"
        ></v-stepper-item>
      </v-stepper-header>

      <v-stepper-window>
        <!-- Step 1: Select Video -->
        <v-stepper-window-item :value="1">
          <v-card>
            <v-card-text :class="isMobile ? 'pa-3' : ''">
              <h3 v-if="!isMobile" class="text-h6 mb-4">Wähle eine Aufnahme</h3>

              <v-select
                v-model="selectedVideoId"
                :items="videoOptions"
                label="Aufnahme"
                item-title="displayName"
                item-value="id"
                variant="outlined"
                :loading="videosStore.loading"
              ></v-select>

              <v-alert v-if="!videoOptions.length" type="info" :class="isMobile ? 'mt-2' : 'mt-4'">
                Keine Aufnahmen verfügbar
              </v-alert>
            </v-card-text>
            <v-card-actions :class="isMobile ? 'pa-2' : ''">
              <v-btn
                variant="text"
                :disabled="!selectedVideoId"
                @click="downloadFullShow"
                :size="isMobile ? 'small' : 'default'"
              >
                <v-icon start>mdi-download</v-icon>
                Ganze Show herunterladen
              </v-btn>
              <v-spacer></v-spacer>
              <v-btn
                color="primary"
                :disabled="!selectedVideoId"
                @click="selectVideo"
                :size="isMobile ? 'default' : 'large'"
                variant="elevated"
                class="weiter-btn"
              >
                <v-icon start>mdi-arrow-right</v-icon>
                Weiter
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-stepper-window-item>

        <!-- Step 2: Set Start Time -->
        <v-stepper-window-item :value="2">
          <v-card>
            <v-card-text :class="isMobile ? 'pa-3' : ''">
              <h3 class="text-h6 mb-4">Startzeit festlegen</h3>

              <TimeSelector
                v-if="videosStore.selectedVideo"
                v-model="startTime"
                :video="videosStore.selectedVideo"
                @preview="updatePreview"
              />
            </v-card-text>
            <v-card-actions :class="isMobile ? 'pa-2' : ''">
              <v-btn @click="step = 1" :size="isMobile ? 'small' : 'default'" variant="text">
                <v-icon start>mdi-arrow-left</v-icon>
                Zurück
              </v-btn>
              <v-spacer></v-spacer>
              <v-btn
                color="primary"
                @click="step = 3"
                :size="isMobile ? 'default' : 'large'"
                variant="elevated"
                class="weiter-btn"
              >
                <v-icon start>mdi-arrow-right</v-icon>
                Weiter
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-stepper-window-item>

        <!-- Step 3: Set End Time -->
        <v-stepper-window-item :value="3">
          <v-card>
            <v-card-text :class="isMobile ? 'pa-3' : ''">
              <h3 class="text-h6 mb-4">Endzeit festlegen</h3>

              <div v-if="videosStore.selectedVideo" class="chip-container" :class="isMobile ? 'mb-2' : 'mb-4'">
                <!-- Duration Chip -->
                <v-chip color="success" :size="isMobile ? 'default' : 'large'" class="chip-item">
                  <v-icon start>mdi-timer</v-icon>
                  Dauer: {{ formatDuration(endTime - startTime) }}
                </v-chip>

                <!-- Time Chip -->
                <v-chip color="primary" :size="isMobile ? 'default' : 'large'" class="chip-item">
                  <v-icon start>mdi-clock</v-icon>
                  {{ formatTimeAsClock(endTime, videosStore.selectedVideo) }}
                </v-chip>
              </div>

              <TimeSelector
                v-if="videosStore.selectedVideo"
                v-model="endTime"
                :video="videosStore.selectedVideo"
                :min-time="startTime"
                @preview="updatePreview"
                :hide-time-chip="true"
              />
            </v-card-text>
            <v-card-actions :class="isMobile ? 'pa-2' : ''">
              <v-btn @click="step = 2" :size="isMobile ? 'small' : 'default'" variant="text">
                <v-icon start>mdi-arrow-left</v-icon>
                Zurück
              </v-btn>
              <v-spacer></v-spacer>
              <v-btn
                color="primary"
                @click="step = 4"
                :size="isMobile ? 'default' : 'large'"
                variant="elevated"
                class="weiter-btn"
              >
                <v-icon start>mdi-arrow-right</v-icon>
                Weiter
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-stepper-window-item>

        <!-- Step 4: Export & Download -->
        <v-stepper-window-item :value="4">
          <v-card>
            <v-card-text :class="isMobile ? 'pa-3' : ''">
              <h3 v-if="!isMobile" class="text-h6 mb-4">Export und Download</h3>

              <v-alert v-if="!videosStore.exportedFile" type="info" :class="isMobile ? 'mb-2' : 'mb-4'">
                <p :class="isMobile ? 'mb-1' : 'mb-2'">
                  <strong>Dauer:</strong> {{ formatDuration(endTime - startTime) }}
                </p>
                <p>
                  Der Export kann bis zu 2 Minuten dauern.
                  Bitte habe etwas Geduld.
                </p>
              </v-alert>

              <div v-if="videosStore.exporting" class="text-center" :class="isMobile ? 'py-4' : 'py-8'">
                <v-progress-circular
                  indeterminate
                  :size="isMobile ? 48 : 64"
                  color="primary"
                ></v-progress-circular>
                <p :class="isMobile ? 'mt-2' : 'mt-4'">Exportiere Video...</p>
              </div>

              <div v-else-if="videosStore.exportedFile">
                <v-alert type="success" :class="isMobile ? 'mb-2' : 'mb-4'">
                  Video kann jetzt heruntergeladen werden
                </v-alert>

                <v-list>
                  <v-list-item>
                    <template #prepend>
                      <v-icon>mdi-file-video</v-icon>
                    </template>
                    <v-list-item-title>{{ videosStore.exportedFile.filename }}</v-list-item-title>
                    <v-list-item-subtitle>
                      Größe: {{ videosStore.formatFileSize(videosStore.exportedFile.size) }}
                    </v-list-item-subtitle>
                  </v-list-item>
                </v-list>

                <v-btn
                  color="success"
                  block
                  :size="isMobile ? 'default' : 'large'"
                  :class="isMobile ? 'mt-2' : 'mt-4'"
                  @click="downloadFile"
                  :disabled="downloading"
                  :loading="downloading"
                >
                  <v-icon start>mdi-download</v-icon>
                  {{ downloading ? 'Download wird gestartet...' : 'Video herunterladen' }}
                </v-btn>

                <v-alert type="info" :class="isMobile ? 'mt-2' : 'mt-4'" density="compact">
                  <small>
                    Hinweis: Stelle sicher, dass du mit dem WLAN verbunden bist.
                    Der Download kann je nach Dateigröße einige Zeit dauern.
                    {{ downloading ? ' Der Download läuft im Hintergrund - bitte warte, bis der Browser den Download startet.' : '' }}
                  </small>
                </v-alert>
              </div>

              <v-btn
                v-else
                color="primary"
                block
                :size="isMobile ? 'default' : 'large'"
                @click="exportVideo"
              >
                <v-icon start>mdi-export</v-icon>
                Video exportieren
              </v-btn>
            </v-card-text>
            <v-card-actions :class="isMobile ? 'pa-2' : ''">
              <v-btn @click="resetWizard" :size="isMobile ? 'small' : 'default'">Neue Auswahl</v-btn>
              <v-spacer></v-spacer>
            </v-card-actions>
          </v-card>
        </v-stepper-window-item>
      </v-stepper-window>
    </v-stepper>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useDisplay } from 'vuetify'
import { useVideosStore } from '@/stores/videos'
import TimeSelector from '@/components/TimeSelector.vue'

const videosStore = useVideosStore()
const { mobile } = useDisplay()
const isMobile = computed(() => mobile.value)

const step = ref(1)
const selectedVideoId = ref(null)
const startTime = ref(0)
const endTime = ref(0)
const downloading = ref(false)
const downloadProgress = ref(0)

const videoOptions = computed(() => {
  return videosStore.videosList
})

async function selectVideo() {
  if (!selectedVideoId.value) return

  await videosStore.selectVideo(selectedVideoId.value)

  if (videosStore.selectedVideo) {
    // Initialize times
    // Use the actual duration from video file (backend calculates it even for recording videos)
    const duration = videosStore.selectedVideo.duration
    startTime.value = 0

    // Set endTime to start + 8 minutes (480 seconds), but not exceeding the video duration
    const eightMinutes = 480
    if (duration && duration > 0) {
      endTime.value = Math.min(eightMinutes, duration)
    } else {
      endTime.value = eightMinutes
    }

    // Switch to step 2 first, then load preview (so loading animation is visible)
    step.value = 2

    // Load initial preview at start time (async, shows loading animation)
    updatePreview(startTime.value)
  }
}

async function downloadFullShow() {
  if (!selectedVideoId.value) return

  try {
    downloading.value = true

    // Use the video ID directly to download the original file
    // The backend endpoint is: GET /api/recordings/videos/{video_id}/download
    const baseURL = import.meta.env.VITE_API_BASE_URL || ''
    const downloadUrl = `${baseURL}/api/recordings/videos/${selectedVideoId.value}/download`

    // Create a hidden link and trigger download
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = `${selectedVideoId.value}.mp4`
    link.style.display = 'none'
    document.body.appendChild(link)
    link.click()

    // Clean up after a short delay
    setTimeout(() => {
      document.body.removeChild(link)
    }, 100)
  } catch (err) {
    console.error('Download failed:', err)
  } finally {
    downloading.value = false
  }
}

async function updatePreview(timestamp) {
  if (!videosStore.selectedVideo) return
  await videosStore.fetchFrame(videosStore.selectedVideo.id, timestamp)
}

async function exportVideo() {
  if (!videosStore.selectedVideo) return

  try {
    await videosStore.exportSubclip(
      videosStore.selectedVideo.id,
      startTime.value,
      endTime.value
    )
  } catch (err) {
    console.error('Export failed:', err)
  }
}

async function downloadFile() {
  if (!videosStore.exportedFile) return

  try {
    downloading.value = true
    downloadProgress.value = 0
    await videosStore.downloadVideo(videosStore.exportedFile.filename)
    downloading.value = false
    downloadProgress.value = 100
  } catch (err) {
    console.error('Download failed:', err)
    downloading.value = false
  }
}

function resetWizard() {
  step.value = 1
  selectedVideoId.value = null
  startTime.value = 0
  endTime.value = 0
  downloading.value = false
  downloadProgress.value = 0
  videosStore.clearExportedFile()
}

function formatDuration(seconds) {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')} Min`
}

function formatTimeAsClock(seconds, video) {
  // Get the video start time and add the offset
  const videoStartTime = new Date(video.start_time)
  const actualTime = new Date(videoStartTime.getTime() + seconds * 1000)

  // Format as HH:MM:SS
  const hrs = actualTime.getHours().toString().padStart(2, '0')
  const mins = actualTime.getMinutes().toString().padStart(2, '0')
  const secs = actualTime.getSeconds().toString().padStart(2, '0')

  return `${hrs}:${mins}:${secs} Uhr`
}

// Watch for changes to startTime and update endTime accordingly
watch(startTime, (newStartTime) => {
  if (videosStore.selectedVideo) {
    const duration = videosStore.selectedVideo.duration
    const eightMinutes = 480
    const proposedEndTime = newStartTime + eightMinutes

    // Only update endTime if it would still be valid
    if (duration && duration > 0) {
      endTime.value = Math.min(proposedEndTime, duration)
    } else {
      endTime.value = proposedEndTime
    }
  }
})

// Watch for step changes and update preview when entering step 3 (Endzeit)
watch(step, async (newStep) => {
  if (newStep === 3 && videosStore.selectedVideo) {
    // Automatically load preview for the current endTime
    await updatePreview(endTime.value)
  }
})

onMounted(async () => {
  await videosStore.fetchVideos()

  // Automatically select the newest recording
  if (videoOptions.value.length > 0) {
    selectedVideoId.value = videoOptions.value[0].id
  }
})
</script>

<style scoped>
/* Highlight the Weiter (Next) button */
.weiter-btn {
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(var(--v-theme-primary), 0.4) !important;
}

@media (hover: hover) {
  .weiter-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(var(--v-theme-primary), 0.5) !important;
  }
}

/* Chip container with responsive wrapping */
.chip-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.chip-item {
  flex: 0 0 auto;
}

/* Only stack chips vertically on very small screens where they don't fit side by side */
@media (max-width: 380px) {
  .chip-container {
    flex-direction: column;
    align-items: flex-start;
  }

  .chip-item {
    width: 100%;
  }
}
</style>
