import { createVuetify } from 'vuetify'
import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { de } from 'vuetify/locale'

export default createVuetify({
  components,
  directives,
  locale: {
    locale: 'de',
    messages: { de }
  },
  theme: {
    defaultTheme: 'dark',
    themes: {
      light: {
        dark: false,
        colors: {
          background: '#F5F7FA',
          surface: '#FFFFFF',
          primary: '#6366F1',
          'primary-darken-1': '#4F46E5',
          secondary: '#8B5CF6',
          'secondary-darken-1': '#7C3AED',
          accent: '#EC4899',
          error: '#EF4444',
          info: '#3B82F6',
          success: '#10B981',
          warning: '#F59E0B',
          'on-background': '#1F2937',
          'on-surface': '#1F2937'
        }
      },
      dark: {
        dark: true,
        colors: {
          background: '#0F172A',
          surface: '#1E293B',
          'surface-bright': '#334155',
          'surface-variant': '#475569',
          primary: '#818CF8',
          'primary-darken-1': '#6366F1',
          secondary: '#A78BFA',
          'secondary-darken-1': '#8B5CF6',
          accent: '#F472B6',
          error: '#F87171',
          info: '#60A5FA',
          success: '#34D399',
          warning: '#FBBF24',
          'on-background': '#F1F5F9',
          'on-surface': '#F1F5F9'
        }
      }
    }
  }
})
