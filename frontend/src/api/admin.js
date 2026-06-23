import api from './chat.js'

export async function getDashboard() {
  const { data } = await api.get('/admin/dashboard')
  return data
}

export async function getInteractions(params = {}) {
  const { data } = await api.get('/admin/interactions', { params })
  return data
}

export async function getTrend(days = 30) {
  const { data } = await api.get('/admin/trend', { params: { days } })
  return data
}

export async function getPopular(limit = 10, days = 7) {
  const { data } = await api.get('/admin/popular', { params: { limit, days } })
  return data
}

export async function getHourly(date = '') {
  const { data } = await api.get('/admin/hourly', { params: { date } })
  return data
}

export async function getReport(days = 7) {
  const { data } = await api.get('/admin/report', { params: { days } })
  return data
}
