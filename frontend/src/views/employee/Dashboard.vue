<template>
  <div class="max-w-5xl mx-auto space-y-6">
    <h1 class="text-2xl font-bold text-gray-800 dark:text-white">Employee Dashboard</h1>

    <!-- Balance -->
    <section>
      <h2 class="text-lg font-semibold text-gray-700 dark:text-gray-300 mb-3">Leave Balance</h2>
      <BalanceBadge :balance="balance" />
    </section>

    <!-- Quick actions -->
    <div class="flex gap-4">
      <router-link to="/employee/apply"
        class="px-5 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition text-sm font-medium">
        + Apply for Leave
      </router-link>
      <router-link to="/employee/history"
        class="px-5 py-2.5 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition text-sm font-medium">
        View History
      </router-link>
    </div>

    <!-- Recent leaves -->
    <section>
      <h2 class="text-lg font-semibold text-gray-700 dark:text-gray-300 mb-3">Recent Leaves</h2>
      <div v-if="!recentLeaves.length" class="text-gray-400 text-sm">No leave applications yet.</div>
      <div class="space-y-2">
        <div v-for="leave in recentLeaves" :key="leave._id"
          class="bg-white dark:bg-gray-800 rounded-lg shadow p-4 flex justify-between items-center">
          <div>
            <span class="font-medium capitalize text-gray-800 dark:text-gray-200">{{ leave.leave_type }}</span>
            <span class="text-xs text-gray-500 ml-2">{{ leave.start_date }} → {{ leave.end_date }}</span>
          </div>
          <span class="text-xs px-2 py-1 rounded-full font-medium" :class="statusClass(leave.status)">
            {{ leave.status }}
          </span>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useLeaveStore } from '../../stores/leaves'
import { useSocketStore } from '../../stores/socket'
import BalanceBadge from '../../components/BalanceBadge.vue'

const leaveStore = useLeaveStore()
const socketStore = useSocketStore()

const balance = ref({})
const recentLeaves = ref([])

onMounted(async () => {
  socketStore.connect()
  const [bal, leaves] = await Promise.all([
    leaveStore.fetchBalance(),
    leaveStore.fetchMyLeaves(),
  ])
  balance.value = bal
  recentLeaves.value = (leaves || []).slice(0, 5)
})

function statusClass(status) {
  return {
    'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300': status === 'pending',
    'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300': status === 'approved',
    'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300': status === 'rejected',
    'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300': status === 'cancelled',
  }
}
</script>
