<template>
  <!-- Search Result Variant -->
  <div v-if="variant === 'search'" class="card h-100 shadow-sm card-hover" @click="$emit('clicked')" style="cursor: pointer;">
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

  <!-- Recommendation Result Variant -->
  <div v-else-if="variant === 'recommend'" class="card shadow-sm h-100 card-hover" @click="$emit('clicked')" style="cursor: pointer;">
    <div class="card-body">
      <div class="row align-items-center">
        <div class="col-auto">
          <div class="rounded-circle d-flex align-items-center justify-content-center" :class="getRankBadgeClass(recommendation.index)" style="width: 50px; height: 50px;">
            <span class="fw-bold fs-5">{{ recommendation.index + 1 }}</span>
          </div>
        </div>
        <div class="col-auto">
          <CardImage
            :src="card.image_url"
            :alt="card.name"
            img-class="rounded"
            img-style="width: 120px; height: 76px; object-fit: contain; background: #f8f9fa;"
            placeholder-size="120x76"
          />
        </div>
        <div class="col">
          <div class="d-flex align-items-center mb-1">
            <span class="badge bg-secondary me-2">{{ card.company }}</span>
            <span v-if="card.ranking" class="badge bg-warning text-dark">인기 {{ card.ranking }}위</span>
          </div>
          <h5 class="card-title mb-1">{{ card.name }}</h5>
          <p class="text-muted mb-2 small">{{ recommendation.preview }}</p>
          <div v-if="card.category_names && card.category_names.length" class="mb-2">
            <span
              v-for="(catName, idx) in card.category_names.slice(0, 4)"
              :key="idx"
              class="badge bg-info bg-opacity-25 text-info me-1"
            >{{ catName }}</span>
          </div>
          <div v-if="recommendation.reasons && recommendation.reasons.length" class="d-flex flex-wrap gap-1">
            <span
              v-for="(reason, ri) in recommendation.reasons.slice(0, 3)"
              :key="ri"
              class="badge bg-light text-dark border"
            >
              {{ reason }}
            </span>
          </div>
        </div>
        <div class="col-auto text-end">
          <div class="text-muted small">매칭 점수</div>
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
  border-color: #e3e3e3;
  box-shadow: 0 2px 6px rgba(0,0,0,0.10), 0 14px 28px rgba(0,0,0,0.08);
}
.small { font-size: 12px; }
</style>
