<template>
  <v-container class="container-max">
    <v-row>
      <v-col cols="12">
        <h1 class="admin-title mb-4">Administration</h1>

        <!-- OBS Connection Status -->
        <v-alert
          :type="adminStore.obsStatus?.is_connected ? 'success' : 'warning'"
          class="mb-4"
          prominent
        >
          <div class="d-flex align-center">
            <v-progress-circular
              v-if="!adminStore.obsStatus?.is_connected"
              indeterminate
              size="24"
              class="mr-3"
            ></v-progress-circular>
            <v-icon v-else start>mdi-check-circle</v-icon>
            <span>
              {{ adminStore.obsStatus?.is_connected ? 'OBS verbunden' : 'OBS nicht verbunden' }}
            </span>
          </div>
        </v-alert>

        <!-- Mute Controls -->
        <v-card class="mb-4">
          <v-card-title>
            <v-icon start>mdi-microphone</v-icon>
            Aufnahmesteuerung
          </v-card-title>
          <v-card-text>
            <v-chip
              v-if="adminStore.isMuted"
              color="warning"
              class="mb-4"
              size="large"
            >
              <v-icon start>mdi-microphone-off</v-icon>
              Aufnahme ist stummgeschaltet
            </v-chip>

            <v-row>
              <v-col cols="12" md="6">
                <v-btn
                  color="error"
                  block
                  size="x-large"
                  :loading="adminStore.loading"
                  @click="adminStore.setMute(true)"
                >
                  <v-icon start>mdi-microphone-off</v-icon>
                  Stummschalten
                </v-btn>
              </v-col>
              <v-col cols="12" md="6">
                <v-btn
                  color="success"
                  block
                  size="x-large"
                  :loading="adminStore.loading"
                  @click="adminStore.setMute(false)"
                >
                  <v-icon start>mdi-microphone</v-icon>
                  Aufnahme aktivieren
                </v-btn>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <!-- Preview Section -->
        <v-expansion-panels class="mb-4">
          <v-expansion-panel>
            <v-expansion-panel-title>
              <v-icon start>mdi-camera</v-icon>
              Kamera-Vorschau
            </v-expansion-panel-title>
            <v-expansion-panel-text>
              <PreviewImage />

              <v-btn
                color="primary"
                block
                class="mt-4"
                :loading="adminStore.loading"
                @click="adminStore.reloadCamera()"
              >
                <v-icon start>mdi-reload</v-icon>
                Kamera neu laden
              </v-btn>
            </v-expansion-panel-text>
          </v-expansion-panel>
        </v-expansion-panels>

        <!-- Manual Recording Controls -->
        <v-card class="mb-4">
          <v-card-title>
            <v-icon start>mdi-record</v-icon>
            Manuelle Aufnahme
          </v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="12" md="6">
                <v-btn
                  color="success"
                  block
                  size="large"
                  :loading="recordingStore.loading"
                  :disabled="recordingStore.isRecording"
                  @click="recordingStore.startRecording()"
                >
                  <v-icon start>mdi-record</v-icon>
                  Aufnahme starten
                </v-btn>
              </v-col>
              <v-col cols="12" md="6">
                <v-btn
                  color="error"
                  block
                  size="large"
                  :loading="recordingStore.loading"
                  :disabled="!recordingStore.isRecording"
                  @click="recordingStore.stopRecording()"
                >
                  <v-icon start>mdi-stop</v-icon>
                  Aufnahme stoppen
                </v-btn>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <!-- Advanced Functions -->
        <v-card class="mb-4">
          <v-card-title>
            <v-icon start>mdi-cog</v-icon>
            Erweiterte Funktionen
          </v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="12" md="6">
                <v-btn
                  color="info"
                  block
                  :loading="adminStore.loading"
                  @click="adminStore.setLogoVisibility(true)"
                >
                  <v-icon start>mdi-image</v-icon>
                  Logo anzeigen
                </v-btn>
              </v-col>
              <v-col cols="12" md="6">
                <v-btn
                  color="info"
                  block
                  :loading="adminStore.loading"
                  @click="adminStore.setLogoVisibility(false)"
                >
                  <v-icon start>mdi-image-off</v-icon>
                  Logo ausblenden
                </v-btn>
              </v-col>
            </v-row>

            <v-divider class="my-4"></v-divider>

            <v-btn
              color="error"
              block
              :loading="adminStore.loading"
              @click="confirmShutdown"
            >
              <v-icon start>mdi-power</v-icon>
              Computer herunterfahren
            </v-btn>
          </v-card-text>
        </v-card>

        <!-- Video Management -->
        <v-card class="mb-4">
          <v-card-title>
            <v-icon start>mdi-video-box</v-icon>
            Video-Verwaltung
          </v-card-title>
          <v-card-text>
            <v-list v-if="videosStore.videos.length">
              <v-list-item
                v-for="video in videosStore.videos"
                :key="video.id"
              >
                <template #prepend>
                  <v-icon>mdi-file-video</v-icon>
                </template>
                <v-list-item-title>{{ formatVideoName(video) }}</v-list-item-title>
                <v-list-item-subtitle>
                  {{ video.filename }}
                </v-list-item-subtitle>
                <template #append>
                  <v-btn
                    icon
                    size="small"
                    color="error"
                    @click="deleteVideo(video.id)"
                  >
                    <v-icon>mdi-delete</v-icon>
                  </v-btn>
                </template>
              </v-list-item>
            </v-list>
            <v-alert v-else type="info">
              Keine Videos vorhanden
            </v-alert>
          </v-card-text>
        </v-card>

        <!-- Log Management -->
        <v-card>
          <v-card-title>
            <v-icon start>mdi-text-box</v-icon>
            Log-Dateien
          </v-card-title>
          <v-card-text>
            <v-btn
              color="primary"
              class="mb-4"
              @click="adminStore.fetchLogs()"
            >
              <v-icon start>mdi-refresh</v-icon>
              Logs aktualisieren
            </v-btn>

            <v-btn
              color="error"
              class="mb-4 ml-2"
              :loading="adminStore.loading"
              @click="confirmDeleteLogs"
            >
              <v-icon start>mdi-delete</v-icon>
              Alle Logs löschen
            </v-btn>

            <v-list v-if="adminStore.logs.length">
              <v-list-item
                v-for="log in adminStore.logs"
                :key="log.filename"
              >
                <template #prepend>
                  <v-icon>mdi-file-document</v-icon>
                </template>
                <v-list-item-title>{{ log.filename }}</v-list-item-title>
                <v-list-item-subtitle>
                  {{ formatFileSize(log.size) }} - {{ formatDate(log.modified) }}
                </v-list-item-subtitle>
              </v-list-item>
            </v-list>
            <v-alert v-else type="info">
              Keine Log-Dateien vorhanden
            </v-alert>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Shutdown Confirmation Dialog -->
    <v-dialog v-model="showShutdownDialog" max-width="500">
      <v-card>
        <v-card-title>Computer herunterfahren?</v-card-title>
        <v-card-text>
          Möchtest du den Computer wirklich herunterfahren?
          Diese Aktion kann nicht rückgängig gemacht werden.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="showShutdownDialog = false">Abbrechen</v-btn>
          <v-btn color="error" @click="shutdown">Herunterfahren</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Delete Logs Confirmation Dialog -->
    <v-dialog v-model="showDeleteLogsDialog" max-width="500">
      <v-card>
        <v-card-title>Alle Logs löschen?</v-card-title>
        <v-card-text>
          Möchtest du wirklich alle Log-Dateien löschen?
          Diese Aktion kann nicht rückgängig gemacht werden.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="showDeleteLogsDialog = false">Abbrechen</v-btn>
          <v-btn color="error" @click="deleteLogs">Löschen</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAdminStore } from '@/stores/admin'
import { useRecordingStore } from '@/stores/recording'
import { useVideosStore } from '@/stores/videos'
import PreviewImage from '@/components/PreviewImage.vue'

const adminStore = useAdminStore()
const recordingStore = useRecordingStore()
const videosStore = useVideosStore()

const showShutdownDialog = ref(false)
const showDeleteLogsDialog = ref(false)

function confirmShutdown() {
  showShutdownDialog.value = true
}

async function shutdown() {
  showShutdownDialog.value = false
  await adminStore.shutdownSystem()
}

function confirmDeleteLogs() {
  showDeleteLogsDialog.value = true
}

async function deleteLogs() {
  showDeleteLogsDialog.value = false
  await adminStore.deleteLogs()
}

async function deleteVideo(videoId) {
  if (confirm('Video wirklich löschen?')) {
    await videosStore.deleteVideo(videoId)
  }
}

function formatVideoName(video) {
  if (!video || !video.start_time) return 'Unbekannt'

  const date = new Date(video.start_time)
  return date.toLocaleString('de-DE')
}

function formatFileSize(bytes) {
  if (!bytes) return '0 B'

  const units = ['B', 'KB', 'MB', 'GB']
  let size = bytes
  let unitIndex = 0

  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }

  return `${size.toFixed(2)} ${units[unitIndex]}`
}

function formatDate(timestamp) {
  const date = new Date(timestamp * 1000)
  return date.toLocaleString('de-DE')
}

onMounted(async () => {
  await adminStore.fetchStatus()
  await recordingStore.fetchStatus()
  await videosStore.fetchVideos()
})
</script>

<style scoped>
/* Admin page mobile optimizations */
.admin-title {
  font-size: 2rem;
  font-weight: 700;
}

@media (max-width: 599px) {
  .admin-title {
    font-size: 1.5rem;
  }
}

/* Ensure buttons are touch-friendly on mobile */
@media (max-width: 599px) {
  .v-btn {
    min-height: 44px;
  }
}
</style>
