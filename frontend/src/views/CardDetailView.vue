<template>
  <div class="container py-5">
    <!-- 로딩 -->
    <LoadingSpinner v-if="isLoading" message="카드 정보를 불러오는 중..." />

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
              <CardImage
                :src="card.image_url"
                :alt="card.name"
                img-style="max-height: 300px; object-fit: contain;"
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
                <strong>{{ getCardTypeLabel(card.card_type) }}</strong>
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
              <span class="badge" :class="getCardTypeBadgeClass(card.card_type)">
                {{ getCardTypeLabel(card.card_type) }}
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
import { onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useCardsStore } from '@/stores/cards'
import { storeToRefs } from 'pinia'
import { useCardUtils } from '@/composables/useCardUtils'
import LoadingSpinner from '@/components/shared/LoadingSpinner.vue'
import CardImage from '@/components/shared/CardImage.vue'

const route = useRoute()
const cardsStore = useCardsStore()
const { currentCard: card, isLoading, error } = storeToRefs(cardsStore)
const {
  decodeHtml,
  formatBenefits,
  formatSpending,
  getCardTypeLabel,
  getCardTypeBadgeClass,
  getCategoryName
} = useCardUtils()

onMounted(async () => {
  const cardId = route.params.id
  await cardsStore.fetchCardDetail(cardId)
})

onUnmounted(() => {
  cardsStore.clearCurrentCard()
})
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
