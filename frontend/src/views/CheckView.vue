<template>
  <v-container class="container-max">
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-4">System Check</h1>

        <!-- Audio Check -->
        <v-card class="mb-4">
          <v-card-title>
            <v-icon start>mdi-volume-high</v-icon>
            Audio-Test
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
import { onMounted } from 'vue'
import { useAdminStore } from '@/stores/admin'
import PreviewImage from '@/components/PreviewImage.vue'

const adminStore = useAdminStore()

async function checkAudio() {
  await adminStore.checkAudio()
}

async function reloadCamera() {
  await adminStore.reloadCamera()
}

function reloadPage() {
  window.location.reload()
}

onMounted(async () => {
  await adminStore.fetchStatus()
})
</script>
