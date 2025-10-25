<template>
  <v-container class="login-container" fluid>
    <v-row justify="center" align="center" class="fill-height">
      <v-col cols="12" sm="8" md="6" lg="4">
        <v-card class="login-card" elevation="8">
          <v-card-title class="text-center pa-6">
            <div class="login-title-wrapper">
              <v-icon icon="mdi-video" size="48" color="primary" class="mb-3"></v-icon>
              <h1 class="app-title mb-2">ScheiniCam</h1>
              <p class="text-subtitle-1 text-medium-emphasis">Bitte anmelden</p>
            </div>
          </v-card-title>

          <v-card-text class="pa-6">
            <v-form @submit.prevent="handleLogin">
              <v-text-field
                v-model="password"
                label="Passwort"
                type="password"
                variant="outlined"
                prepend-inner-icon="mdi-lock"
                :error-messages="errorMessage"
                :disabled="loading"
                autocomplete="current-password"
                autofocus
                @keyup.enter="handleLogin"
                class="mb-4"
              ></v-text-field>

              <v-btn
                type="submit"
                color="primary"
                size="large"
                block
                :loading="loading"
                :disabled="!password || loading"
                class="login-btn"
              >
                <v-icon start>mdi-login</v-icon>
                Anmelden
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const password = ref('')
const loading = ref(false)
const errorMessage = ref('')

const handleLogin = async () => {
  if (!password.value) return

  loading.value = true
  errorMessage.value = ''

  const success = await authStore.login(password.value)

  if (success) {
    // Redirect to home or intended route
    const redirectTo = router.currentRoute.value.query.redirect || '/'
    router.push(redirectTo)
  } else {
    errorMessage.value = authStore.authError || 'Login fehlgeschlagen'
    password.value = ''
  }

  loading.value = false
}
</script>

<style scoped>
.login-container {
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  padding: 0 !important;
  margin: 0 !important;
  min-height: 100% !important;
  height: 100% !important;
}

.fill-height {
  height: 100%;
  margin: 0;
  width: 100%;
}

.login-card {
  background: rgb(var(--v-theme-surface)) !important;
  width: 100%;
  max-width: 500px;
}

.login-title-wrapper {
  width: 100%;
  text-align: center;
}

.app-title {
  font-size: 2rem;
  font-weight: 600;
  letter-spacing: -0.5px;
  background: linear-gradient(135deg, rgb(var(--v-theme-primary)) 0%, rgb(var(--v-theme-secondary)) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.login-btn {
  margin-top: 1rem;
  transition: all 0.3s ease;
}

@media (hover: hover) {
  .login-btn:not(:disabled):hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(var(--v-theme-primary), 0.3);
  }
}

/* Mobile optimizations */
@media (max-width: 599px) {
  .app-title {
    font-size: 1.5rem;
  }

  .login-container {
    padding: 1rem !important;
  }

  .login-card {
    max-width: 100%;
  }
}
</style>
