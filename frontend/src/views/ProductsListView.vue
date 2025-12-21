<template>
  <div class="container py-4">
    <h2 class="text-center mb-4">예금비교</h2>

    <!-- 탭: 정기예금 / 정기적금 -->
    <ul class="nav nav-tabs mb-4">
      <li class="nav-item">
        <button
          class="nav-link"
          :class="{ active: activeTab === 'deposit' }"
          @click="activeTab = 'deposit'"
        >
          정기예금
        </button>
      </li>
      <li class="nav-item">
        <button
          class="nav-link"
          :class="{ active: activeTab === 'saving' }"
          @click="activeTab = 'saving'"
        >
          정기적금
        </button>
      </li>
    </ul>

    <!-- 필터 영역 -->
    <div class="row mb-4">
      <div class="col-md-3">
        <label class="form-label">은행 선택</label>
        <select v-model="selectedBank" class="form-select">
          <option value="">전체</option>
          <option v-for="bank in banks" :key="bank" :value="bank">{{ bank }}</option>
        </select>
      </div>
      <div class="col-md-3">
        <label class="form-label">상품명 검색</label>
        <input
          v-model="searchKeyword"
          type="text"
          class="form-control"
          placeholder="상품명 입력"
        />
      </div>
      <div class="col-md-3">
        <label class="form-label">정렬기간</label>
        <select v-model="selectedTerm" class="form-select">
          <option value="">선택안함</option>
          <option value="6">6개월</option>
          <option value="12">12개월</option>
          <option value="24">24개월</option>
          <option value="36">36개월</option>
        </select>
      </div>
      <div class="col-md-3 d-flex align-items-end">
        <button @click="handleFetchProducts" class="btn btn-primary w-100">조회</button>
      </div>
    </div>

    <!-- 로딩 -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- 상품 테이블 -->
    <div v-else>
      <table class="table table-hover table-bordered">
        <thead class="table-dark">
          <tr>
            <th>공시제출월</th>
            <th>금융회사명</th>
            <th>상품명</th>
            <th>6개월</th>
            <th>12개월</th>
            <th>24개월</th>
            <th>36개월</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="product in products"
            :key="product.id"
            @click="goToDetail(product.id)"
            style="cursor: pointer;"
          >
            <td>{{ product.dcls_month }}</td>
            <td>{{ product.kor_co_nm }}</td>
            <td>{{ product.fin_prdt_nm }}</td>
            <td>{{ product.intr_rate_6 ? product.intr_rate_6 + '%' : '-' }}</td>
            <td>{{ product.intr_rate_12 ? product.intr_rate_12 + '%' : '-' }}</td>
            <td>{{ product.intr_rate_24 ? product.intr_rate_24 + '%' : '-' }}</td>
            <td>{{ product.intr_rate_36 ? product.intr_rate_36 + '%' : '-' }}</td>
          </tr>
          <tr v-if="products.length === 0">
            <td colspan="7" class="text-center text-muted py-4">
              조회된 상품이 없습니다.
            </td>
          </tr>
        </tbody>
      </table>
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
.nav-link {
  cursor: pointer;
}
.table tbody tr:hover {
  background-color: #f5f5f5;
}
</style>
