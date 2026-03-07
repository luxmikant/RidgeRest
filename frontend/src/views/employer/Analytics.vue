<template>
  <div class="max-w-6xl mx-auto space-y-6">
    <h1 class="text-2xl font-bold text-gray-800 dark:text-white">Leave Analytics</h1>

    <!-- Stat cards -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
      <div v-for="card in statCards" :key="card.label"
        class="bg-white dark:bg-gray-800 rounded-xl shadow p-5 text-center">
        <p class="text-3xl font-bold" :class="card.color">{{ card.value }}</p>
        <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">{{ card.label }}</p>
      </div>
    </div>

    <!-- Charts -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Status breakdown -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow p-5">
        <h3 class="text-sm font-semibold text-gray-600 dark:text-gray-300 mb-4">By Status</h3>
        <Doughnut v-if="statusChartData" :data="statusChartData" :options="chartOpts" />
      </div>

      <!-- Type breakdown -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow p-5">
        <h3 class="text-sm font-semibold text-gray-600 dark:text-gray-300 mb-4">By Type</h3>
        <Doughnut v-if="typeChartData" :data="typeChartData" :options="chartOpts" />
      </div>

      <!-- Monthly trend -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow p-5 md:col-span-2">
        <h3 class="text-sm font-semibold text-gray-600 dark:text-gray-300 mb-4">Monthly Trend</h3>
        <Bar v-if="monthlyChartData" :data="monthlyChartData" :options="barOpts" />
      </div>
    </div>

    <!-- Top employees -->
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow p-5">
      <h3 class="text-sm font-semibold text-gray-600 dark:text-gray-300 mb-4">Top Employees by Leave Count</h3>
      <div v-if="!data?.top_employees?.length" class="text-gray-400 text-sm">No data yet.</div>
      <div class="space-y-2">
        <div v-for="emp in data?.top_employees" :key="emp._id"
          class="flex justify-between items-center text-sm text-gray-700 dark:text-gray-300">
          <span>{{ emp.name }}</span>
          <span class="font-mono">{{ emp.count }} leaves</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Doughnut, Bar } from 'vue-chartjs'
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement } from 'chart.js'
import { useLeaveStore } from '../../stores/leaves'

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement)

const leaveStore = useLeaveStore()
const data = ref(null)

const chartOpts = { responsive: true, plugins: { legend: { position: 'bottom' } } }
const barOpts = { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } } }

const statusColors = { pending: '#eab308', approved: '#22c55e', rejected: '#ef4444', cancelled: '#6b7280' }
const typeColors = { sick: '#ef4444', casual: '#3b82f6', annual: '#10b981' }

const statCards = computed(() => {
  if (!data.value) return []
  const sc = data.value.status_counts || {}
  return [
    { label: 'Total', value: Object.values(sc).reduce((a, b) => a + b, 0), color: 'text-blue-600' },
    { label: 'Pending', value: sc.pending || 0, color: 'text-yellow-600' },
    { label: 'Approved', value: sc.approved || 0, color: 'text-green-600' },
    { label: 'Employees', value: data.value.total_employees || 0, color: 'text-purple-600' },
  ]
})

const statusChartData = computed(() => {
  if (!data.value?.status_counts) return null
  const sc = data.value.status_counts
  return {
    labels: Object.keys(sc),
    datasets: [{ data: Object.values(sc), backgroundColor: Object.keys(sc).map(k => statusColors[k] || '#6b7280') }]
  }
})

const typeChartData = computed(() => {
  if (!data.value?.type_counts) return null
  const tc = data.value.type_counts
  return {
    labels: Object.keys(tc),
    datasets: [{ data: Object.values(tc), backgroundColor: Object.keys(tc).map(k => typeColors[k] || '#6b7280') }]
  }
})

const monthlyChartData = computed(() => {
  if (!data.value?.monthly) return null
  const m = data.value.monthly
  return {
    labels: m.map(i => i.month),
    datasets: [{ data: m.map(i => i.count), backgroundColor: '#3b82f6', borderRadius: 6 }]
  }
})

onMounted(async () => {
  data.value = await leaveStore.fetchAnalytics()
})
</script>
