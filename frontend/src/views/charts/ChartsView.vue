<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { Chart } from 'chart.js/auto'
import { useGoldStore } from '@/stores/goldStore'
import { storeToRefs } from 'pinia'

const canvasRef = ref(null)
let chartInstance = null

const metal = ref('gold')   // gold | silver
const range = ref('3m')     // 7d/1m/3m/6m/1y/ytd/max/custom
const start = ref('')       // custom용 YYYY-MM-DD
const end = ref('')         // custom용 YYYY-MM-DD

const goldStore = useGoldStore()
const { chart, datasets, loading, error } = storeToRefs(goldStore)

const isCustom = computed(() => range.value === 'custom')
const hasData = computed(() => {
  if (!chart.value) return false
  if (!chart.value.labels?.length) return false

  // series 중 하나라도 null이 아닌 값이 있으면 true
  return chart.value.series?.some(s =>
    s.data?.some(v => v !== null)
  )
})


const renderChart = () => {
  if (!canvasRef.value) return

  if (!hasData.value) {
    // ❗ 데이터 없으면 차트 생성 안 함
    if (chartInstance) {
      chartInstance.destroy()
      chartInstance = null
    }
    return
  }

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
      plugins: {
        legend: { display: true },
      },
      scales: {
        y: { beginAtZero: false },
      },
    },
  })
}




const load = async () => {
  await goldStore.fetchGoldChart({
    metal: metal.value,
    range: range.value,
    start: isCustom.value ? start.value : null,
    end: isCustom.value ? end.value : null,
    rows: 60, // max일 때만 의미 있음(기간 필터 없을 때)
  })
  renderChart()
}

onMounted(load)

// 차트 데이터 바뀌면 재렌더
watch(
  () => [chart.value.labels, chart.value.series],
  () => renderChart(),
  { deep: true }
)

// 선택 변경 시 재조회
watch([metal, range], () => load())

// custom 날짜 변경 시 재조회 (둘 다 들어왔을 때만)
watch([start, end], () => {
  if (!isCustom.value) return
  if (start.value && end.value) load()
})
</script>

<template>
  <div class="card p-3">
    <div class="d-flex flex-wrap gap-2 align-items-center justify-content-between mb-2">
      <div class="fw-bold">금/은 시세 추이</div>

      <div class="d-flex gap-2 align-items-center">
        <select v-model="metal" class="form-select form-select-sm" style="width: 120px;">
          <option value="gold">Gold</option>
          <option value="silver">Silver</option>
        </select>

        <select v-model="range" class="form-select form-select-sm" style="width: 140px;">
          <option value="7d">7D</option>
          <option value="1m">1M</option>
          <option value="3m">3M</option>
          <option value="6m">6M</option>
          <option value="1y">1Y</option>
          <option value="ytd">YTD</option>
          <option value="max">MAX</option>
          <option value="custom">CUSTOM</option>
        </select>

        <div v-if="range === 'custom'" class="d-flex gap-2 align-items-center">
          <input v-model="start" type="date" class="form-control form-control-sm" />
          <span class="text-muted">~</span>
          <input v-model="end" type="date" class="form-control form-control-sm" />
        </div>
      </div>
    </div>

    <div v-if="loading" class="text-muted">로딩중...</div>
    <div v-else-if="error" class="text-danger">불러오기 실패</div>
    <!-- ❗ 데이터 없음 -->
    <div
      v-else-if="!hasData"
      class="text-muted text-center py-5"
    >
      선택한 기간에 데이터가 없습니다.
    </div>

    <!-- 차트 -->
    <canvas v-else ref="canvasRef"></canvas>
  </div>
</template>
