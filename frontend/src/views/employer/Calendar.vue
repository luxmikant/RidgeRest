<template>
  <div class="max-w-6xl mx-auto">
    <h1 class="text-2xl font-bold text-gray-800 dark:text-white mb-6">Team Availability Calendar</h1>

    <div class="bg-white dark:bg-gray-800 rounded-xl shadow p-4">
      <FullCalendar :options="calendarOptions" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import FullCalendar from '@fullcalendar/vue3'
import dayGridPlugin from '@fullcalendar/daygrid'
import { useLeaveStore } from '../../stores/leaves'

const leaveStore = useLeaveStore()
const events = ref([])

const colors = {
  sick: '#ef4444',
  casual: '#3b82f6',
  annual: '#10b981',
}

const calendarOptions = ref({
  plugins: [dayGridPlugin],
  initialView: 'dayGridMonth',
  headerToolbar: {
    left: 'prev,next today',
    center: 'title',
    right: 'dayGridMonth',
  },
  events: [],
  height: 'auto',
})

onMounted(async () => {
  const leaves = await leaveStore.fetchAllLeaves({ status: 'approved' }) || []
  calendarOptions.value.events = leaves.map(l => ({
    title: `${l.employee_name} (${l.leave_type})`,
    start: l.start_date,
    end: addOneDay(l.end_date),
    color: colors[l.leave_type] || '#6b7280',
    allDay: true,
  }))
})

function addOneDay(dateStr) {
  const d = new Date(dateStr)
  d.setDate(d.getDate() + 1)
  return d.toISOString().split('T')[0]
}
</script>

<style>
.fc { font-size: 0.85rem; }
.fc .fc-toolbar-title { font-size: 1.1rem; font-weight: 600; }
.dark .fc { color: #e5e7eb; }
.dark .fc .fc-col-header-cell, .dark .fc .fc-daygrid-day { background: #1f2937; border-color: #374151; }
.dark .fc .fc-button { background: #374151; border-color: #4b5563; color: #e5e7eb; }
.dark .fc .fc-button:hover { background: #4b5563; }
.dark .fc .fc-button-active { background: #2563eb; }
.dark .fc .fc-today-button { background: #2563eb; }
</style>
