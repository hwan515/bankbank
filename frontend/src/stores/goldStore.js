import { defineStore } from 'pinia'
import axios from 'axios'

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  import.meta.env.VITE_API_URL ||
  'http://localhost:8000'
const apiBaseUrl = API_BASE_URL.replace(/\/$/, '')

export const useGoldStore = defineStore('gold', {
  state: () => ({
    chart: { labels: [], series: [] },
    datasets: [],
    loading: false,
    error: null,
  }),

  actions: {
    async fetchGoldChart({ metal = 'gold', range = '3m', rows = 60, start = null, end = null } = {}) {
      this.loading = true
      this.error = null
      try {
        const params = { metal, range, rows }
        if (range === 'custom') {
          if (start) params.start = start
          if (end) params.end = end
        }

        const { data } = await axios.get(`${apiBaseUrl}/api/metals/chart/`, { params })

        this.chart = data
        this.datasets = (data.series || []).map((s) => ({
          label: s.name,
          data: s.data,
          borderWidth: 2,
          tension: 0.25,

          spanGaps: false,        // ✅ null에서 선 끊기
          pointRadius: (ctx) => {
            return ctx.raw === null ? 0 : 2   // ✅ null 포인트 숨김
          },
          pointHoverRadius: 4,
        }))
      } catch (e) {
        this.error = e
      } finally {
        this.loading = false
      }
    },
  },
})
