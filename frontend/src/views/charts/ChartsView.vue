<script setup>
import { ref, onMounted, watch } from 'vue'
import { Chart } from 'chart.js/auto'
import { useGoldStore } from '@/stores/gold'
import { storeToRefs } from 'pinia'

const canvasRef = ref(null)
let chartInstance = null

const goldStore = useGoldStore()
const { chart, datasets, loading, error } = storeToRefs(goldStore)

const renderChart = () => {
  if (!canvasRef.value) return
  if (chartInstance) chartInstance.destroy()

  chartInstance = new Chart(canvasRef.value, {
    type: 'line',
    data: {
      labels: chart.value.labels,
      datasets: datasets.value,
    },
    options: {
      responsive: true,
      interaction: { mode: 'index', intersect: false },
      plugins: { legend: { display: true } },
      scales: { y: { beginAtZero: false } },
    },
  })
}

onMounted(async () => {
  await goldStore.fetchGoldChart({ rows: 60, page: 1 })
  renderChart()
})

// 데이터 바뀌면 재렌더
watch(
  () => [chart.value.labels, chart.value.series],
  () => renderChart(),
  { deep: true }
)
</script>

<template>
  <div class="card p-3">
    <div class="fw-bold mb-2">금 시세 추이</div>

    <div v-if="loading" class="text-muted">로딩중...</div>
    <div v-else-if="error" class="text-danger">불러오기 실패</div>
    <canvas v-else ref="canvasRef"></canvas>
  </div>
</template>
