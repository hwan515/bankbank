<template>
  <div class="page">
    <div class="container py-4">

      <!-- 헤더 -->
      <div class="head">
        <div>
          <div class="badge">Cards</div>
          <h1 class="title">카드</h1>
          <p class="sub">원하는 카드를 검색하거나 AI 추천을 받아보세요.</p>
        </div>
      </div>

      <!-- 탭 -->
      <div class="tabs">
        <button class="tab" :class="{ active: activeTab === 'search' }" @click="activeTab = 'search'">
          <i class="bi bi-search"></i> 카드 검색
        </button>
        <button class="tab" :class="{ active: activeTab === 'recommend' }" @click="activeTab = 'recommend'">
          <i class="bi bi-stars"></i> AI 추천
        </button>
      </div>

      <!-- SEARCH -->
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
                    class="input"
                    placeholder="카드명, 카드사, 혜택 검색..."
                    @keyup.enter="handleSearch"
                  />
                  <button class="btn-solid" @click="handleSearch">검색</button>
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

        <!-- 목록 -->
        <div v-else>
          <div class="topline">
            <span class="muted">총 <strong class="strong">{{ pagination.count }}</strong>개의 카드</span>
          </div>

          <div class="row g-4">
            <div v-for="card in cards" :key="card.id" class="col-md-6 col-lg-4">
              <CardListItem :card="card" @clicked="goToDetail(card.id)" />
            </div>
          </div>

          <div v-if="cards.length === 0" class="empty">
            <div class="empty-title">검색 결과가 없습니다</div>
            <div class="empty-sub">검색어나 필터를 바꿔서 다시 시도해보세요.</div>
          </div>

          <!-- 페이지네이션 -->
          <nav v-if="pagination.totalPages > 1" class="mt-4">
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

      <!-- RECOMMEND -->
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

            <div class="examples">
              <div class="examples-title">추천 질문</div>
              <div class="chips">
                <button
                  v-for="example in exampleQueries"
                  :key="example"
                  class="chip"
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
          <div class="result-head">
            <span class="badge primary">{{ recommendedCards.length }}</span>
            <span class="result-text">"{{ lastQuery }}" 검색 결과</span>
          </div>

          <div class="row g-4">
            <div v-for="(result, index) in recommendedCards" :key="result.card.gorilla_id" class="col-12">
              <CardListItem
                variant="recommend"
                :card="result.card"
                :recommendation="{ ...result, index }"
                @clicked="goToDetail(result.card.id)"
              />
            </div>
          </div>
        </div>

        <!-- 검색 전 -->
        <div v-else-if="!lastQuery" class="empty">
          <div class="empty-title">AI 추천을 받아보세요</div>
          <div class="empty-sub">위 검색창에 원하는 카드 혜택을 입력해보세요.</div>
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
import CardListItem from '@/components/cards/CardListItem.vue'
import api from '@/stores/api'

const router = useRouter()
const route = useRoute()
const cardsStore = useCardsStore()
const { cards, companies, recommendedCards, isLoading, error, lastQuery, pagination } = storeToRefs(cardsStore)
const { formatScore, getRankBadgeClass, getScoreClass, getCardTypeBadgeClass } = useCardUtils()

const activeTab = ref(route.query.tab === 'recommend' ? 'recommend' : 'search')

watch(() => route.query.tab, (newTab) => {
  activeTab.value = newTab === 'recommend' ? 'recommend' : 'search'
})

const searchQuery = ref('')
const selectedCompany = ref('')
const selectedCardType = ref('')
const selectedCategory = ref('')
const categoryOptions = ref({})

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
  for (let i = Math.max(1, current - 2); i <= Math.min(total, current + 2); i++) pages.push(i)
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
    const response = await api.get('/cards/categories/')
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
  if (cardId) router.push({ name: 'card-detail', params: { id: cardId } })
}
</script>

<style scoped>
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
.badge.primary { background: #111; border-color: #111; color: #fff; }

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
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.06), 0 8px 18px rgba(0,0,0,0.05);
}
.tab.active {
  background: #111;
  border-color: #111;
  color: #fff;
}
.tab i { font-size: 14px; }

/* 박스 */
.box {
  border: 1px solid #efefef;
  border-radius: 16px;
  background: #fff;
  box-shadow: 0 1px 2px rgba(0,0,0,0.08), 0 10px 24px rgba(0,0,0,0.06);
}
.box-body { padding: 14px; }
.mb { margin-bottom: 14px; }

.filter-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 120px;
  gap: 12px;
}
.field { display: grid; gap: 6px; }
.label { font-size: 12px; font-weight: 900; color: #111; }

.search-row {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 8px;
}
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

/* 상태 */
.state { text-align: center; padding: 48px 0; }
.state-sub { margin-top: 12px; color: #777; font-size: 13px; }
.topline { margin: 10px 0 12px; }
.muted { color: #777; font-size: 13px; }
.strong { color: #111; }

/* 카드 그리드 */
.grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}
.card {
  background: #fff;
  border: 1px solid #efefef;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: transform .15s ease, box-shadow .15s ease, border-color .15s ease;
  box-shadow: 0 1px 2px rgba(0,0,0,0.08), 0 8px 20px rgba(0,0,0,0.06);
}
.card:hover {
  transform: translateY(-2px);
  border-color: #e3e3e3;
  box-shadow: 0 2px 6px rgba(0,0,0,0.10), 0 14px 28px rgba(0,0,0,0.08);
}
.img-wrap {
  height: 160px;
  background: #fafafa;
  border-bottom: 1px solid #f0f0f0;
  display: grid;
  place-items: center;
  padding: 10px;
}
.img { max-height: 140px; max-width: 92%; object-fit: contain; }
.body { padding: 12px; display: grid; gap: 8px; }
.badges { display: flex; gap: 6px; flex-wrap: wrap; }
.b {
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
.b.primary { background: #111; border-color: #111; color: #fff; }
.b.success { background: #0f5132; border-color: #0f5132; color: #fff; }
.b.warning { background: #fff3cd; border-color: #ffe69c; color: #7a5a00; }
.name {
  font-weight: 900;
  color: #111;
  font-size: 14px;
  line-height: 1.35;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.benefit {
  font-size: 13px;
  color: #666;
  line-height: 1.45;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.fee { font-size: 12px; color: #777; text-align: right; }

.empty {
  margin-top: 14px;
  padding: 18px;
  border: 1px solid #efefef;
  border-radius: 16px;
  background: #fff;
  text-align: center;
}
.empty-title { font-weight: 900; color: #111; margin-bottom: 6px; }
.empty-sub { font-size: 13px; color: #777; }

/* 추천 */
.recommend-row {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 8px;
  align-items: center;
}
.examples { margin-top: 12px; }
.examples-title { font-size: 12px; font-weight: 900; color: #111; margin-bottom: 8px; }
.chips { display: flex; flex-wrap: wrap; gap: 8px; }
.chip {
  height: 32px;
  padding: 0 12px;
  border-radius: 999px;
  border: 1px solid #e8e8e8;
  background: #fff;
  color: #222;
  font-size: 12px;
  font-weight: 900;
  cursor: pointer;
}
.chip:hover { background: #fafafa; }

/* 추천 결과 */
.result-head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 10px 0 12px;
}
.result-text { font-weight: 900; color: #111; }

.rec-list { display: grid; gap: 10px; }
.rec-card {
  display: grid;
  grid-template-columns: 54px 140px 1fr 120px;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: 1px solid #efefef;
  border-radius: 16px;
  background: #fff;
  cursor: pointer;
  box-shadow: 0 1px 2px rgba(0,0,0,0.08), 0 10px 24px rgba(0,0,0,0.06);
  transition: transform .15s ease, box-shadow .15s ease, border-color .15s ease;
}
.rec-card:hover {
  transform: translateY(-1px);
  border-color: #e3e3e3;
  box-shadow: 0 2px 6px rgba(0,0,0,0.10), 0 14px 28px rgba(0,0,0,0.08);
}
.rank {
  width: 54px; height: 54px;
  border-radius: 999px;
  display: grid;
  place-items: center;
  font-weight: 950;
  border: 1px solid #efefef;
  background: #fafafa;
  color: #111;
}
.rank.gold { background: #fff3cd; border-color: #ffe69c; color: #7a5a00; }
.rank.silver { background: #f2f2f2; border-color: #e6e6e6; color: #444; }
.rank.bronze { background: #fbe7d5; border-color: #f5d0a9; color: #7a3e00; }

.rec-img-wrap {
  height: 76px;
  border-radius: 14px;
  background: #fafafa;
  border: 1px solid #f0f0f0;
  display: grid;
  place-items: center;
  padding: 6px;
}
.rec-img { width: 100%; height: 100%; object-fit: contain; }

.rec-body { display: grid; gap: 6px; }
.rec-name { font-weight: 950; color: #111; letter-spacing: -0.2px; }
.rec-preview {
  font-size: 13px;
  color: #666;
  line-height: 1.45;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.score { text-align: right; }
.small { font-size: 12px; }
.score-num { font-size: 22px; font-weight: 950; }
.score-num.good { color: #0f5132; }
.score-num.mid { color: #111; }
.score-num.high { color: #7a5a00; }

/* 반응형 */
@media (max-width: 992px) {
  .filter-row { grid-template-columns: 1fr 1fr; }
  .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .rec-card { grid-template-columns: 54px 140px 1fr; }
  .score { text-align: left; }
}
@media (max-width: 576px) {
  .tabs { grid-template-columns: 1fr; }
  .filter-row { grid-template-columns: 1fr; }
  .grid { grid-template-columns: 1fr; }
  .recommend-row { grid-template-columns: 1fr; }
  .btn-solid { width: 100%; }
  .rec-card { grid-template-columns: 54px 1fr; }
  .rec-img-wrap { grid-column: 1 / -1; height: 90px; }
}
</style>
