<template>
  <!-- Search Result Variant -->
  <div v-if="variant === 'search'" class="card ui-card h-100 card-hover" @click="$emit('clicked')" style="cursor: pointer;">
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
        <span class="ui-badge me-1">{{ card.company }}</span>
        <span class="ui-badge" :class="getCardTypeBadgeClass(card.card_type)">
          {{ card.card_type === 'CRD' ? '신용' : '체크' }}
        </span>
        <span v-if="card.ranking" class="ui-badge ui-badge-warning ms-1">{{ card.ranking }}위</span>
      </div>
      <h6 class="card-title mb-2">{{ card.name }}</h6>
      <p class="card-text ui-text-muted small mb-2">{{ card.main_benefit || '혜택 정보 없음' }}</p>
      <div v-if="card.category_names && card.category_names.length" class="mb-2">
        <span
          v-for="(catName, idx) in card.category_names.slice(0, 4)"
          :key="idx"
          class="ui-badge ui-badge-info me-1"
        >{{ catName }}</span>
      </div>
      <div class="text-end">
        <small class="ui-text-muted">{{ card.annual_fee || '연회비 정보 없음' }}</small>
      </div>
    </div>
  </div>

  <!-- Recommendation Result Variant -->
  <div v-else-if="variant === 'recommend'" class="card ui-card h-100 card-hover" @click="$emit('clicked')" style="cursor: pointer;">
    <div class="card-body">
      <div class="row g-3 align-items-center">
        <div class="col-12 col-sm-auto text-center">
          <div class="rounded-circle d-flex align-items-center justify-content-center" :class="getRankBadgeClass(recommendation.index)" style="width: 50px; height: 50px;">
            <span class="fw-bold fs-5">{{ recommendation.index + 1 }}</span>
          </div>
        </div>
        <div class="col-12 col-sm-auto text-center">
          <CardImage
            :src="card.image_url"
            :alt="card.name"
            img-class="rounded"
            img-style="width: 120px; height: 76px; max-width: 100%; object-fit: contain; background: #f8f9fa;"
            placeholder-size="120x76"
          />
        </div>
        <div class="col-12 col-md">
          <div class="d-flex align-items-center mb-1">
            <span class="ui-badge me-2">{{ card.company }}</span>
            <span v-if="card.ranking" class="ui-badge ui-badge-warning">인기 {{ card.ranking }}위</span>
          </div>
          <h5 class="card-title mb-1">{{ card.name }}</h5>
          <p class="ui-text-muted mb-2 small">{{ recommendation.preview }}</p>
          <div v-if="card.category_names && card.category_names.length" class="mb-2">
            <span
              v-for="(catName, idx) in card.category_names.slice(0, 4)"
              :key="idx"
              class="ui-badge ui-badge-info me-1"
            >{{ catName }}</span>
          </div>
          <div v-if="recommendation.reasons && recommendation.reasons.length" class="d-flex flex-wrap gap-1">
            <span
              v-for="(reason, ri) in recommendation.reasons.slice(0, 3)"
              :key="ri"
              class="ui-badge"
            >
              {{ reason }}
            </span>
          </div>
        </div>
        <div class="col-12 col-md-auto text-md-end">
          <div class="ui-text-muted small">매칭 점수</div>
          <div class="fs-4 fw-bold" :class="getScoreClass(recommendation.score)">{{ formatScore(recommendation.score) }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import CardImage from '@/components/shared/CardImage.vue'
import { useCardUtils } from '@/composables/useCardUtils'

defineProps({
  variant: {
    type: String,
    default: 'search' // 'search' or 'recommend'
  },
  card: {
    type: Object,
    required: true
  },
  recommendation: {
    type: Object,
    default: () => ({})
  }
})

defineEmits(['clicked'])

const { getCardTypeBadgeClass, getRankBadgeClass, getScoreClass, formatScore } = useCardUtils()
</script>

<style scoped>
.card-hover {
  transition: transform .15s ease, box-shadow .15s ease, border-color .15s ease;
}
.card-hover:hover {
  transform: translateY(-2px);
  border-color: rgba(27, 95, 122, 0.3);
  box-shadow: var(--shadow-2);
}
.small { font-size: 12px; }
</style>
