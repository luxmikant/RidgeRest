<template>
  <div class="max-w-2xl mx-auto">
    <h1 class="text-2xl font-bold text-gray-800 dark:text-white mb-6">Apply for Leave</h1>

    <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 space-y-5">
      <!-- Balance preview -->
      <BalanceBadge :balance="balance" />

      <form @submit.prevent="handleSubmit" class="space-y-4 mt-4">
        <div>
          <label class="label">Leave Type</label>
          <select v-model="form.leave_type" class="input">
            <option value="sick">Sick Leave</option>
            <option value="casual">Casual Leave</option>
            <option value="annual">Annual Leave</option>
          </select>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Start Date</label>
            <input v-model="form.start_date" type="date" :min="today" required class="input" />
          </div>
          <div>
            <label class="label">End Date</label>
            <input v-model="form.end_date" type="date" :min="form.start_date || today" required class="input" />
          </div>
        </div>

        <div>
          <label class="label">Reason</label>
          <textarea v-model="form.reason" rows="3" required minlength="5" class="input" placeholder="Brief reason for leave..."></textarea>
        </div>

        <p v-if="error" class="text-red-500 text-sm">{{ error }}</p>
        <p v-if="success" class="text-green-500 text-sm">{{ success }}</p>

        <button type="submit" :disabled="loading" class="w-full py-2.5 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 disabled:opacity-50 transition">
          {{ loading ? 'Submitting...' : 'Submit Application' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useLeaveStore } from '../../stores/leaves'
import BalanceBadge from '../../components/BalanceBadge.vue'

const leaveStore = useLeaveStore()
const balance = ref({})

const today = new Date().toISOString().split('T')[0]
const form = ref({ leave_type: 'casual', start_date: '', end_date: '', reason: '' })
const error = ref('')
const success = ref('')
const loading = ref(false)

onMounted(async () => {
  balance.value = await leaveStore.fetchBalance()
})

async function handleSubmit() {
  error.value = ''
  success.value = ''
  loading.value = true
  try {
    await leaveStore.applyLeave(form.value)
    success.value = 'Leave application submitted!'
    form.value = { leave_type: 'casual', start_date: '', end_date: '', reason: '' }
    balance.value = await leaveStore.fetchBalance()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to apply'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.label { @apply block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1; }
.input { @apply w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:outline-none; }
</style>
