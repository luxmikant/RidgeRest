import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useToastStore = defineStore('toast', () => {
  const message = ref('')
  const type = ref('info') // 'success' | 'error' | 'info'
  const visible = ref(false)
  let timeout = null

  function show(msg, t = 'info', duration = 4000) {
    message.value = msg
    type.value = t
    visible.value = true

    if (timeout) clearTimeout(timeout)
    timeout = setTimeout(() => {
      visible.value = false
    }, duration)
  }

  function hide() {
    visible.value = false
  }

  return { message, type, visible, show, hide }
})
