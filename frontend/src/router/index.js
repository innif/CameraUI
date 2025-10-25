import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'recording',
      component: () => import('@/views/RecordingView.vue'),
      meta: { title: 'Aufnahme' }
    },
    {
      path: '/download',
      name: 'download',
      component: () => import('@/views/DownloadView.vue'),
      meta: { title: 'Videoarchiv' }
    },
    {
      path: '/admin',
      name: 'admin',
      component: () => import('@/views/AdminView.vue'),
      meta: { title: 'Administration' }
    },
    {
      path: '/check',
      name: 'check',
      component: () => import('@/views/CheckView.vue'),
      meta: { title: 'System Check' }
    }
  ]
})

// Update page title on route change
router.beforeEach((to, from, next) => {
  document.title = to.meta.title
    ? `${to.meta.title} - ScheiniCam`
    : 'ScheiniCam'
  next()
})

export default router
