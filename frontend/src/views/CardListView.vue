<template>
  <div class="container py-5">
    <!-- 헤더 -->
    <div class="text-center mb-5">
      <h1 class="display-5 fw-bold">카드 검색</h1>
      <p class="text-muted">원하는 카드를 검색하고 비교해보세요</p>
    </div>

    <!-- 검색 및 필터 -->
    <div class="row justify-content-center mb-4">
      <div class="col-lg-10">
        <div class="card shadow-sm">
          <div class="card-body">
            <div class="row g-3">
              <!-- 검색어 -->
              <div class="col-md-5">
                <div class="input-group">
                  <input
                    v-model="searchQuery"
                    type="text"
                    class="form-control"
                    placeholder="카드명, 카드사, 혜택 검색..."
                    @keyup.enter="handleSearch"
                  />
                  <button class="btn btn-primary" @click="handleSearch">
                    검색
                  </button>
                </div>
              </div>

              <!-- 카드사 필터 -->
              <div class="col-md-3">
                <select v-model="selectedCompany" class="form-select" @change="handleSearch">
                  <option value="">전체 카드사</option>
                  <option v-for="company in companies" :key="company" :value="company">
                    {{ company }}
                  </option>
                </select>
              </div>

              <!-- 카드 타입 필터 -->
              <div class="col-md-3">
                <select v-model="selectedCardType" class="form-select" @change="handleSearch">
                  <option value="">전체 카드</option>
                  <option value="credit">신용카드</option>
                  <option value="check">체크카드</option>
                </select>
              </div>

              <!-- 초기화 -->
              <div class="col-md-1">
                <button class="btn btn-outline-secondary w-100" @click="resetFilters" title="필터 초기화">
                  초기화
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 로딩 -->
    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;"></div>
      <p class="mt-3 text-muted">카드를 불러오는 중...</p>
    </div>

    <!-- 에러 -->
    <div v-else-if="error" class="row justify-content-center">
      <div class="col-lg-8">
        <div class="alert alert-danger">{{ error }}</div>
      </div>
    </div>

    <!-- 카드 목록 -->
    <div v-else>
      <div class="d-flex justify-content-between align-items-center mb-3">
        <span class="text-muted">
          총 <strong>{{ pagination.count }}</strong>개의 카드
        </span>
      </div>

      <div class="row g-4">
        <div
          v-for="card in cards"
          :key="card.id"
          class="col-md-6 col-lg-4"
        >
          <div
            class="card h-100 shadow-sm card-hover"
            @click="goToDetail(card.id)"
            style="cursor: pointer;"
          >
            <!-- 카드 이미지 -->
            <div class="card-img-top bg-light d-flex align-items-center justify-content-center" style="height: 160px;">
              <img
                :src="card.image_url"
                :alt="card.name"
                class="img-fluid"
                style="max-height: 140px; max-width: 90%; object-fit: contain;"
                @error="handleImageError"
              />
            </div>

            <div class="card-body">
              <!-- 뱃지 -->
              <div class="mb-2">
                <span class="badge bg-secondary me-1">{{ card.company }}</span>
                <span class="badge" :class="card.card_type === 'credit' ? 'bg-primary' : 'bg-success'">
                  {{ card.card_type === 'credit' ? '신용' : '체크' }}
                </span>
                <span v-if="card.ranking" class="badge bg-warning text-dark ms-1">
                  {{ card.ranking }}위
                </span>
              </div>

              <!-- 카드명 -->
              <h6 class="card-title mb-2">{{ card.name }}</h6>

              <!-- 혜택 -->
              <p class="card-text text-muted small mb-2">
                {{ card.main_benefit || '혜택 정보 없음' }}
              </p>

              <!-- 연회비 -->
              <div class="text-end">
                <small class="text-muted">{{ card.annual_fee || '연회비 정보 없음' }}</small>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 결과 없음 -->
      <div v-if="cards.length === 0" class="text-center py-5">
        <i class="bi bi-credit-card" style="font-size: 4rem; color: #ccc;"></i>
        <p class="mt-3 text-muted fs-5">검색 결과가 없습니다</p>
      </div>

      <!-- 페이지네이션 -->
      <nav v-if="pagination.totalPages > 1" class="mt-5">
        <ul class="pagination justify-content-center">
          <li class="page-item" :class="{ disabled: pagination.page <= 1 }">
            <a class="page-link" href="#" @click.prevent="goToPage(pagination.page - 1)">이전</a>
          </li>
          <li
            v-for="p in visiblePages"
            :key="p"
            class="page-item"
            :class="{ active: p === pagination.page }"
          >
            <a class="page-link" href="#" @click.prevent="goToPage(p)">{{ p }}</a>
          </li>
          <li class="page-item" :class="{ disabled: pagination.page >= pagination.totalPages }">
            <a class="page-link" href="#" @click.prevent="goToPage(pagination.page + 1)">다음</a>
          </li>
        </ul>
      </nav>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCardsStore } from '@/stores/cards'
import { storeToRefs } from 'pinia'

const router = useRouter()
const cardsStore = useCardsStore()
const { cards, companies, isLoading, error, pagination } = storeToRefs(cardsStore)

const searchQuery = ref('')
const selectedCompany = ref('')
const selectedCardType = ref('')

// 페이지네이션 표시
const visiblePages = computed(() => {
  const total = pagination.value.totalPages
  const current = pagination.value.page
  const pages = []
  const range = 2

  for (let i = Math.max(1, current - range); i <= Math.min(total, current + range); i++) {
    pages.push(i)
  }
  return pages
})

onMounted(async () => {
  await cardsStore.fetchCompanies()
  await loadCards()
})

async function loadCards() {
  const params = {
    page: pagination.value.page,
    page_size: 12
  }

  if (searchQuery.value) params.q = searchQuery.value
  if (selectedCompany.value) params.company = selectedCompany.value
  if (selectedCardType.value) params.card_type = selectedCardType.value

  await cardsStore.fetchCards(params)
}

function handleSearch() {
  pagination.value.page = 1
  loadCards()
}

function resetFilters() {
  searchQuery.value = ''
  selectedCompany.value = ''
  selectedCardType.value = ''
  pagination.value.page = 1
  loadCards()
}

function goToPage(page) {
  if (page < 1 || page > pagination.value.totalPages) return
  pagination.value.page = page
  loadCards()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function goToDetail(cardId) {
  router.push({ name: 'card-detail', params: { id: cardId } })
}

function handleImageError(event) {
  event.target.src = 'https://placehold.co/200x120/f8f9fa/999?text=No+Image'
}
</script>

<style scoped>
.card-hover {
  transition: transform 0.2s, box-shadow 0.2s;
}

.card-hover:hover {
  transform: translateY(-5px);
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15) !important;
}
</style>
