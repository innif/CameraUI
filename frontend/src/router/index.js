import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { title: 'Login', requiresAuth: false }
    },
    {
      path: '/',
      name: 'recording',
      component: () => import('@/views/RecordingView.vue'),
      meta: { title: 'Aufnahme', requiresAuth: true }
    },
    {
      path: '/download',
      name: 'download',
      component: () => import('@/views/DownloadView.vue'),
      meta: { title: 'Videoarchiv', requiresAuth: true }
    },
    {
      path: '/admin',
      name: 'admin',
      component: () => import('@/views/AdminView.vue'),
      meta: { title: 'Administration', requiresAuth: true }
    },
    {
      path: '/check',
      name: 'check',
      component: () => import('@/views/CheckView.vue'),
      meta: { title: 'System Check', requiresAuth: true }
    }
  ]
})

// Authentication guard and page title update
router.beforeEach((to, from, next) => {
  // Update page title
  document.title = to.meta.title
    ? `${to.meta.title} - ScheiniCam`
    : 'ScheiniCam'

  // Check authentication
  const authStore = useAuthStore()
  const requiresAuth = to.meta.requiresAuth !== false // Default to true

  if (requiresAuth && !authStore.isAuthenticated) {
    // Redirect to login if not authenticated
    next({
      name: 'login',
      query: { redirect: to.fullPath }
    })
  } else if (to.name === 'login' && authStore.isAuthenticated) {
    // Redirect to home if already authenticated and trying to access login
    next({ name: 'recording' })
  } else {
    next()
  }
})

export default router
