<template>
  <div class="container py-5">
    <!-- 로딩 -->
    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;"></div>
      <p class="mt-3 text-muted">카드 정보를 불러오는 중...</p>
    </div>

    <!-- 에러 -->
    <div v-else-if="error" class="text-center py-5">
      <div class="alert alert-danger">{{ error }}</div>
      <button class="btn btn-primary" @click="$router.back()">뒤로 가기</button>
    </div>

    <!-- 카드 상세 -->
    <div v-else-if="card">
      <!-- 뒤로 가기 -->
      <button class="btn btn-outline-secondary mb-4" @click="$router.back()">
        &larr; 목록으로
      </button>

      <div class="row g-5">
        <!-- 왼쪽: 카드 이미지 -->
        <div class="col-lg-5">
          <div class="card shadow">
            <div class="card-body text-center p-5 bg-light">
              <img
                :src="card.image_url"
                :alt="card.name"
                class="img-fluid"
                style="max-height: 300px; object-fit: contain;"
                @error="handleImageError"
              />
            </div>
          </div>

          <!-- 기본 정보 카드 -->
          <div class="card shadow mt-4">
            <div class="card-header bg-white">
              <h5 class="mb-0">기본 정보</h5>
            </div>
            <ul class="list-group list-group-flush">
              <li class="list-group-item d-flex justify-content-between">
                <span class="text-muted">카드사</span>
                <strong>{{ card.company }}</strong>
              </li>
              <li class="list-group-item d-flex justify-content-between">
                <span class="text-muted">카드 종류</span>
                <strong>{{ card.card_type === 'CRD' ? '신용카드' : '체크카드' }}</strong>
              </li>
              <li class="list-group-item d-flex justify-content-between">
                <span class="text-muted">연회비</span>
                <strong>{{ card.annual_fee || '정보 없음' }}</strong>
              </li>
              <li class="list-group-item d-flex justify-content-between">
                <span class="text-muted">전월실적</span>
                <strong>{{ formatSpending(card.min_spending) }}</strong>
              </li>
              <li v-if="card.ranking" class="list-group-item d-flex justify-content-between">
                <span class="text-muted">인기 순위</span>
                <strong class="text-warning">{{ card.ranking }}위</strong>
              </li>
            </ul>
          </div>
        </div>

        <!-- 오른쪽: 카드 정보 -->
        <div class="col-lg-7">
          <!-- 카드명 -->
          <div class="mb-4">
            <div class="d-flex align-items-center gap-2 mb-2">
              <span class="badge bg-secondary">{{ card.company }}</span>
              <span class="badge" :class="card.card_type === 'CRD' ? 'bg-primary' : 'bg-success'">
                {{ card.card_type === 'CRD' ? '신용카드' : '체크카드' }}
              </span>
              <span v-if="card.category" class="badge bg-info">{{ card.category }}</span>
            </div>
            <h1 class="display-6 fw-bold">{{ card.name }}</h1>
          </div>

          <!-- 주요 혜택 -->
          <div class="card shadow mb-4">
            <div class="card-header bg-primary text-white">
              <h5 class="mb-0">주요 혜택</h5>
            </div>
            <div class="card-body">
              <p v-if="card.main_benefit" class="lead mb-0">{{ card.main_benefit }}</p>
              <p v-else class="text-muted mb-0">혜택 정보가 없습니다.</p>
            </div>
          </div>

          <!-- 혜택 요약 -->
          <div v-if="card.benefits_summary" class="card shadow mb-4">
            <div class="card-header bg-white">
              <h5 class="mb-0">혜택 요약</h5>
            </div>
            <div class="card-body">
              <p class="mb-0 pre-line">{{ formatBenefits(card.benefits_summary) }}</p>
            </div>
          </div>

          <!-- 상세 혜택 (benefits_json) -->
          <div v-if="card.benefits_json && card.benefits_json.length > 0" class="card shadow mb-4">
            <div class="card-header bg-white">
              <h5 class="mb-0">상세 혜택</h5>
            </div>
            <div class="card-body">
              <div class="accordion" id="benefitsAccordion">
                <div
                  v-for="(benefit, index) in card.benefits_json"
                  :key="index"
                  class="accordion-item"
                >
                  <h2 class="accordion-header">
                    <button
                      class="accordion-button"
                      :class="{ collapsed: index !== 0 }"
                      type="button"
                      :data-bs-toggle="'collapse'"
                      :data-bs-target="'#benefit' + index"
                    >
                      {{ benefit.title || benefit.category || `혜택 ${index + 1}` }}
                    </button>
                  </h2>
                  <div
                    :id="'benefit' + index"
                    class="accordion-collapse collapse"
                    :class="{ show: index === 0 }"
                  >
                    <div class="accordion-body pre-line">
                      <p v-if="benefit.summary">{{ decodeHtml(benefit.summary) }}</p>
                      <p v-if="benefit.detail" class="text-muted small">{{ decodeHtml(benefit.detail) }}</p>
                      <ul v-if="benefit.items && benefit.items.length" class="mb-0">
                        <li v-for="(item, i) in benefit.items" :key="i">{{ decodeHtml(item) }}</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 구조화된 혜택 -->
          <div v-if="card.structured_benefit && card.structured_benefit.length > 0" class="card shadow">
            <div class="card-header bg-white">
              <h5 class="mb-0">혜택 카테고리</h5>
            </div>
            <div class="card-body">
              <div class="row g-3">
                <div
                  v-for="(sb, index) in card.structured_benefit"
                  :key="index"
                  class="col-md-6"
                >
                  <div class="border rounded p-3 h-100 pre-line">
                    <div class="d-flex align-items-center mb-2">
                      <span class="badge bg-dark me-2">{{ getCategoryName(sb.category) }}</span>
                      <strong>{{ sb.brand || sb.name || '' }}</strong>
                    </div>
                    <p class="mb-1 text-primary fw-bold">{{ sb.rate || sb.benefit || '' }}</p>
                    <small v-if="sb.condition" class="text-muted">{{ sb.condition }}</small>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useCardsStore } from '@/stores/cards'
import { storeToRefs } from 'pinia'

const route = useRoute()
const cardsStore = useCardsStore()
const { currentCard: card, isLoading, error } = storeToRefs(cardsStore)

const categoryMap = {
  'TRANS': '교통',
  'COMM': '통신',
  'SHOP': '쇼핑',
  'COFFEE': '카페',
  'FOOD': '외식',
  'GAS': '주유',
  'UTIL': '공과금',
  'SUB': '구독',
  'PAY': '페이',
  'MOVIE': '영화',
  'TRAVEL': '여행',
  'ONLINE': '온라인',
  'MART': '마트',
  'BEAUTY': '뷰티',
  'HEALTH': '건강',
  'EDU': '교육',
  'ETC': '기타'
}

onMounted(async () => {
  const cardId = route.params.id
  await cardsStore.fetchCardDetail(cardId)
})

onUnmounted(() => {
  cardsStore.clearCurrentCard()
})

function formatSpending(amount) {
  if (!amount || amount === 0) return '조건 없음'
  return `${(amount / 10000).toLocaleString()}만원 이상`
}

function formatBenefits(text) {
  if (!text) return ''
  // 앞뒤에 공백이 있는 " / "만 줄바꿈으로 변환
  return decodeHtml(text).replace(/\s+\/\s+/g, '\n')
}

function decodeHtml(text) {
  if (!text) return ''
  const entities = {
    '&middot;': '·',
    '&bull;': '•',
    '&amp;': '&',
    '&lt;': '<',
    '&gt;': '>',
    '&nbsp;': ' ',
    '&quot;': '"',
    '&#39;': "'",
    '&apos;': "'",
    '&ndash;': '–',
    '&mdash;': '—',
    '&hellip;': '…',
    '&trade;': '™',
    '&reg;': '®',
    '&copy;': '©',
    '&times;': '×',
    '&divide;': '÷',
    '&plusmn;': '±',
    '&rarr;': '→',
    '&larr;': '←',
    '&uarr;': '↑',
    '&darr;': '↓',
  }
  return text.replace(/&[a-zA-Z0-9#]+;/g, match => entities[match] || match)
}

function getCategoryName(code) {
  return categoryMap[code] || code || '기타'
}

function handleImageError(event) {
  event.target.src = 'https://placehold.co/300x200/f8f9fa/999?text=No+Image'
}
</script>

<style scoped>
.accordion-button:not(.collapsed) {
  background-color: #e7f1ff;
  color: #0c63e4;
}

.pre-line {
  white-space: pre-line;
}
</style>
