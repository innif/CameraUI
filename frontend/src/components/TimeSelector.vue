<template>
  <div class="time-selector">
    <!-- Time Display -->
    <v-chip v-if="!hideTimeChip" color="primary" :size="isMobile ? 'default' : 'large'" :class="isMobile ? 'mb-2' : 'mb-4'">
      <v-icon start>mdi-clock</v-icon>
      {{ formatTimeAsClock(modelValue) }}
    </v-chip>

    <!-- Slider -->
    <v-slider
      :model-value="modelValue"
      :min="minTime"
      :max="maxDuration"
      :step="1"
      thumb-label="always"
      color="primary"
      :class="isMobile ? 'mb-2' : 'mb-4'"
      @update:model-value="updateValue"
    >
      <template #thumb-label="{ modelValue }">
        {{ formatTimeShort(modelValue) }}
      </template>
    </v-slider>

    <!-- Quick Navigation Buttons -->
    <v-row :class="isMobile ? 'mb-2 time-nav-buttons-mobile' : 'mb-4'" dense>
      <!-- Button -1 Min -->
      <v-col cols="6" sm="3" order="1">
        <v-btn
          block
          variant="outlined"
          :disabled="modelValue - 60 < minTime"
          @click="adjustTime(-60)"
          class="time-nav-btn"
          :size="isMobile ? 'small' : 'default'"
        >
          <v-icon :size="isMobile ? 'small' : 'default'">mdi-rewind</v-icon>
          <span class="ml-1" :class="isMobile ? 'mobile-btn-text' : ''">{{ isMobile ? '-1m' : '-1 Min' }}</span>
        </v-btn>
      </v-col>

      <!-- Button -10s -->
      <v-col cols="6" sm="3" order="2">
        <v-btn
          block
          variant="outlined"
          :disabled="modelValue - 10 < minTime"
          @click="adjustTime(-10)"
          class="time-nav-btn"
          :size="isMobile ? 'small' : 'default'"
        >
          <v-icon :size="isMobile ? 'small' : 'default'">mdi-rewind-10</v-icon>
          <span class="ml-1 mobile-btn-text">-10s</span>
        </v-btn>
      </v-col>

      <!-- Button +10s -->
      <v-col cols="6" sm="3" order="3" order-xs="4">
        <v-btn
          block
          variant="outlined"
          :disabled="modelValue + 10 > maxDuration"
          @click="adjustTime(10)"
          class="time-nav-btn"
          :size="isMobile ? 'small' : 'default'"
        >
          <v-icon :size="isMobile ? 'small' : 'default'">mdi-fast-forward-10</v-icon>
          <span class="ml-1 mobile-btn-text">+10s</span>
        </v-btn>
      </v-col>

      <!-- Button +1 Min -->
      <v-col cols="6" sm="3" order="4" order-xs="3">
        <v-btn
          block
          variant="outlined"
          :disabled="modelValue + 60 > maxDuration"
          @click="adjustTime(60)"
          class="time-nav-btn"
          :size="isMobile ? 'small' : 'default'"
        >
          <v-icon :size="isMobile ? 'small' : 'default'">mdi-fast-forward</v-icon>
          <span class="ml-1" :class="isMobile ? 'mobile-btn-text' : ''">{{ isMobile ? '+1m' : '+1 Min' }}</span>
        </v-btn>
      </v-col>
    </v-row>

    <!-- Preview Image -->
    <div v-if="videosStore.previewFrame" class="preview-container">
      <img
        :src="`${videosStore.previewFrame}`"
        alt="Vorschau"
        class="preview-image"
      />
    </div>
    <div v-else class="preview-placeholder">
      <v-icon size="64" color="grey">mdi-image-off</v-icon>
      <p class="text-grey">Keine Vorschau verfügbar</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useDisplay } from 'vuetify'
import { useVideosStore } from '@/stores/videos'

const props = defineProps({
  modelValue: {
    type: Number,
    required: true
  },
  video: {
    type: Object,
    required: true
  },
  minTime: {
    type: Number,
    default: 0
  },
  hideTimeChip: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'preview'])

const videosStore = useVideosStore()
const { mobile } = useDisplay()

const isMobile = computed(() => mobile.value)

// Debounce timer for slider preview updates
let previewDebounceTimer = null

// Debounced preview update function
function debouncedPreviewUpdate(value) {
  if (previewDebounceTimer) {
    clearTimeout(previewDebounceTimer)
  }
  previewDebounceTimer = setTimeout(() => {
    emit('preview', value)
  }, 500) // Wait 500ms after user stops moving slider
}

const maxDuration = computed(() => {
  // Use video duration if available, otherwise fallback to a large value
  // to allow slider interaction while duration is being loaded
  const duration = props.video?.duration
  if (duration && duration > 0) {
    return duration
  }
  // Fallback: allow up to 24 hours if duration is not yet available
  return 86400
})

function updateValue(value) {
  emit('update:modelValue', value)
  // Auto-update preview when slider changes (with debounce)
  debouncedPreviewUpdate(value)
}

function adjustTime(seconds) {
  const newValue = Math.max(
    props.minTime,
    Math.min(maxDuration.value, props.modelValue + seconds)
  )
  emit('update:modelValue', newValue)
  // Auto-update preview immediately when buttons are clicked
  emit('preview', newValue)
}

function formatTimeAsClock(seconds) {
  // Get the video start time and add the offset
  const videoStartTime = new Date(props.video.start_time)
  const actualTime = new Date(videoStartTime.getTime() + seconds * 1000)

  // Format as HH:MM:SS
  const hrs = actualTime.getHours().toString().padStart(2, '0')
  const mins = actualTime.getMinutes().toString().padStart(2, '0')
  const secs = actualTime.getSeconds().toString().padStart(2, '0')

  return `${hrs}:${mins}:${secs} Uhr`
}

function formatTimeShort(seconds) {
  // Get the video start time and add the offset
  const videoStartTime = new Date(props.video.start_time)
  const actualTime = new Date(videoStartTime.getTime() + seconds * 1000)

  // Format as HH:MM (shorter for slider thumb)
  const hrs = actualTime.getHours().toString().padStart(2, '0')
  const mins = actualTime.getMinutes().toString().padStart(2, '0')

  return `${hrs}:${mins}`
}
</script>

<style scoped>
.time-selector {
  width: 100%;
}

/* Mobile-optimized navigation buttons */
.time-nav-btn {
  min-height: 44px; /* Touch-friendly minimum height */
  font-size: 0.875rem;
}

@media (max-width: 599px) {
  .mobile-btn-text {
    font-size: 0.75rem;
  }

  .time-nav-btn {
    min-height: 40px;
    padding: 0.25rem 0.5rem;
  }

  .time-nav-buttons-mobile {
    margin-left: -4px;
    margin-right: -4px;
  }
}

.preview-container {
  width: 100%;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  background-color: #000;
}

.preview-image {
  width: 100%;
  height: auto;
  display: block;
  object-fit: contain;
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

/* Mobile-responsive preview placeholder */
@media (max-width: 599px) {
  .preview-placeholder {
    min-height: 180px;
  }

  .preview-placeholder .v-icon {
    font-size: 48px !important;
  }

  .preview-placeholder p {
    font-size: 0.875rem;
  }
}
</style>
