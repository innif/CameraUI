<template>
  <v-app>
    <v-app-bar
      color="surface"
      elevation="0"
      class="app-bar-glass"
    >
      <v-app-bar-title class="d-flex align-center">
        <v-icon icon="mdi-video" size="28" class="mr-3" color="primary"></v-icon>
        <span class="app-title">ScheiniCam</span>
      </v-app-bar-title>

      <v-spacer></v-spacer>

      <v-btn
        icon
        to="/"
        title="Aufnahme"
        variant="text"
        class="nav-btn"
      >
        <v-icon>mdi-record-circle</v-icon>
      </v-btn>

      <v-btn
        icon
        to="/admin"
        title="Admin"
        variant="text"
        class="nav-btn"
      >
        <v-icon>mdi-cog</v-icon>
      </v-btn>

      <v-btn
        icon
        to="/check"
        title="System Check"
        variant="text"
        class="nav-btn"
      >
        <v-icon>mdi-check-circle</v-icon>
      </v-btn>

      <v-btn
        icon
        @click="toggleTheme"
        title="Dark Mode umschalten"
        variant="text"
        class="nav-btn ml-2"
      >
        <v-icon>{{ theme.global.current.value.dark ? 'mdi-weather-sunny' : 'mdi-weather-night' }}</v-icon>
      </v-btn>
    </v-app-bar>

    <v-main class="main-content">
      <v-container fluid class="pa-0">
        <router-view v-slot="{ Component }">
          <transition name="page" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </v-container>
    </v-main>

    <v-footer class="footer-glass">
      <v-container>
        <div class="text-center footer-text">
          <v-icon icon="mdi-video" size="16" class="mr-1"></v-icon>
          ScheiniCam - Automatisches Aufnahmesystem &copy; {{ new Date().getFullYear() }}
        </div>
      </v-container>
    </v-footer>
  </v-app>
</template>

<script setup>
import { useTheme } from 'vuetify'

const theme = useTheme()

function toggleTheme() {
  theme.global.name.value = theme.global.current.value.dark ? 'light' : 'dark'
}
</script>

<style scoped>
.app-bar-glass {
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.app-title {
  font-size: 1.5rem;
  font-weight: 600;
  letter-spacing: -0.5px;
  background: linear-gradient(135deg, rgb(var(--v-theme-primary)) 0%, rgb(var(--v-theme-secondary)) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav-btn {
  transition: all 0.2s ease;
}

.nav-btn:hover {
  transform: translateY(-2px);
}

.main-content {
  background: linear-gradient(180deg, rgba(var(--v-theme-primary), 0.03) 0%, transparent 100%);
  min-height: calc(100vh - 64px - 56px);
}

.footer-glass {
  backdrop-filter: blur(10px);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(var(--v-theme-surface), 0.8) !important;
}

.footer-text {
  opacity: 0.7;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Page transition animations */
.page-enter-active,
.page-leave-active {
  transition: all 0.3s ease;
}

.page-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
