<template>
  <div class="page">
    <div class="container py-4">
      <!-- 헤더 -->
      <div class="head">
        <div class="ui-badge">Products</div>
        <h1 class="ui-title serif-title">예금 비교</h1>
        <p class="ui-sub">은행/상품명/기간으로 필터링해서 금리를 한눈에 비교해보세요.</p>
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
      <div class="box ui-card mb">
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
              <button class="ui-btn ui-btn-primary w100" @click="handleFetchProducts" :disabled="loading">
                {{ loading ? '조회 중...' : '조회' }}
              </button>
            </div>

            <div class="field">
              <label class="label">&nbsp;</label>
              <button class="ui-btn ui-btn-ghost w100" @click="resetFilters" :disabled="loading">
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
      <div v-else class="box ui-card">
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
  background:
    radial-gradient(900px 300px at 10% 0%, rgba(27, 95, 122, 0.10), transparent 60%),
    linear-gradient(180deg, var(--bg-alt) 0%, var(--bg) 100%);
}

/* 헤더 */
.head { margin-bottom: 14px; }
.ui-title { margin: 10px 0 6px; }
.ui-sub { margin: 0; }

/* 탭 */
.tabs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-bottom: 12px;
}
.tab {
  height: var(--btn-h);
  border-radius: 14px;
  border: 1px solid var(--border);
  background: var(--surface);
  font-weight: 700;
  color: var(--ink-soft);
  cursor: pointer;
  box-shadow: var(--shadow-1);
}
.tab.active {
  background: var(--accent);
  border-color: var(--accent);
  color: #fff;
}

/* 박스 */
.box {
  border-radius: 16px;
  overflow: hidden;
}
.box-head {
  padding: 14px 14px 10px;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
}
.box-title { font-weight: 700; letter-spacing: -0.2px; color: var(--ink); }
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
.label { font-size: 12px; font-weight: 700; color: var(--ink); }

.input, .select {
  height: 42px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  background: var(--surface);
  padding: 0 12px;
  font-size: 14px;
  outline: none;
}
.input:focus, .select:focus {
  border-color: rgba(27, 95, 122, 0.5);
  box-shadow: 0 0 0 0.2rem rgba(27, 95, 122, 0.15);
}


/* 로딩 */
.state { text-align: center; padding: 48px 0; }
.state-sub { margin-top: 12px; color: var(--muted); font-size: 13px; }

.muted { color: var(--muted); font-size: 13px; }
.strong { color: var(--ink); }

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
  font-weight: 700;
  color: var(--ink);
  background: var(--bg-alt);
  border-bottom: 1px solid var(--border);
  padding: 10px 10px;
  white-space: nowrap;
}
.t tbody td {
  font-size: 13px;
  color: var(--ink-soft);
  border-bottom: 1px solid var(--border);
  padding: 10px 10px;
  vertical-align: middle;
}
.row-click { cursor: pointer; }
.row-click:hover { background: var(--bg-alt); }

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
  color: var(--muted);
  padding: 22px 0;
}

/* 하단 힌트 */
.hint {
  margin-top: 10px;
  font-size: 12px;
  color: var(--muted);
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
