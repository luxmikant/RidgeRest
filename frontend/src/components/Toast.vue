<template>
  <Transition name="toast">
    <div v-if="toastStore.visible"
      class="fixed top-4 right-4 z-50 flex items-center gap-3 px-5 py-3 rounded-lg shadow-lg text-sm font-medium"
      :class="classes">
      <span>{{ toastStore.message }}</span>
      <button @click="toastStore.hide()" class="ml-2 opacity-70 hover:opacity-100">&times;</button>
    </div>
  </Transition>
</template>

<script setup>
import { computed } from 'vue'
import { useToastStore } from '../stores/toast'

const toastStore = useToastStore()

const classes = computed(() => ({
  'bg-green-500 text-white': toastStore.type === 'success',
  'bg-red-500 text-white': toastStore.type === 'error',
  'bg-blue-500 text-white': toastStore.type === 'info',
}))
</script>

<style scoped>
.toast-enter-active, .toast-leave-active {
  transition: all 0.3s ease;
}
.toast-enter-from, .toast-leave-to {
  opacity: 0;
  transform: translateX(100px);
}
</style>
