import { defineStore } from 'pinia'
import axios from 'axios'

export const useGoldStore = defineStore('gold', {
  state: () => ({
    loading: false,
    error: null,
    chart: {
      labels: [],
      series: [], // [{ name, data }]
    },
  }),

  getters: {
    // Chart.js에 바로 넣을 datasets로 변환
    datasets: (state) =>
      state.chart.series.map((s) => ({
        label: s.name,
        data: s.data,
        tension: 0.3,
        spanGaps: true,
      })),
  },

  actions: {
    async fetchGoldChart({ rows = 60, page = 1 } = {}) {
      this.loading = true
      this.error = null
      try {
        // ✅ 백엔드 URL에 맞게 수정 (/api/ prefix 등)
        const { data } = await axios.get('http://localhost:8000/api/charts/gold/', {
          params: { numOfRows: rows, pageNo: page }, // 백엔드에서 받게 해놨다면
        })

        // 기대 형태: { labels: [...], series: [...] }
        this.chart = {
          labels: data.labels ?? [],
          series: data.series ?? [],
        }

        return this.chart
      } catch (e) {
        console.error(e)
        this.error = e
        throw e
      } finally {
        this.loading = false
      }
    },
  },
})
