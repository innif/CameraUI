<template>
  <v-container class="container-max">
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-4">Videoarchiv</h1>

        <DownloadWizard />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import DownloadWizard from '@/components/DownloadWizard.vue'
</script>
