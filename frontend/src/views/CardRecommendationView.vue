<template>
  <div class="container py-5">
    <!-- 헤더 -->
    <div class="text-center mb-5">
      <h1 class="display-5 fw-bold">AI 카드 추천</h1>
      <p class="text-muted">원하는 혜택을 입력하면 맞춤 카드를 추천해드립니다</p>
    </div>

    <!-- 검색 영역 -->
    <div class="row justify-content-center mb-5">
      <div class="col-lg-8">
        <div class="card shadow-sm">
          <div class="card-body p-4">
            <form @submit.prevent="handleSearch">
              <div class="input-group input-group-lg">
                <input
                  v-model="searchQuery"
                  type="text"
                  class="form-control"
                  placeholder="예: 스타벅스 할인 많은 카드, 주유 혜택 좋은 카드"
                  :disabled="isLoading"
                />
                <button
                  type="submit"
                  class="btn btn-primary px-4"
                  :disabled="isLoading || !searchQuery.trim()"
                >
                  <span v-if="isLoading" class="spinner-border spinner-border-sm me-2"></span>
                  {{ isLoading ? '검색 중...' : '추천받기' }}
                </button>
              </div>
            </form>

            <!-- 예시 질문 -->
            <div class="mt-3">
              <small class="text-muted">추천 질문:</small>
              <div class="d-flex flex-wrap gap-2 mt-2">
                <button
                  v-for="example in exampleQueries"
                  :key="example"
                  class="btn btn-outline-secondary btn-sm"
                  @click="setQuery(example)"
                  :disabled="isLoading"
                >
                  {{ example }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 에러 메시지 -->
    <div v-if="error" class="row justify-content-center mb-4">
      <div class="col-lg-8">
        <div class="alert alert-danger d-flex align-items-center" role="alert">
          <i class="bi bi-exclamation-triangle-fill me-2"></i>
          {{ error }}
        </div>
      </div>
    </div>

    <!-- 로딩 -->
    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;"></div>
      <p class="mt-3 text-muted">AI가 최적의 카드를 찾고 있습니다...</p>
    </div>

    <!-- 검색 결과 -->
    <div v-else-if="recommendedCards.length > 0">
      <h4 class="mb-4">
        <span class="badge bg-primary me-2">{{ recommendedCards.length }}</span>
        "{{ lastQuery }}" 검색 결과
      </h4>

      <div class="row g-4">
        <div
          v-for="(result, index) in recommendedCards"
          :key="result.card.gorilla_id"
          class="col-12"
        >
          <div
            class="card shadow-sm h-100 card-clickable"
            @click="goToDetail(result.card)"
            style="cursor: pointer;"
          >
            <div class="card-body">
              <div class="row align-items-center">
                <!-- 순위 -->
                <div class="col-auto">
                  <div
                    class="rounded-circle d-flex align-items-center justify-content-center"
                    :class="getRankBadgeClass(index)"
                    style="width: 50px; height: 50px;"
                  >
                    <span class="fw-bold fs-5">{{ index + 1 }}</span>
                  </div>
                </div>

                <!-- 카드 이미지 -->
                <div class="col-auto">
                  <img
                    :src="result.card.image_url"
                    :alt="result.card.name"
                    class="rounded"
                    style="width: 120px; height: 76px; object-fit: contain; background: #f8f9fa;"
                    @error="handleImageError"
                  />
                </div>

                <!-- 카드 정보 -->
                <div class="col">
                  <div class="d-flex align-items-center mb-1">
                    <span class="badge bg-secondary me-2">{{ result.card.company }}</span>
                    <span v-if="result.card.ranking" class="badge bg-warning text-dark">
                      인기 {{ result.card.ranking }}위
                    </span>
                  </div>
                  <h5 class="card-title mb-1">{{ result.card.name }}</h5>
                  <p class="text-muted mb-0 small">{{ result.preview }}</p>
                </div>

                <!-- 매칭 점수 -->
                <div class="col-auto text-end">
                  <div class="text-muted small">매칭 점수</div>
                  <div class="fs-4 fw-bold" :class="getScoreClass(result.score)">
                    {{ formatScore(result.score) }}
                  </div>
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

    <!-- 결과 없음 -->
    <div v-else class="text-center py-5">
      <div class="text-muted">
        <i class="bi bi-search" style="font-size: 4rem;"></i>
        <p class="mt-3 fs-5">검색 결과가 없습니다</p>
        <p>다른 키워드로 검색해보세요</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useCardsStore } from '@/stores/cards'
import { storeToRefs } from 'pinia'

const router = useRouter()
const cardsStore = useCardsStore()
const { recommendedCards, isLoading, error, lastQuery } = storeToRefs(cardsStore)

const searchQuery = ref('')

const exampleQueries = [
  '스타벅스 할인',
  '주유 혜택',
  '온라인 쇼핑',
  '해외여행',
  '대중교통',
  '영화 할인'
]

function setQuery(query) {
  searchQuery.value = query
  handleSearch()
}

async function handleSearch() {
  if (!searchQuery.value.trim()) return

  try {
    await cardsStore.getRecommendations(searchQuery.value.trim(), 5)
  } catch (err) {
    console.error('추천 검색 실패:', err)
  }
}

function getRankBadgeClass(index) {
  if (index === 0) return 'bg-warning text-dark'
  if (index === 1) return 'bg-secondary text-white'
  if (index === 2) return 'bg-danger text-white'
  return 'bg-light text-dark'
}

function getScoreClass(score) {
  // Chroma 거리 점수: 낮을수록 좋음 (0에 가까울수록 유사)
  if (score < 0.5) return 'text-success'
  if (score < 1.0) return 'text-primary'
  return 'text-warning'
}

function formatScore(score) {
  // 거리를 유사도(%)로 변환 (대략적인 변환)
  const similarity = Math.max(0, Math.min(100, (1 - score / 2) * 100))
  return similarity.toFixed(0) + '%'
}

function handleImageError(event) {
  event.target.src = 'https://placehold.co/120x76/f8f9fa/999?text=No+Image'
}

function goToDetail(card) {
  if (card.id) {
    router.push({ name: 'card-detail', params: { id: card.id } })
  }
}
</script>

<style scoped>
.card {
  transition: transform 0.2s, box-shadow 0.2s;
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15) !important;
}

.btn-outline-secondary:hover {
  background-color: #6c757d;
  color: white;
}
</style>
