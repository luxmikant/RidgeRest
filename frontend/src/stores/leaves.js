import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api'

export const useLeaveStore = defineStore('leaves', () => {
  const myLeaves = ref([])
  const allLeaves = ref([])
  const balance = ref(null)
  const loading = ref(false)

  async function fetchMyLeaves(status = null) {
    loading.value = true
    try {
      const params = status ? { status } : {}
      const res = await api.get('/api/leaves/my', { params })
      myLeaves.value = res.data
    } finally {
      loading.value = false
    }
  }

  async function fetchAllLeaves(filters = {}) {
    loading.value = true
    try {
      const res = await api.get('/api/leaves/', { params: filters })
      allLeaves.value = res.data
    } finally {
      loading.value = false
    }
  }

  async function applyLeave(data) {
    const res = await api.post('/api/leaves/', data)
    return res.data
  }

  async function cancelLeave(leaveId) {
    await api.delete(`/api/leaves/${leaveId}`)
  }

  async function approveLeave(leaveId) {
    const res = await api.patch(`/api/leaves/${leaveId}/approve`)
    return res.data
  }

  async function rejectLeave(leaveId, rejectionReason) {
    const res = await api.patch(`/api/leaves/${leaveId}/reject`, {
      rejection_reason: rejectionReason,
    })
    return res.data
  }

  async function fetchBalance() {
    try {
      const res = await api.get('/api/balance/')
      balance.value = res.data
    } catch {
      balance.value = null
    }
  }

  async function fetchEmployeeBalance(employeeId) {
    const res = await api.get(`/api/balance/${employeeId}`)
    return res.data
  }

  async function fetchAnalytics() {
    const res = await api.get('/api/analytics/overview')
    return res.data
  }

  return {
    myLeaves, allLeaves, balance, loading,
    fetchMyLeaves, fetchAllLeaves, applyLeave, cancelLeave,
    approveLeave, rejectLeave, fetchBalance, fetchEmployeeBalance, fetchAnalytics,
  }
})
