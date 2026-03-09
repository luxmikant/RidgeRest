import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { clerkPlugin } from '@clerk/vue'
import App from './App.vue'
import router from './router'
import './style.css'

const PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY
if (!PUBLISHABLE_KEY) {
  throw new Error('Missing VITE_CLERK_PUBLISHABLE_KEY environment variable')
}

// Datadog RUM (only in production)
if (import.meta.env.VITE_DD_APPLICATION_ID) {
  import('@datadog/browser-rum').then(({ datadogRum }) => {
    datadogRum.init({
      applicationId: import.meta.env.VITE_DD_APPLICATION_ID,
      clientToken: import.meta.env.VITE_DD_CLIENT_TOKEN,
      site: import.meta.env.VITE_DD_SITE || 'datadoghq.com',
      service: 'ridgerest-frontend',
      env: import.meta.env.MODE,
      sessionSampleRate: 100,
      sessionReplaySampleRate: import.meta.env.MODE === 'production' ? 20 : 100,
      trackUserInteractions: true,
      trackResources: true,
      trackLongTasks: true,
      defaultPrivacyLevel: 'mask-user-input',
    })
  })
}

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(clerkPlugin, { publishableKey: PUBLISHABLE_KEY })
app.mount('#app')

