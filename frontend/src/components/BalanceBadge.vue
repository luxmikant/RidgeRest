<template>
  <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
    <div v-for="item in balanceItems" :key="item.type"
      class="bg-white dark:bg-gray-800 rounded-xl shadow p-4">
      <div class="flex justify-between text-sm mb-2">
        <span class="font-medium text-gray-700 dark:text-gray-300 capitalize">{{ item.type }}</span>
        <span class="text-gray-500 dark:text-gray-400">
          {{ item.remaining }}/{{ item.total }}
        </span>
      </div>
      <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
        <div class="h-2.5 rounded-full transition-all duration-500"
          :class="barColor(item.remaining, item.total)"
          :style="{ width: pct(item.remaining, item.total) + '%' }"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  balance: { type: Object, default: () => ({}) }
})

const balanceItems = computed(() => {
  if (!props.balance?.balances) return []
  return props.balance.balances.map(b => ({
    type: b.leave_type,
    total: b.total,
    remaining: b.remaining,
  }))
})

function pct(remaining, total) {
  if (!total) return 0
  return Math.round((remaining / total) * 100)
}

function barColor(remaining, total) {
  const p = pct(remaining, total)
  if (p > 50) return 'bg-green-500'
  if (p > 20) return 'bg-yellow-500'
  return 'bg-red-500'
}
</script>
