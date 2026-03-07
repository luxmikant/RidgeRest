<template>
  <div class="max-w-5xl mx-auto space-y-6">
    <h1 class="text-2xl font-bold text-gray-800 dark:text-white">Employer Dashboard</h1>

    <!-- Stats cards -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
      <div v-for="card in stats" :key="card.label"
        class="bg-white dark:bg-gray-800 rounded-xl shadow p-5 text-center">
        <p class="text-3xl font-bold" :class="card.color">{{ card.value }}</p>
        <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">{{ card.label }}</p>
      </div>
    </div>

    <!-- Quick links -->
    <div class="flex gap-4">
      <router-link to="/employer/requests"
        class="px-5 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition text-sm font-medium">
        Review Requests
      </router-link>
      <router-link to="/employer/calendar"
        class="px-5 py-2.5 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition text-sm font-medium">
        Team Calendar
      </router-link>
      <router-link to="/employer/analytics"
        class="px-5 py-2.5 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition text-sm font-medium">
        Analytics
      </router-link>
    </div>

    <!-- Recent pending -->
    <section>
      <h2 class="text-lg font-semibold text-gray-700 dark:text-gray-300 mb-3">Pending Requests</h2>
      <div v-if="!pending.length" class="text-gray-400 text-sm">No pending requests.</div>
      <div class="space-y-2">
        <div v-for="leave in pending" :key="leave._id"
          class="bg-white dark:bg-gray-800 rounded-lg shadow p-4 flex justify-between items-center">
          <div>
            <span class="font-medium text-gray-800 dark:text-gray-200">{{ leave.employee_name }}</span>
            <span class="text-xs text-gray-500 ml-2 capitalize">{{ leave.leave_type }}</span>
            <span class="text-xs text-gray-400 ml-2">{{ leave.start_date }} → {{ leave.end_date }}</span>
          </div>
          <div class="flex gap-2">
            <button @click="approve(leave._id)" class="text-xs px-3 py-1 rounded bg-green-500 text-white hover:bg-green-600">Approve</button>
            <button @click="openReject(leave._id)" class="text-xs px-3 py-1 rounded bg-red-500 text-white hover:bg-red-600">Reject</button>
          </div>
        </div>
      </div>
    </section>

    <!-- Reject modal -->
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
const rejectModal = ref(false)
const rejectId = ref('')
const rejectReason = ref('')

const pending = computed(() => allLeaves.value.filter(l => l.status === 'pending'))

const stats = computed(() => [
  { label: 'Total Requests', value: allLeaves.value.length, color: 'text-blue-600' },
  { label: 'Pending', value: pending.value.length, color: 'text-yellow-600' },
  { label: 'Approved', value: allLeaves.value.filter(l => l.status === 'approved').length, color: 'text-green-600' },
  { label: 'Rejected', value: allLeaves.value.filter(l => l.status === 'rejected').length, color: 'text-red-600' },
])

onMounted(async () => {
  allLeaves.value = await leaveStore.fetchAllLeaves() || []
})

async function approve(id) {
  try {
    await leaveStore.approveLeave(id)
    allLeaves.value = await leaveStore.fetchAllLeaves() || []
    toastStore.show('Leave approved', 'success')
  } catch (e) {
    toastStore.show(e.response?.data?.detail || 'Failed to approve', 'error')
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
    toastStore.show(e.response?.data?.detail || 'Failed to reject', 'error')
  }
}
</script>
