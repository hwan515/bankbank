<template>
  <div class="container py-5">
    <!-- 헤더 -->
    <div class="text-center mb-4">
      <h1 class="display-5 fw-bold">카드</h1>
      <p class="text-muted">원하는 카드를 검색하거나 AI 추천을 받아보세요</p>
    </div>

    <!-- 탭 네비게이션 -->
    <ul class="nav nav-tabs nav-justified mb-4">
      <li class="nav-item">
        <button
          class="nav-link"
          :class="{ active: activeTab === 'search' }"
          @click="activeTab = 'search'"
        >
          <i class="bi bi-search me-2"></i>카드 검색
        </button>
      </li>
      <li class="nav-item">
        <button
          class="nav-link"
          :class="{ active: activeTab === 'recommend' }"
          @click="activeTab = 'recommend'"
        >
          <i class="bi bi-stars me-2"></i>AI 추천
        </button>
      </li>
    </ul>

    <!-- 탭 컨텐츠 -->
    <div class="tab-content">
      <!-- 카드 검색 탭 -->
      <div v-show="activeTab === 'search'">
        <!-- 검색 및 필터 -->
        <div class="card shadow-sm mb-4">
          <div class="card-body">
            <div class="row g-3">
              <div class="col-md-4">
                <div class="input-group">
                  <input
                    v-model="searchQuery"
                    type="text"
                    class="form-control"
                    placeholder="카드명, 카드사, 혜택 검색..."
                    @keyup.enter="handleSearch"
                  />
                  <button class="btn btn-primary" @click="handleSearch">검색</button>
                </div>
              </div>
              <div class="col-md-2">
                <select v-model="selectedCompany" class="form-select" @change="handleSearch">
                  <option value="">전체 카드사</option>
                  <option v-for="company in companies" :key="company" :value="company">
                    {{ company }}
                  </option>
                </select>
              </div>
              <div class="col-md-2">
                <select v-model="selectedCardType" class="form-select" @change="handleSearch">
                  <option value="">전체 카드</option>
                  <option value="CRD">신용카드</option>
                  <option value="CHK">체크카드</option>
                </select>
              </div>
              <div class="col-md-3">
                <select v-model="selectedCategory" class="form-select" @change="handleSearch">
                  <option value="">전체 카테고리</option>
                  <option v-for="(name, code) in categoryOptions" :key="code" :value="code">
                    {{ name }}
                  </option>
                </select>
              </div>
              <div class="col-md-1">
                <button class="btn btn-outline-secondary w-100" @click="resetFilters">초기화</button>
              </div>
            </div>
          </div>
        </div>

        <!-- 로딩 -->
        <LoadingSpinner
          v-if="isLoading && activeTab === 'search'"
          message="카드를 불러오는 중..."
          size="2rem"
        />

        <!-- 카드 목록 -->
        <div v-else>
          <div class="d-flex justify-content-between align-items-center mb-3">
            <span class="text-muted">총 <strong>{{ pagination.count }}</strong>개의 카드</span>
          </div>

          <div class="row g-4">
            <div v-for="card in cards" :key="card.id" class="col-md-6 col-lg-4">
              <div class="card h-100 shadow-sm card-hover" @click="goToDetail(card.id)" style="cursor: pointer;">
                <div class="card-img-top bg-light d-flex align-items-center justify-content-center" style="height: 160px;">
                  <CardImage
                    :src="card.image_url"
                    :alt="card.name"
                    img-style="max-height: 140px; object-fit: contain;"
                    placeholder-size="200x120"
                  />
                </div>
                <div class="card-body">
                  <div class="mb-2">
                    <span class="badge bg-secondary me-1">{{ card.company }}</span>
                    <span class="badge" :class="getCardTypeBadgeClass(card.card_type)">
                      {{ card.card_type === 'CRD' ? '신용' : '체크' }}
                    </span>
                    <span v-if="card.ranking" class="badge bg-warning text-dark ms-1">{{ card.ranking }}위</span>
                  </div>
                  <h6 class="card-title mb-2">{{ card.name }}</h6>
                  <p class="card-text text-muted small mb-2">{{ card.main_benefit || '혜택 정보 없음' }}</p>
                  <!-- 카테고리 표시 -->
                  <div v-if="card.category_names && card.category_names.length" class="mb-2">
                    <span
                      v-for="(catName, idx) in card.category_names.slice(0, 4)"
                      :key="idx"
                      class="badge bg-info bg-opacity-25 text-info me-1"
                    >{{ catName }}</span>
                  </div>
                  <div class="text-end">
                    <small class="text-muted">{{ card.annual_fee || '연회비 정보 없음' }}</small>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-if="cards.length === 0" class="text-center py-5">
            <p class="text-muted fs-5">검색 결과가 없습니다</p>
          </div>

          <!-- 페이지네이션 -->
          <nav v-if="pagination.totalPages > 1" class="mt-5">
            <ul class="pagination justify-content-center">
              <li class="page-item" :class="{ disabled: pagination.page <= 1 }">
                <a class="page-link" href="#" @click.prevent="goToPage(pagination.page - 1)">이전</a>
              </li>
              <li v-for="p in visiblePages" :key="p" class="page-item" :class="{ active: p === pagination.page }">
                <a class="page-link" href="#" @click.prevent="goToPage(p)">{{ p }}</a>
              </li>
              <li class="page-item" :class="{ disabled: pagination.page >= pagination.totalPages }">
                <a class="page-link" href="#" @click.prevent="goToPage(pagination.page + 1)">다음</a>
              </li>
            </ul>
          </nav>
        </div>
      </div>

      <!-- AI 추천 탭 -->
      <div v-show="activeTab === 'recommend'">
        <!-- 검색 영역 -->
        <div class="card shadow-sm mb-4">
          <div class="card-body p-4">
            <form @submit.prevent="handleRecommend">
              <div class="input-group input-group-lg mb-3">
                <input
                  v-model="recommendQuery"
                  type="text"
                  class="form-control"
                  placeholder="예: 스타벅스 할인 많은 카드, 주유 혜택 좋은 카드"
                  :disabled="isLoading"
                />
                <button type="submit" class="btn btn-primary px-4" :disabled="isLoading || !recommendQuery.trim()">
                  <span v-if="isLoading && activeTab === 'recommend'" class="spinner-border spinner-border-sm me-2"></span>
                  {{ isLoading && activeTab === 'recommend' ? '검색 중...' : '추천받기' }}
                </button>
              </div>

              <!-- 필터 옵션 (접이식) -->
              <div class="mb-3">
                <button
                  type="button"
                  class="btn btn-sm btn-outline-secondary"
                  @click="showFilters = !showFilters"
                >
                  <i class="bi" :class="showFilters ? 'bi-chevron-up' : 'bi-chevron-down'"></i>
                  필터 옵션 {{ showFilters ? '접기' : '펼치기' }}
                </button>
              </div>

              <div v-show="showFilters" class="row g-3 mb-3">
                <div class="col-md-3">
                  <label class="form-label small text-muted">카드사</label>
                  <select v-model="recFilters.company" class="form-select form-select-sm">
                    <option value="">전체</option>
                    <option v-for="c in companies" :key="c" :value="c">{{ c }}</option>
                  </select>
                </div>
                <div class="col-md-3">
                  <label class="form-label small text-muted">카드 종류</label>
                  <select v-model="recFilters.card_type" class="form-select form-select-sm">
                    <option value="">전체</option>
                    <option value="CRD">신용카드</option>
                    <option value="CHK">체크카드</option>
                  </select>
                </div>
                <div class="col-md-3">
                  <label class="form-label small text-muted">연회비 상한</label>
                  <select v-model="recFilters.max_annual_fee" class="form-select form-select-sm">
                    <option :value="null">제한 없음</option>
                    <option :value="0">무료</option>
                    <option :value="10000">1만원 이하</option>
                    <option :value="20000">2만원 이하</option>
                    <option :value="50000">5만원 이하</option>
                    <option :value="100000">10만원 이하</option>
                  </select>
                </div>
                <div class="col-md-3">
                  <label class="form-label small text-muted">전월실적 상한</label>
                  <select v-model="recFilters.max_min_spending" class="form-select form-select-sm">
                    <option :value="null">제한 없음</option>
                    <option :value="0">조건 없음</option>
                    <option :value="300000">30만원 이하</option>
                    <option :value="500000">50만원 이하</option>
                    <option :value="1000000">100만원 이하</option>
                  </select>
                </div>
              </div>
            </form>

            <div class="mt-3">
              <small class="text-muted">추천 질문:</small>
              <div class="d-flex flex-wrap gap-2 mt-2">
                <button
                  v-for="example in exampleQueries"
                  :key="example"
                  class="btn btn-outline-secondary btn-sm"
                  @click="setRecommendQuery(example)"
                  :disabled="isLoading"
                >
                  {{ example }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 에러 -->
        <div v-if="error && activeTab === 'recommend'" class="alert alert-danger">{{ error }}</div>

        <!-- 로딩 -->
        <LoadingSpinner
          v-if="isLoading && activeTab === 'recommend'"
          message="AI가 최적의 카드를 찾고 있습니다..."
        />

        <!-- 추천 결과 -->
        <div v-else-if="recommendedCards.length > 0">
          <h5 class="mb-4">
            <span class="badge bg-primary me-2">{{ recommendedCards.length }}</span>
            "{{ lastQuery }}" 검색 결과
          </h5>

          <div class="row g-4">
            <div v-for="(result, index) in recommendedCards" :key="result.card.gorilla_id" class="col-12">
              <div class="card shadow-sm h-100 card-hover" @click="goToDetail(result.card.id)" style="cursor: pointer;">
                <div class="card-body">
                  <div class="row align-items-center">
                    <div class="col-auto">
                      <div class="rounded-circle d-flex align-items-center justify-content-center" :class="getRankBadgeClass(index)" style="width: 50px; height: 50px;">
                        <span class="fw-bold fs-5">{{ index + 1 }}</span>
                      </div>
                    </div>
                    <div class="col-auto">
                      <CardImage
                        :src="result.card.image_url"
                        :alt="result.card.name"
                        img-class="rounded"
                        img-style="width: 120px; height: 76px; object-fit: contain; background: #f8f9fa;"
                        placeholder-size="120x76"
                      />
                    </div>
                    <div class="col">
                      <div class="d-flex align-items-center mb-1">
                        <span class="badge bg-secondary me-2">{{ result.card.company }}</span>
                        <span v-if="result.card.ranking" class="badge bg-warning text-dark">인기 {{ result.card.ranking }}위</span>
                      </div>
                      <h5 class="card-title mb-1">{{ result.card.name }}</h5>
                      <p class="text-muted mb-2 small">{{ result.preview }}</p>
                      <!-- 카테고리 표시 -->
                      <div v-if="result.card.category_names && result.card.category_names.length" class="mb-2">
                        <span
                          v-for="(catName, idx) in result.card.category_names.slice(0, 4)"
                          :key="idx"
                          class="badge bg-info bg-opacity-25 text-info me-1"
                        >{{ catName }}</span>
                      </div>
                      <!-- 추천 이유 -->
                      <div v-if="result.reasons && result.reasons.length" class="d-flex flex-wrap gap-1">
                        <span
                          v-for="(reason, ri) in result.reasons.slice(0, 3)"
                          :key="ri"
                          class="badge bg-light text-dark border"
                        >
                          {{ reason }}
                        </span>
                      </div>
                    </div>
                    <div class="col-auto text-end">
                      <div class="text-muted small">매칭 점수</div>
                      <div class="fs-4 fw-bold" :class="getScoreClass(result.score)">{{ formatScore(result.score) }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 검색 전 안내 -->
        <div v-else-if="!lastQuery" class="text-center py-5">
          <div class="text-muted">
            <i class="bi bi-credit-card" style="font-size: 4rem;"></i>
            <p class="mt-3 fs-5">위 검색창에 원하는 카드 혜택을 입력해보세요</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useCardsStore } from '@/stores/cards'
import { storeToRefs } from 'pinia'
import { useCardUtils } from '@/composables/useCardUtils'
import LoadingSpinner from '@/components/shared/LoadingSpinner.vue'
import CardImage from '@/components/shared/CardImage.vue'

const router = useRouter()
const route = useRoute()
const cardsStore = useCardsStore()
const { cards, companies, recommendedCards, isLoading, error, lastQuery, pagination } = storeToRefs(cardsStore)
const { formatScore, getRankBadgeClass, getScoreClass, getCardTypeBadgeClass } = useCardUtils()

// 탭 상태 (URL 쿼리로 유지)
const activeTab = ref(route.query.tab === 'recommend' ? 'recommend' : 'search')

// URL 쿼리 변경 감지
watch(() => route.query.tab, (newTab) => {
  activeTab.value = newTab === 'recommend' ? 'recommend' : 'search'
})

// 검색 탭 상태
const searchQuery = ref('')
const selectedCompany = ref('')
const selectedCardType = ref('')
const selectedCategory = ref('')
const categoryOptions = ref({})

// 추천 탭 상태
const recommendQuery = ref('')
const showFilters = ref(false)
const recFilters = ref({
  company: '',
  card_type: '',
  max_annual_fee: null,
  max_min_spending: null
})

const exampleQueries = ['스타벅스 할인', '주유 혜택', '온라인 쇼핑', '해외여행', '대중교통', '영화 할인']

const visiblePages = computed(() => {
  const total = pagination.value.totalPages
  const current = pagination.value.page
  const pages = []
  for (let i = Math.max(1, current - 2); i <= Math.min(total, current + 2); i++) {
    pages.push(i)
  }
  return pages
})

onMounted(async () => {
  await cardsStore.fetchCompanies()
  await fetchCategories()
  if (activeTab.value === 'search') {
    await loadCards()
  }
})

// 카테고리 목록 조회
async function fetchCategories() {
  try {
    const response = await import('@/stores/api').then(m => m.default.get('/cards/categories/'))
    categoryOptions.value = response.data
  } catch (err) {
    console.error('카테고리 목록 조회 실패:', err)
    // 기본값 설정
    categoryOptions.value = {
      'TRANS': '교통', 'COMM': '통신', 'SHOP': '쇼핑', 'COFFEE': '카페',
      'FOOD': '외식', 'GAS': '주유', 'UTIL': '공과금', 'SUB': '구독',
      'PAY': '페이', 'TRAVEL': '여행', 'MART': '마트', 'ETC': '기타'
    }
  }
}

// 검색 탭 함수들
async function loadCards() {
  const params = { page: pagination.value.page, page_size: 12 }
  if (searchQuery.value) params.q = searchQuery.value
  if (selectedCompany.value) params.company = selectedCompany.value
  if (selectedCardType.value) params.card_type = selectedCardType.value
  if (selectedCategory.value) params.category = selectedCategory.value
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
  selectedCategory.value = ''
  pagination.value.page = 1
  loadCards()
}

function goToPage(page) {
  if (page < 1 || page > pagination.value.totalPages) return
  pagination.value.page = page
  loadCards()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// 추천 탭 함수들
function setRecommendQuery(query) {
  recommendQuery.value = query
  handleRecommend()
}

async function handleRecommend() {
  if (!recommendQuery.value.trim()) return
  try {
    // 필터 객체 구성 (null/빈값 제외)
    const filters = {}
    if (recFilters.value.company) filters.company = recFilters.value.company
    if (recFilters.value.card_type) filters.card_type = recFilters.value.card_type
    if (recFilters.value.max_annual_fee !== null) filters.max_annual_fee = recFilters.value.max_annual_fee
    if (recFilters.value.max_min_spending !== null) filters.max_min_spending = recFilters.value.max_min_spending

    await cardsStore.getRecommendations(recommendQuery.value.trim(), 5, filters)
  } catch (err) {
    console.error('추천 검색 실패:', err)
  }
}

// 공통 함수
function goToDetail(cardId) {
  if (cardId) {
    router.push({ name: 'card-detail', params: { id: cardId } })
  }
}
</script>

<style scoped>
.nav-tabs .nav-link {
  color: #6c757d;
  border: none;
  border-bottom: 2px solid transparent;
  padding: 1rem 2rem;
  font-weight: 500;
}

.nav-tabs .nav-link.active {
  color: #0d6efd;
  border-bottom: 2px solid #0d6efd;
  background: transparent;
}

.nav-tabs .nav-link:hover:not(.active) {
  border-bottom: 2px solid #dee2e6;
}

.card-hover {
  transition: transform 0.2s, box-shadow 0.2s;
}

.card-hover:hover {
  transform: translateY(-3px);
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15) !important;
}
</style>
