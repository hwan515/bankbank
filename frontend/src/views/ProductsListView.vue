<template>
  <div class="page">
    <div class="container py-4">
      <!-- 헤더 -->
      <div class="head">
        <div class="badge">Products</div>
        <h1 class="title">예금 비교</h1>
        <p class="sub">은행/상품명/기간으로 필터링해서 금리를 한눈에 비교해보세요.</p>
      </div>

      <!-- 탭 (미니멀 토글) -->
      <div class="tabs">
        <button class="tab" :class="{ active: activeTab === 'deposit' }" @click="activeTab = 'deposit'">
          정기예금
        </button>
        <button class="tab" :class="{ active: activeTab === 'saving' }" @click="activeTab = 'saving'">
          정기적금
        </button>
      </div>

      <!-- 필터 -->
      <div class="box mb">
        <div class="box-body">
          <div class="filter-grid">
            <div class="field">
              <label class="label">은행 선택</label>
              <select v-model="selectedBank" class="select">
                <option value="">전체</option>
                <option v-for="bank in banks" :key="bank" :value="bank">{{ bank }}</option>
              </select>
            </div>

            <div class="field span-2">
              <label class="label">상품명 검색</label>
              <input
                v-model="searchKeyword"
                type="text"
                class="input"
                placeholder="예: 우리, 정기예금, 우대, 청년..."
                @keyup.enter="handleFetchProducts"
              />
            </div>

            <div class="field">
              <label class="label">정렬기간</label>
              <select v-model="selectedTerm" class="select">
                <option value="">선택안함</option>
                <option value="6">6개월</option>
                <option value="12">12개월</option>
                <option value="24">24개월</option>
                <option value="36">36개월</option>
              </select>
            </div>

            <div class="field">
              <label class="label">&nbsp;</label>
              <button class="btn-solid w100" @click="handleFetchProducts" :disabled="loading">
                {{ loading ? '조회 중...' : '조회' }}
              </button>
            </div>

            <div class="field">
              <label class="label">&nbsp;</label>
              <button class="btn-ghost w100" @click="resetFilters" :disabled="loading">
                초기화
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 로딩 -->
      <div v-if="loading" class="state">
        <div class="spinner-border" style="width: 2.6rem; height: 2.6rem;"></div>
        <p class="state-sub">상품 목록을 불러오는 중...</p>
      </div>

      <!-- 테이블 -->
      <div v-else class="box">
        <div class="box-head">
          <div class="box-title">
            {{ activeTab === 'deposit' ? '정기예금' : '정기적금' }} 목록
          </div>
          <div class="muted">
            총 <strong class="strong">{{ products.length }}</strong>개
          </div>
        </div>

        <div class="box-body">
          <div class="table-wrap">
            <table class="t">
              <thead>
                <tr>
                  <th>공시</th>
                  <th>금융회사</th>
                  <th>상품명</th>
                  <th class="num">6개월</th>
                  <th class="num">12개월</th>
                  <th class="num">24개월</th>
                  <th class="num">36개월</th>
                </tr>
              </thead>

              <tbody>
                <tr
                  v-for="product in products"
                  :key="product.id"
                  class="row-click"
                  @click="goToDetail(product.id)"
                >
                  <td class="nowrap">{{ product.dcls_month }}</td>
                  <td class="nowrap">{{ product.kor_co_nm }}</td>
                  <td class="name" :title="product.fin_prdt_nm">{{ product.fin_prdt_nm }}</td>

                  <td class="num">{{ product.intr_rate_6 != null ? product.intr_rate_6 + '%' : '-' }}</td>
                  <td class="num">{{ product.intr_rate_12 != null ? product.intr_rate_12 + '%' : '-' }}</td>
                  <td class="num">{{ product.intr_rate_24 != null ? product.intr_rate_24 + '%' : '-' }}</td>
                  <td class="num">{{ product.intr_rate_36 != null ? product.intr_rate_36 + '%' : '-' }}</td>
                </tr>

                <tr v-if="products.length === 0">
                  <td colspan="7" class="empty">
                    조회된 상품이 없습니다.
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="hint">
            * 행을 클릭하면 상세 페이지로 이동합니다.
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useProductsStore } from '@/stores/products'
import { storeToRefs } from 'pinia'

const router = useRouter()
const productsStore = useProductsStore()

const { loading, banks, depositProducts, savingProducts } = storeToRefs(productsStore)

// 로컬 UI 상태
const activeTab = ref('deposit')
const selectedBank = ref('')
const searchKeyword = ref('')
const selectedTerm = ref('')

// 현재 탭에 따른 상품 목록
const products = computed(() =>
  activeTab.value === 'deposit' ? depositProducts.value : savingProducts.value
)

const handleFetchProducts = async () => {
  const filters = {}
  if (selectedBank.value) filters.bank = selectedBank.value
  if (searchKeyword.value) filters.search = searchKeyword.value
  if (selectedTerm.value) filters.ordering = `intr_rate_${selectedTerm.value}`

  try {
    await productsStore.fetchProducts(activeTab.value, filters)
  } catch (err) {
    console.error('상품 목록 조회 실패:', err)
  }
}

const resetFilters = () => {
  selectedBank.value = ''
  searchKeyword.value = ''
  selectedTerm.value = ''
  handleFetchProducts()
}

const goToDetail = (id) => {
  const routeName = activeTab.value === 'deposit' ? 'deposit-detail' : 'saving-detail'
  router.push({ name: routeName, params: { id } })
}

watch(activeTab, () => {
  handleFetchProducts()
})

onMounted(async () => {
  await productsStore.fetchBanks()
  await handleFetchProducts()
})
</script>

<style scoped>
/* 배경 */
.page {
  min-height: 100%;
  background: linear-gradient(180deg, #fafafa 0%, #ffffff 100%);
}

/* 헤더 */
.head { margin-bottom: 14px; }
.badge {
  display: inline-flex;
  align-items: center;
  height: 26px;
  padding: 0 10px;
  border-radius: 999px;
  border: 1px solid #ededed;
  background: #f6f6f6;
  color: #333;
  font-size: 12px;
  font-weight: 900;
}
.title {
  margin: 10px 0 6px;
  font-size: 26px;
  font-weight: 950;
  letter-spacing: -0.4px;
  color: #111;
}
.sub { margin: 0; font-size: 13px; color: #777; }

/* 탭 */
.tabs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-bottom: 12px;
}
.tab {
  height: 42px;
  border-radius: 14px;
  border: 1px solid #efefef;
  background: #fff;
  font-weight: 900;
  color: #444;
  cursor: pointer;
  box-shadow: 0 1px 2px rgba(0,0,0,0.06), 0 8px 18px rgba(0,0,0,0.05);
}
.tab.active {
  background: #111;
  border-color: #111;
  color: #fff;
}

/* 박스 */
.box {
  background: #fff;
  border: 1px solid #efefef;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 1px 2px rgba(0,0,0,0.08), 0 10px 24px rgba(0,0,0,0.06);
}
.box-head {
  padding: 14px 14px 10px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
}
.box-title { font-weight: 900; letter-spacing: -0.2px; color: #111; }
.box-body { padding: 14px; }

.mb { margin-bottom: 14px; }

/* 필터 */
.filter-grid {
  display: grid;
  grid-template-columns: 1.2fr 2fr 1fr 140px 140px;
  gap: 12px;
  align-items: end;
}
.field { display: grid; gap: 6px; }
.label { font-size: 12px; font-weight: 900; color: #111; }

.input, .select {
  height: 42px;
  border-radius: 12px;
  border: 1px solid #eaeaea;
  background: #fff;
  padding: 0 12px;
  font-size: 14px;
  outline: none;
}
.input:focus, .select:focus {
  border-color: #d8d8d8;
  box-shadow: 0 0 0 0.2rem rgba(0,0,0,0.06);
}

.btn-solid {
  height: 42px;
  border-radius: 12px;
  border: 1px solid #111;
  background: #111;
  color: #fff;
  font-weight: 900;
  font-size: 13px;
  padding: 0 14px;
  cursor: pointer;
}
.btn-solid:hover { background: #000; }
.btn-solid:disabled { opacity: .6; cursor: not-allowed; }

.btn-ghost {
  height: 42px;
  border-radius: 12px;
  border: 1px solid #e8e8e8;
  background: #fff;
  color: #222;
  font-weight: 900;
  font-size: 13px;
  cursor: pointer;
}
.btn-ghost:hover { background: #fafafa; }
.w100 { width: 100%; }

/* 로딩 */
.state { text-align: center; padding: 48px 0; }
.state-sub { margin-top: 12px; color: #777; font-size: 13px; }

.muted { color: #777; font-size: 13px; }
.strong { color: #111; }

/* 테이블 */
.table-wrap { overflow-x: auto; }
.t {
  width: 100%;
  border-collapse: collapse;
  min-width: 860px;
}
.t thead th {
  text-align: left;
  font-size: 12px;
  font-weight: 900;
  color: #111;
  background: #fafafa;
  border-bottom: 1px solid #efefef;
  padding: 10px 10px;
  white-space: nowrap;
}
.t tbody td {
  font-size: 13px;
  color: #444;
  border-bottom: 1px solid #f2f2f2;
  padding: 10px 10px;
  vertical-align: middle;
}
.row-click { cursor: pointer; }
.row-click:hover { background: #fafafa; }

.num { text-align: right; white-space: nowrap; }
.nowrap { white-space: nowrap; }
.name {
  max-width: 420px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* empty */
.empty {
  text-align: center;
  color: #777;
  padding: 22px 0;
}

/* 하단 힌트 */
.hint {
  margin-top: 10px;
  font-size: 12px;
  color: #777;
}

/* 반응형 */
@media (max-width: 992px) {
  .filter-grid {
    grid-template-columns: 1fr 1fr;
  }
  .tabs { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 576px) {
  .tabs { grid-template-columns: 1fr; }
  .filter-grid { grid-template-columns: 1fr; }
  .name { max-width: 260px; }
}
</style>
