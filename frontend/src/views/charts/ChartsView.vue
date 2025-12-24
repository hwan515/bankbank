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
  <div class="page">
    <div class="container py-4">
      <div class="chart-card ui-card">
        <div class="title serif-title">금 시세 추이</div>

        <div v-if="loading" class="muted">로딩중...</div>
        <div v-else-if="error" class="ui-text-danger">불러오기 실패</div>
        <canvas v-else ref="canvasRef"></canvas>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page {
  min-height: 100%;
  background:
    radial-gradient(900px 300px at 10% 0%, rgba(27, 95, 122, 0.10), transparent 60%),
    linear-gradient(180deg, var(--bg-alt) 0%, var(--bg) 100%);
}

.chart-card {
  border-radius: var(--radius-md);
  padding: 18px;
}

.title {
  font-weight: 700;
  color: var(--ink);
  margin-bottom: 12px;
}

.muted {
  color: var(--muted);
}
</style>
