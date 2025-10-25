<template>
  <v-container class="container-max">
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-4">System Check</h1>

        <!-- Audio Monitor Status -->
        <v-card class="mb-4" v-if="adminStore.obsStatus?.audio_monitor">
          <v-card-title>
            <v-icon start>mdi-robot</v-icon>
            Automatische Audio-Überwachung
          </v-card-title>
          <v-card-text>
            <v-alert
              :type="getAudioMonitorAlertType()"
              :icon="getAudioMonitorIcon()"
              class="mb-4"
            >
              <div>
                <strong>Status: {{ adminStore.obsStatus.audio_monitor.running ? 'Aktiv' : 'Inaktiv' }}</strong>
                <div class="mt-2">
                  <small>
                    Die automatische Audio-Überwachung prüft alle {{ adminStore.obsStatus.audio_monitor.check_interval }} Sekunden
                    den Audio-Pegel und lädt die Kamera bei {{ adminStore.obsStatus.audio_monitor.failure_threshold }}
                    aufeinanderfolgenden Fehlern automatisch neu.
                  </small>
                </div>
              </div>
            </v-alert>

            <v-row dense>
              <v-col cols="6">
                <v-card variant="outlined">
                  <v-card-text>
                    <div class="text-caption text-grey">Gesamte Checks</div>
                    <div class="text-h6">{{ adminStore.obsStatus.audio_monitor.total_checks }}</div>
                  </v-card-text>
                </v-card>
              </v-col>
              <v-col cols="6">
                <v-card variant="outlined">
                  <v-card-text>
                    <div class="text-caption text-grey">Fehler</div>
                    <div class="text-h6">{{ adminStore.obsStatus.audio_monitor.total_failures }}</div>
                  </v-card-text>
                </v-card>
              </v-col>
              <v-col cols="6">
                <v-card variant="outlined">
                  <v-card-text>
                    <div class="text-caption text-grey">Aufeinanderfolgende Fehler</div>
                    <div class="text-h6" :class="adminStore.obsStatus.audio_monitor.consecutive_failures > 0 ? 'text-error' : ''">
                      {{ adminStore.obsStatus.audio_monitor.consecutive_failures }}
                    </div>
                  </v-card-text>
                </v-card>
              </v-col>
              <v-col cols="6">
                <v-card variant="outlined">
                  <v-card-text>
                    <div class="text-caption text-grey">Kamera-Neustarts</div>
                    <div class="text-h6">{{ adminStore.obsStatus.audio_monitor.camera_reloads }}</div>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>

            <div v-if="adminStore.obsStatus.audio_monitor.last_check_time" class="mt-3">
              <v-divider class="my-2"></v-divider>
              <div class="text-caption">
                Letzter Check: {{ formatDate(adminStore.obsStatus.audio_monitor.last_check_time) }}
              </div>
              <div v-if="adminStore.obsStatus.audio_monitor.last_failure_time" class="text-caption text-error">
                Letzter Fehler: {{ formatDate(adminStore.obsStatus.audio_monitor.last_failure_time) }}
              </div>
            </div>
          </v-card-text>
        </v-card>

        <!-- Audio Check -->
        <v-card class="mb-4">
          <v-card-title>
            <v-icon start>mdi-volume-high</v-icon>
            Manueller Audio-Test
          </v-card-title>
          <v-card-text>
            <p class="mb-4">
              Dieser Test überprüft den Audio-Pegel der Kamera für 2 Sekunden.
            </p>

            <v-btn
              color="primary"
              block
              size="large"
              :loading="adminStore.loading"
              @click="checkAudio"
            >
              <v-icon start>mdi-play</v-icon>
              Audio-Test starten
            </v-btn>

            <div v-if="adminStore.audioCheckResult" class="mt-4">
              <v-alert
                :type="adminStore.audioCheckResult.has_audio ? 'success' : 'error'"
                prominent
              >
                <div class="d-flex align-center">
                  <v-icon start size="large">
                    {{ adminStore.audioCheckResult.has_audio ? 'mdi-check-circle' : 'mdi-alert-circle' }}
                  </v-icon>
                  <div>
                    <strong>
                      {{ adminStore.audioCheckResult.has_audio ? 'Audio funktioniert!' : 'Kein Audio erkannt' }}
                    </strong>
                    <p class="mb-0 mt-2">
                      Audio-Bereich: {{ adminStore.audioCheckResult.range?.toFixed(4) || 'N/A' }}
                    </p>
                  </div>
                </div>
              </v-alert>
            </div>
          </v-card-text>
        </v-card>

        <!-- Camera Preview -->
        <v-card class="mb-4">
          <v-card-title>
            <v-icon start>mdi-camera</v-icon>
            Kamera-Vorschau
          </v-card-title>
          <v-card-text>
            <PreviewImage />

            <v-btn
              color="primary"
              block
              class="mt-4"
              :loading="adminStore.loading"
              @click="reloadCamera"
            >
              <v-icon start>mdi-reload</v-icon>
              Kamera neu laden
            </v-btn>
          </v-card-text>
        </v-card>

        <!-- Page Actions -->
        <v-card>
          <v-card-title>
            <v-icon start>mdi-cog</v-icon>
            Aktionen
          </v-card-title>
          <v-card-text>
            <v-btn
              color="info"
              block
              @click="reloadPage"
            >
              <v-icon start>mdi-refresh</v-icon>
              Seite neu laden
            </v-btn>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { useAdminStore } from '@/stores/admin'
import PreviewImage from '@/components/PreviewImage.vue'

const adminStore = useAdminStore()
const statusInterval = ref(null)

async function checkAudio() {
  await adminStore.checkAudio()
}

async function reloadCamera() {
  await adminStore.reloadCamera()
}

function reloadPage() {
  window.location.reload()
}

function getAudioMonitorAlertType() {
  const monitor = adminStore.obsStatus?.audio_monitor
  if (!monitor || !monitor.running) return 'info'
  if (monitor.consecutive_failures >= monitor.failure_threshold) return 'error'
  if (monitor.consecutive_failures > 0) return 'warning'
  return 'success'
}

function getAudioMonitorIcon() {
  const monitor = adminStore.obsStatus?.audio_monitor
  if (!monitor || !monitor.running) return 'mdi-pause-circle'
  if (monitor.consecutive_failures >= monitor.failure_threshold) return 'mdi-alert-circle'
  if (monitor.consecutive_failures > 0) return 'mdi-alert'
  return 'mdi-check-circle'
}

function formatDate(isoString) {
  if (!isoString) return 'N/A'
  const date = new Date(isoString)
  return date.toLocaleString('de-DE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

onMounted(async () => {
  await adminStore.fetchStatus()

  // Refresh status every 10 seconds to see audio monitor updates
  statusInterval.value = setInterval(async () => {
    await adminStore.fetchStatus()
  }, 10000)
})

onUnmounted(() => {
  if (statusInterval.value) {
    clearInterval(statusInterval.value)
  }
})
</script>
