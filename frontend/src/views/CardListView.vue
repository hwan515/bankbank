<template>
  <div class="page">
    <div class="container py-4">

      <!-- 헤더 -->
      <div class="head">
        <div>
          <div class="badge">Cards</div>
          <h1 class="title">카드 검색</h1>
          <p class="sub">원하는 카드를 검색하고 비교해보세요.</p>
        </div>

        <div class="count" v-if="!isLoading && !error">
          총 <strong>{{ pagination.count }}</strong>개
        </div>
      </div>

      <!-- 검색/필터 -->
      <div class="filters">
        <div class="row">
          <!-- 검색어 -->
          <div class="field span-2">
            <label class="label">검색</label>
            <div class="search-row">
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

          <!-- 카드사 -->
          <div class="field">
            <label class="label">카드사</label>
            <select v-model="selectedCompany" class="select" @change="handleSearch">
              <option value="">전체 카드사</option>
              <option v-for="company in companies" :key="company" :value="company">
                {{ company }}
              </option>
            </select>
          </div>

          <!-- 타입 -->
          <div class="field">
            <label class="label">카드 타입</label>
            <select v-model="selectedCardType" class="select" @change="handleSearch">
              <option value="">전체 카드</option>
              <option value="credit">신용카드</option>
              <option value="check">체크카드</option>
            </select>
          </div>

          <!-- 초기화 -->
          <div class="field">
            <label class="label">&nbsp;</label>
            <button class="btn-ghost w100" @click="resetFilters" title="필터 초기화">
              초기화
            </button>
          </div>
        </div>
      </div>

      <!-- 로딩 -->
      <div v-if="isLoading" class="state">
        <div class="spinner-border" style="width: 2.6rem; height: 2.6rem;"></div>
        <p class="state-sub">카드를 불러오는 중...</p>
      </div>

      <!-- 에러 -->
      <div v-else-if="error" class="state">
        <div class="alert alert-danger">{{ error }}</div>
      </div>

      <!-- 목록 -->
      <div v-else>
        <div class="grid">
          <div
            v-for="card in cards"
            :key="card.id"
            class="card"
            @click="goToDetail(card.id)"
          >
            <!-- 이미지 -->
            <div class="img-wrap">
              <img
                :src="card.image_url"
                :alt="card.name"
                class="img"
                @error="handleImageError"
              />
            </div>

            <div class="body">
              <div class="badges">
                <span class="b">{{ card.company }}</span>
                <span class="b" :class="card.card_type === 'credit' ? 'primary' : 'success'">
                  {{ card.card_type === 'credit' ? '신용' : '체크' }}
                </span>
                <span v-if="card.ranking" class="b warning">
                  {{ card.ranking }}위
                </span>
              </div>

              <div class="name" :title="card.name">{{ card.name }}</div>

              <div class="benefit">
                {{ card.main_benefit || '혜택 정보 없음' }}
              </div>

              <div class="fee">
                {{ card.annual_fee || '연회비 정보 없음' }}
              </div>
            </div>
          </div>
        </div>

        <!-- 결과 없음 -->
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
    page_size: 12,
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
/* 전체 배경 */
.page {
  min-height: 100%;
  background: linear-gradient(180deg, #fafafa 0%, #ffffff 100%);
}

/* 헤더 */
.head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}

.badge {
  display: inline-block;
  font-size: 12px;
  color: #444;
  background: #f6f6f6;
  border: 1px solid #ededed;
  padding: 6px 10px;
  border-radius: 999px;
}

.title {
  margin: 10px 0 6px;
  font-size: 26px;
  font-weight: 950;
  letter-spacing: -0.4px;
  color: #111;
}

.sub {
  margin: 0;
  font-size: 13px;
  color: #777;
}

.count {
  font-size: 13px;
  color: #777;
}
.count strong {
  color: #111;
}

/* 필터 박스 */
.filters {
  border: 1px solid #efefef;
  border-radius: 16px;
  background: #fff;
  padding: 14px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.08), 0 10px 24px rgba(0,0,0,0.06);
  margin-bottom: 14px;
}

.row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 120px;
  gap: 12px;
}

.field { display: grid; gap: 6px; }
.label {
  font-size: 12px;
  font-weight: 900;
  color: #111;
}

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
.state {
  text-align: center;
  padding: 48px 0;
}
.state-sub {
  margin-top: 12px;
  color: #777;
  font-size: 13px;
}

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
  transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
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

.img {
  max-height: 140px;
  max-width: 92%;
  object-fit: contain;
}

.body {
  padding: 12px;
  display: grid;
  gap: 8px;
}

.badges {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

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

.fee {
  font-size: 12px;
  color: #777;
  text-align: right;
}

/* empty */
.empty {
  margin-top: 14px;
  padding: 18px;
  border: 1px solid #efefef;
  border-radius: 16px;
  background: #fff;
  text-align: center;
}
.empty-title {
  font-weight: 900;
  color: #111;
  margin-bottom: 6px;
}
.empty-sub {
  font-size: 13px;
  color: #777;
}

/* 반응형 */
@media (max-width: 992px) {
  .row { grid-template-columns: 1fr 1fr; }
  .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

@media (max-width: 576px) {
  .head { flex-direction: column; align-items: flex-start; }
  .row { grid-template-columns: 1fr; }
  .grid { grid-template-columns: 1fr; }
}
</style>
