<template>
  <div class="preview-image-container">
    <div v-if="recordingStore.previewImage" class="preview-wrapper">
      <img
        :src="recordingStore.previewImage"
        alt="Kamera-Vorschau"
        class="preview-image"
      />
      <div class="preview-overlay">
        <v-chip color="success" size="small">
          <v-icon start size="small">mdi-circle</v-icon>
          Live
        </v-chip>
      </div>
    </div>
    <div v-else class="preview-placeholder">
      <v-progress-circular indeterminate color="primary"></v-progress-circular>
      <p class="mt-4 text-grey">Lade Vorschau...</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import { useRecordingStore } from '@/stores/recording'

const recordingStore = useRecordingStore()
let previewInterval = null

async function updatePreview() {
  try {
    await recordingStore.fetchPreview()
  } catch (err) {
    console.error('Failed to update preview:', err)
  }
}

onMounted(async () => {
  await updatePreview()
  previewInterval = setInterval(updatePreview, 1000)
})

onUnmounted(() => {
  if (previewInterval) {
    clearInterval(previewInterval)
  }
})
</script>

<style scoped>
.preview-image-container {
  width: 100%;
}

.preview-wrapper {
  position: relative;
  width: 100%;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.preview-image {
  width: 100%;
  height: auto;
  display: block;
}

.preview-overlay {
  position: absolute;
  top: 12px;
  right: 12px;
}

.preview-placeholder {
  width: 100%;
  min-height: 300px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background-color: #f5f5f5;
  border-radius: 8px;
}
</style>
