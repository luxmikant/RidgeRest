import { defineStore } from 'pinia'
import { ref } from 'vue'
import { io } from 'socket.io-client'
import { useToastStore } from './toast'

export const useSocketStore = defineStore('socket', () => {
  const socket = ref(null)
  const connected = ref(false)

  function connect(userId) {
    if (socket.value) return

    const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
    socket.value = io(baseUrl, {
      path: '/ws/socket.io',
      withCredentials: true,
    })

    socket.value.on('connect', () => {
      connected.value = true
      // Join personal room
      socket.value.emit('join', { user_id: userId })
    })

    socket.value.on('leave_status_changed', (data) => {
      const toast = useToastStore()
      if (data.status === 'approved') {
        toast.show('Your leave request has been approved!', 'success')
      } else if (data.status === 'rejected') {
        toast.show(`Your leave request was rejected: ${data.rejection_reason || ''}`, 'error')
      }
    })

    socket.value.on('disconnect', () => {
      connected.value = false
    })
  }

  function disconnect() {
    if (socket.value) {
      socket.value.disconnect()
      socket.value = null
      connected.value = false
    }
  }

  return { socket, connected, connect, disconnect }
})
