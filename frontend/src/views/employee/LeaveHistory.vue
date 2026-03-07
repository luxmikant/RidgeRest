<template>
  <div class="max-w-5xl mx-auto">
    <h1 class="text-2xl font-bold text-gray-800 dark:text-white mb-6">Leave History</h1>

    <!-- Filters -->
    <div class="flex gap-3 mb-4">
      <button v-for="s in statuses" :key="s"
        @click="filter = s"
        class="px-3 py-1 rounded-full text-sm font-medium border transition"
        :class="filter === s ? 'bg-blue-600 text-white border-blue-600' : 'border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-400'">
        {{ s || 'All' }}
      </button>
    </div>

    <!-- Table -->
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 dark:bg-gray-700 text-gray-500 dark:text-gray-400 text-left">
          <tr>
            <th class="px-4 py-3">Type</th>
            <th class="px-4 py-3">From</th>
            <th class="px-4 py-3">To</th>
            <th class="px-4 py-3">Reason</th>
            <th class="px-4 py-3">Status</th>
            <th class="px-4 py-3">Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="leave in filteredLeaves" :key="leave._id"
            class="border-t border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-750">
            <td class="px-4 py-3 capitalize">{{ leave.leave_type }}</td>
            <td class="px-4 py-3">{{ leave.start_date }}</td>
            <td class="px-4 py-3">{{ leave.end_date }}</td>
            <td class="px-4 py-3 max-w-xs truncate">{{ leave.reason }}</td>
            <td class="px-4 py-3">
              <span class="text-xs px-2 py-1 rounded-full font-medium" :class="statusCls(leave.status)">
                {{ leave.status }}
              </span>
              <span v-if="leave.rejection_reason" class="block text-xs text-red-400 mt-1">
                {{ leave.rejection_reason }}
              </span>
            </td>
            <td class="px-4 py-3">
              <button v-if="leave.status === 'pending'" @click="cancel(leave._id)"
                class="text-red-500 hover:text-red-700 text-xs font-medium">
                Cancel
              </button>
            </td>
          </tr>
          <tr v-if="!filteredLeaves.length">
            <td colspan="6" class="px-4 py-8 text-center text-gray-400">No leaves found.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useLeaveStore } from '../../stores/leaves'
import { useToastStore } from '../../stores/toast'

const leaveStore = useLeaveStore()
const toastStore = useToastStore()

const leaves = ref([])
const filter = ref('')
const statuses = ['', 'pending', 'approved', 'rejected', 'cancelled']

const filteredLeaves = computed(() =>
  filter.value ? leaves.value.filter(l => l.status === filter.value) : leaves.value
)

onMounted(async () => {
  leaves.value = await leaveStore.fetchMyLeaves() || []
})

async function cancel(id) {
  try {
    await leaveStore.cancelLeave(id)
    leaves.value = await leaveStore.fetchMyLeaves() || []
    toastStore.show('Leave cancelled', 'success')
  } catch {
    toastStore.show('Failed to cancel', 'error')
  }
}

function statusCls(status) {
  return {
    'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300': status === 'pending',
    'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300': status === 'approved',
    'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300': status === 'rejected',
    'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300': status === 'cancelled',
  }
}
</script>
