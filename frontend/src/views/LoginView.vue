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
            <!-- Password hint alert -->
            <v-alert
              v-if="showPasswordHint"
              type="warning"
              variant="tonal"
              prominent
              closable
              @click:close="showPasswordHint = false"
              class="mb-4"
            >
              <v-alert-title class="text-h6 mb-2">
                Passwort vergessen?
              </v-alert-title>
              <div class="text-body-1">
                Das Passwort findest du groß in der Mitte des Anleitungszettels, direkt neben dem QR-Code. Der Zettel liegt in der Garderobe.
              </div>
            </v-alert>

            <v-form @submit.prevent="handleLogin">
              <!-- Hidden username field to help browsers recognize this as a login form -->
              <v-text-field
                v-model="username"
                label="Benutzername"
                type="text"
                variant="outlined"
                prepend-inner-icon="mdi-account"
                :disabled="loading"
                autocomplete="username"
                class="mb-4"
                style="display: none;"
                value="user"
              ></v-text-field>

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
                name="password"
              ></v-text-field>

              <v-checkbox
                v-model="rememberMe"
                label="Angemeldet bleiben"
                :disabled="loading"
                color="primary"
                hide-details
                class="mb-4"
              ></v-checkbox>

              <v-btn
                type="submit"
                color="primary"
                size="large"
                block
                :loading="loading"
                :disabled="!password || loading || authStore.loginCooldown > 0"
                class="login-btn"
              >
                <v-icon start>mdi-login</v-icon>
                <span v-if="authStore.loginCooldown > 0">
                  Warte {{ authStore.loginCooldown }}s
                </span>
                <span v-else>Anmelden</span>
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

const username = ref('user')
const password = ref('')
const rememberMe = ref(false)
const loading = ref(false)
const errorMessage = ref('')
const showPasswordHint = ref(false)

// Initialize rememberMe checkbox from localStorage
const savedRememberMe = localStorage.getItem('rememberMe')
if (savedRememberMe === 'true') {
  rememberMe.value = true
}

const handleLogin = async () => {
  if (!password.value) return

  loading.value = true
  errorMessage.value = ''

  const success = await authStore.login(password.value, rememberMe.value)

  if (success) {
    // Redirect to home or intended route
    const redirectTo = router.currentRoute.value.query.redirect || '/'
    router.push(redirectTo)
  } else {
    errorMessage.value = authStore.authError || 'Login fehlgeschlagen'
    showPasswordHint.value = true
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

  /* Make alert more spacious on mobile */
  :deep(.v-alert) {
    padding: 1rem !important;
  }

  :deep(.v-alert-title) {
    font-size: 1.1rem !important;
    line-height: 1.4 !important;
    margin-bottom: 0.75rem !important;
  }

  :deep(.v-alert .text-body-1) {
    font-size: 0.95rem !important;
    line-height: 1.5 !important;
  }

  /* Give the warning icon more space */
  :deep(.v-alert__prepend) {
    margin-right: 0.75rem !important;
  }
}
</style>
