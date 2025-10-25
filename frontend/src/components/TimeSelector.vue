<template>
  <div class="time-selector">
    <!-- Time Display -->
    <v-chip color="primary" size="large" class="mb-4">
      <v-icon start>mdi-clock</v-icon>
      {{ formatTime(modelValue) }}
    </v-chip>

    <!-- Slider -->
    <v-slider
      :model-value="modelValue"
      :min="minTime"
      :max="maxDuration"
      :step="1"
      thumb-label="always"
      color="primary"
      class="mb-4"
      @update:model-value="updateValue"
    >
      <template #thumb-label="{ modelValue }">
        {{ formatTime(modelValue) }}
      </template>
    </v-slider>

    <!-- Quick Navigation Buttons -->
    <v-row class="mb-4">
      <v-col cols="6" sm="3">
        <v-btn
          block
          variant="outlined"
          :disabled="modelValue - 60 < minTime"
          @click="adjustTime(-60)"
        >
          <v-icon start>mdi-rewind</v-icon>
          -1 Min
        </v-btn>
      </v-col>
      <v-col cols="6" sm="3">
        <v-btn
          block
          variant="outlined"
          :disabled="modelValue - 10 < minTime"
          @click="adjustTime(-10)"
        >
          <v-icon start>mdi-rewind-10</v-icon>
          -10s
        </v-btn>
      </v-col>
      <v-col cols="6" sm="3">
        <v-btn
          block
          variant="outlined"
          :disabled="modelValue + 10 > maxDuration"
          @click="adjustTime(10)"
        >
          <v-icon start>mdi-fast-forward-10</v-icon>
          +10s
        </v-btn>
      </v-col>
      <v-col cols="6" sm="3">
        <v-btn
          block
          variant="outlined"
          :disabled="modelValue + 60 > maxDuration"
          @click="adjustTime(60)"
        >
          <v-icon start>mdi-fast-forward</v-icon>
          +1 Min
        </v-btn>
      </v-col>
    </v-row>

    <!-- Preview Button -->
    <v-btn
      color="info"
      block
      class="mb-4"
      @click="emit('preview', modelValue)"
    >
      <v-icon start>mdi-image-search</v-icon>
      Vorschau aktualisieren
    </v-btn>

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
  }
})

const emit = defineEmits(['update:modelValue', 'preview'])

const videosStore = useVideosStore()

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
}

function adjustTime(seconds) {
  const newValue = Math.max(
    props.minTime,
    Math.min(maxDuration.value, props.modelValue + seconds)
  )
  emit('update:modelValue', newValue)
}

function formatTime(seconds) {
  const hrs = Math.floor(seconds / 3600)
  const mins = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)

  if (hrs > 0) {
    return `${hrs}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
  return `${mins}:${secs.toString().padStart(2, '0')}`
}
</script>

<style scoped>
.time-selector {
  width: 100%;
}

.preview-container {
  width: 100%;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
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
