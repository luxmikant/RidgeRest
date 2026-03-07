<template>
  <div class="max-w-6xl mx-auto">
    <h1 class="text-2xl font-bold text-gray-800 dark:text-white mb-6">Leave Requests</h1>

    <!-- Filters -->
    <div class="flex gap-3 mb-4 flex-wrap">
      <button v-for="s in statuses" :key="s" @click="filter = s"
        class="px-3 py-1 rounded-full text-sm font-medium border transition"
        :class="filter === s ? 'bg-blue-600 text-white border-blue-600' : 'border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-400'">
        {{ s || 'All' }}
      </button>
    </div>

    <!-- Table -->
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow overflow-x-auto">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 dark:bg-gray-700 text-gray-500 dark:text-gray-400 text-left">
          <tr>
            <th class="px-4 py-3">Employee</th>
            <th class="px-4 py-3">Type</th>
            <th class="px-4 py-3">From</th>
            <th class="px-4 py-3">To</th>
            <th class="px-4 py-3">Reason</th>
            <th class="px-4 py-3">Status</th>
            <th class="px-4 py-3">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="leave in filtered" :key="leave._id"
            class="border-t border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-750">
            <td class="px-4 py-3 font-medium text-gray-800 dark:text-gray-200">{{ leave.employee_name }}</td>
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
              <div v-if="leave.status === 'pending'" class="flex gap-2">
                <button @click="approve(leave._id)" class="text-xs px-3 py-1 rounded bg-green-500 text-white hover:bg-green-600">Approve</button>
                <button @click="openReject(leave._id)" class="text-xs px-3 py-1 rounded bg-red-500 text-white hover:bg-red-600">Reject</button>
              </div>
              <span v-else class="text-xs text-gray-400">—</span>
            </td>
          </tr>
          <tr v-if="!filtered.length">
            <td colspan="7" class="px-4 py-8 text-center text-gray-400">No requests found.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Reject Modal -->
    <div v-if="rejectModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="rejectModal = false">
      <div class="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-md space-y-4">
        <h3 class="text-lg font-semibold text-gray-800 dark:text-white">Rejection Reason</h3>
        <textarea v-model="rejectReason" rows="3" class="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:outline-none" placeholder="Min 5 characters..."></textarea>
        <div class="flex justify-end gap-2">
          <button @click="rejectModal = false" class="px-4 py-2 text-sm rounded-lg border border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-300">Cancel</button>
          <button @click="confirmReject" :disabled="rejectReason.length < 5" class="px-4 py-2 text-sm rounded-lg bg-red-500 text-white hover:bg-red-600 disabled:opacity-50">Reject</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useLeaveStore } from '../../stores/leaves'
import { useToastStore } from '../../stores/toast'

const leaveStore = useLeaveStore()
const toastStore = useToastStore()

const allLeaves = ref([])
const filter = ref('')
const statuses = ['', 'pending', 'approved', 'rejected', 'cancelled']
const rejectModal = ref(false)
const rejectId = ref('')
const rejectReason = ref('')

const filtered = computed(() =>
  filter.value ? allLeaves.value.filter(l => l.status === filter.value) : allLeaves.value
)

onMounted(async () => {
  allLeaves.value = await leaveStore.fetchAllLeaves() || []
})

async function approve(id) {
  try {
    await leaveStore.approveLeave(id)
    allLeaves.value = await leaveStore.fetchAllLeaves() || []
    toastStore.show('Leave approved', 'success')
  } catch (e) {
    toastStore.show(e.response?.data?.detail || 'Failed', 'error')
  }
}

function openReject(id) {
  rejectId.value = id
  rejectReason.value = ''
  rejectModal.value = true
}

async function confirmReject() {
  try {
    await leaveStore.rejectLeave(rejectId.value, rejectReason.value)
    rejectModal.value = false
    allLeaves.value = await leaveStore.fetchAllLeaves() || []
    toastStore.show('Leave rejected', 'success')
  } catch (e) {
    toastStore.show(e.response?.data?.detail || 'Failed', 'error')
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
