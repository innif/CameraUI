<template>
  <div>
    <v-stepper v-model="step" :alt-labels="!isMobile" :mobile="isMobile">
      <v-stepper-header>
        <v-stepper-item
          :complete="step > 1"
          :value="1"
          :title="isMobile ? 'Wählen' : 'Aufnahme wählen'"
          icon="mdi-calendar"
        ></v-stepper-item>

        <v-divider></v-divider>

        <v-stepper-item
          :complete="step > 2"
          :value="2"
          :title="isMobile ? 'Start' : 'Startzeit'"
          icon="mdi-clock-start"
        ></v-stepper-item>

        <v-divider></v-divider>

        <v-stepper-item
          :complete="step > 3"
          :value="3"
          :title="isMobile ? 'Ende' : 'Endzeit'"
          icon="mdi-clock-end"
        ></v-stepper-item>

        <v-divider></v-divider>

        <v-stepper-item
          :value="4"
          title="Download"
          icon="mdi-download"
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
              <h3 v-if="!isMobile" class="text-h6 mb-4">Startzeit festlegen</h3>

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
              <h3 v-if="!isMobile" class="text-h6 mb-4">Endzeit festlegen</h3>

              <TimeSelector
                v-if="videosStore.selectedVideo"
                v-model="endTime"
                :video="videosStore.selectedVideo"
                :min-time="startTime"
                @preview="updatePreview"
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
                  Export erfolgreich abgeschlossen!
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
import { ref, computed, onMounted } from 'vue'
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
    // Set endTime to duration if available, otherwise use a safe default
    endTime.value = duration && duration > 0 ? duration : 3600

    // Load initial preview at start time
    await updatePreview(startTime.value)

    step.value = 2
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

onMounted(async () => {
  await videosStore.fetchVideos()
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
</style>
