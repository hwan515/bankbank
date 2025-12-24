<template>
  <div class="page">
    <div class="container py-5">
    <!-- 로딩 -->
    <LoadingSpinner v-if="isLoading" message="카드 정보를 불러오는 중..." />

      <!-- 에러 -->
      <div v-else-if="error" class="state">
        <div class="alert alert-danger">{{ error }}</div>
        <button class="ui-btn ui-btn-primary" @click="$router.back()">뒤로 가기</button>
      </div>

      <!-- 카드 상세 -->
      <div v-else-if="card">
        <!-- 뒤로 가기 -->
        <button class="ui-btn ui-btn-ghost mb-3" @click="$router.back()">← 목록으로</button>

      <div class="row g-5">
        <!-- 왼쪽: 카드 이미지 -->
        <div class="col-lg-5">
          <div class="card ui-card">
            <div class="card-body text-center p-5 ui-card-soft">
              <CardImage
                :src="card.image_url"
                :alt="card.name"
                img-style="max-height: 300px; object-fit: contain;"
              />
            </div>
          </div>

          <!-- 기본 정보 카드 -->
          <div class="card ui-card mt-4">
            <div class="card-header">
              <h5 class="mb-0">기본 정보</h5>
            </div>
            <ul class="list-group list-group-flush">
              <li class="list-group-item d-flex justify-content-between">
                <span class="ui-sub">카드사</span>
                <strong>{{ card.company }}</strong>
              </li>
              <li class="list-group-item d-flex justify-content-between">
                <span class="ui-sub">카드 종류</span>
                <strong>{{ getCardTypeLabel(card.card_type) }}</strong>
              </li>
              <li class="list-group-item d-flex justify-content-between">
                <span class="ui-sub">연회비</span>
                <strong>{{ card.annual_fee || '정보 없음' }}</strong>
              </li>
              <li class="list-group-item d-flex justify-content-between">
                <span class="ui-sub">전월실적</span>
                <strong>{{ formatSpending(card.min_spending) }}</strong>
              </li>
              <li v-if="card.ranking" class="list-group-item d-flex justify-content-between">
                <span class="ui-sub">인기 순위</span>
                <strong class="ui-badge ui-badge-warning">{{ card.ranking }}위</strong>
              </li>
            </ul>
          </div>
        </div>

        <!-- 오른쪽: 카드 정보 -->
        <div class="col-lg-7">
          <!-- 카드명 -->
          <div class="mb-4">
            <div class="d-flex align-items-center gap-2 mb-2">
              <span class="ui-badge">{{ card.company }}</span>
              <span class="ui-badge" :class="getCardTypeBadgeClass(card.card_type)">
                {{ getCardTypeLabel(card.card_type) }}
              </span>
              <span v-if="card.category" class="ui-badge ui-badge-info">{{ card.category }}</span>

              <!-- 좋아요 버튼 -->
              <button
                class="btn-like ui-btn"
                :class="card.is_liked ? 'liked' : 'ui-btn-ghost'"
                @click="handleLikeToggle"
                :disabled="likeLoading"
              >
                <i class="bi" :class="card.is_liked ? 'bi-heart-fill' : 'bi-heart'"></i>
                <span>{{ card.like_count || 0 }}</span>
              </button>
            </div>

            <!-- 주요 혜택 -->
            <div class="box ui-card mb">
              <div class="box-head">
                <div class="box-title">주요 혜택</div>
              </div>
              <div class="box-body">
                <p v-if="card.main_benefit" class="lead">{{ card.main_benefit }}</p>
                <p v-else class="muted">혜택 정보가 없습니다.</p>
              </div>
            </div>

            <!-- 혜택 요약 -->
            <div v-if="card.benefits_summary" class="box ui-card mb">
              <div class="box-head">
                <div class="box-title">혜택 요약</div>
              </div>
              <div class="box-body">
                <p class="pre-line">{{ formatBenefits(card.benefits_summary) }}</p>
              </div>
            </div>

            <!-- 상세 혜택 -->
            <div v-if="card.benefits_json && card.benefits_json.length" class="box ui-card mb">
              <div class="box-head">
                <div class="box-title">상세 혜택</div>
              </div>

              <div class="box-body">
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
                        <p v-if="benefit.detail" class="muted small">{{ decodeHtml(benefit.detail) }}</p>
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
            <div v-if="card.structured_benefit && card.structured_benefit.length" class="box ui-card">
              <div class="box-head">
                <div class="box-title">혜택 카테고리</div>
              </div>

              <div class="box-body">
                <div class="sb-grid">
                  <div v-for="(sb, index) in card.structured_benefit" :key="index" class="sb">
                    <div class="sb-top">
                      <span class="ui-badge ui-badge-primary">{{ getCategoryName(sb.category) }}</span>
                      <strong class="sb-name">{{ sb.brand || sb.name || '' }}</strong>
                    </div>
                    <div class="sb-rate">{{ sb.rate || sb.benefit || '' }}</div>
                    <div v-if="sb.condition" class="sb-cond">{{ sb.condition }}</div>
                  </div>
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
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useCardsStore } from '@/stores/cards'
import { useAccountStore } from '@/stores/account'
import { storeToRefs } from 'pinia'
import { useCardUtils } from '@/composables/useCardUtils'
import LoadingSpinner from '@/components/shared/LoadingSpinner.vue'
import CardImage from '@/components/shared/CardImage.vue'

const route = useRoute()
const cardsStore = useCardsStore()
const accountStore = useAccountStore()
const { currentCard: card, isLoading, error } = storeToRefs(cardsStore)
const { isLogin } = storeToRefs(accountStore)
const {
  decodeHtml,
  formatBenefits,
  formatSpending,
  getCardTypeLabel,
  getCardTypeBadgeClass,
  getCategoryName
} = useCardUtils()

const likeLoading = ref(false)

onMounted(async () => {
  const cardId = route.params.id
  await cardsStore.fetchCardDetail(cardId)

  // VIEW 이벤트 기록
  cardsStore.recordEvent(cardId, 'VIEW', { source: 'detail_page' })
})

onUnmounted(() => {
  cardsStore.clearCurrentCard()
})

// 좋아요 토글
async function handleLikeToggle() {
  if (!isLogin.value) {
    alert('로그인이 필요합니다.')
    return
  }
  if (likeLoading.value) return

  likeLoading.value = true
  try {
    await cardsStore.toggleLike(card.value.id)
  } finally {
    likeLoading.value = false
  }
}
</script>

<style scoped>
/* 배경 톤 통일 */
.page {
  background:
    radial-gradient(900px 300px at 10% 0%, rgba(27, 95, 122, 0.10), transparent 60%),
    linear-gradient(180deg, var(--bg-alt) 0%, var(--bg) 100%);
  min-height: 100%;
}

/* 로딩/에러 상태 */
.state {
  text-align: center;
  padding: 48px 0;
}
.state-sub {
  margin-top: 12px;
  color: var(--muted);
  font-size: 13px;
}

/* 미니멀 버튼 */
/* 좋아요 버튼 */
.btn-like {
  gap: 6px;
  font-size: 13px;
  transition: all 0.15s ease;
}
.btn-like:hover {
  border-color: #dc3545;
  color: #dc3545;
}
.btn-like.liked {
  background: #dc3545;
  border-color: #dc3545;
  color: #fff;
}
.btn-like:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 레이아웃 */
.layout {
  display: grid;
  grid-template-columns: 420px 1fr;
  gap: 14px;
}

@media (max-width: 992px) {
  .layout { grid-template-columns: 1fr; }
}

/* 공통 박스(카드) */
.box {
  border-radius: 16px;
  overflow: hidden;
}
.box-head {
  padding: 14px 14px 10px;
  border-bottom: 1px solid var(--border);
}
.box-title {
  font-weight: 700;
  letter-spacing: -0.2px;
  color: var(--ink);
}
.box-body { padding: 14px; }

.mt { margin-top: 12px; }
.mb { margin-bottom: 12px; }

/* 이미지 영역 */
.img-area {
  padding: 18px;
  background: var(--bg-alt);
  display: grid;
  place-items: center;
}
.card-img {
  max-height: 280px;
  width: 100%;
  object-fit: contain;
}

/* 헤더 */
.header { margin-bottom: 12px; }
.badges { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 8px; }

.h1 {
  margin: 0;
  font-size: 26px;
  font-weight: 700;
  letter-spacing: -0.4px;
  color: var(--ink);
}

.lead {
  margin: 0;
  font-size: 14px;
  color: var(--ink-soft);
  line-height: 1.6;
}
.muted { color: var(--muted); margin: 0; }
.pre-line { white-space: pre-line; }

/* Key-Value */
.kv { padding: 6px 14px 14px; }
.kv-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid var(--border);
}
.kv-row:last-child { border-bottom: 0; }
.k { color: var(--muted); font-size: 13px; }
.v { color: var(--ink); font-size: 13px; font-weight: 700; }
.rank { color: #b7791f; }

/* accordion 미니멀 톤(부트스트랩 기본 유지, 컬러만 약하게) */
.accordion-button:not(.collapsed) {
  background-color: var(--bg-alt);
  color: var(--ink);
}

/* structured benefit grid */
.sb-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}
@media (max-width: 576px) {
  .sb-grid { grid-template-columns: 1fr; }
}
.sb {
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 12px;
  background: var(--surface);
}
.sb-top {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}
.sb-name {
  font-size: 13px;
  color: var(--ink);
  font-weight: 700;
}
.sb-rate {
  font-size: 13px;
  color: var(--ink);
  font-weight: 700;
  margin-bottom: 6px;
}
.sb-cond {
  font-size: 12px;
  color: var(--muted);
}
</style>
