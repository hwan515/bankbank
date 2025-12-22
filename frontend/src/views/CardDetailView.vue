<template>
  <div class="page">
    <div class="container py-4">
      <!-- 로딩 -->
      <div v-if="isLoading" class="state">
        <div class="spinner-border" style="width: 2.6rem; height: 2.6rem;"></div>
        <p class="state-sub">카드 정보를 불러오는 중...</p>
      </div>

      <!-- 에러 -->
      <div v-else-if="error" class="state">
        <div class="alert alert-danger">{{ error }}</div>
        <button class="btn-mini" @click="$router.back()">뒤로 가기</button>
      </div>

      <!-- 카드 상세 -->
      <div v-else-if="card">
        <!-- 뒤로 가기 -->
        <button class="btn-mini ghost mb-3" @click="$router.back()">← 목록으로</button>

        <div class="layout">
          <!-- 왼쪽 -->
          <div class="left">
            <!-- 이미지 -->
            <div class="box">
              <div class="box-body img-area">
                <img
                  :src="card.image_url"
                  :alt="card.name"
                  class="card-img"
                  @error="handleImageError"
                />
              </div>
            </div>

            <!-- 기본 정보 -->
            <div class="box mt">
              <div class="box-head">
                <div class="box-title">기본 정보</div>
              </div>

              <div class="kv">
                <div class="kv-row">
                  <span class="k">카드사</span>
                  <strong class="v">{{ card.company }}</strong>
                </div>
                <div class="kv-row">
                  <span class="k">카드 종류</span>
                  <strong class="v">{{ card.card_type === 'CRD' ? '신용카드' : '체크카드' }}</strong>
                </div>
                <div class="kv-row">
                  <span class="k">연회비</span>
                  <strong class="v">{{ card.annual_fee || '정보 없음' }}</strong>
                </div>
                <div class="kv-row">
                  <span class="k">전월실적</span>
                  <strong class="v">{{ formatSpending(card.min_spending) }}</strong>
                </div>
                <div v-if="card.ranking" class="kv-row">
                  <span class="k">인기 순위</span>
                  <strong class="v rank">{{ card.ranking }}위</strong>
                </div>
              </div>
            </div>
          </div>

          <!-- 오른쪽 -->
          <div class="right">
            <!-- 헤더 -->
            <div class="header">
              <div class="badges">
                <span class="badge">{{ card.company }}</span>
                <span class="badge" :class="card.card_type === 'CRD' ? 'primary' : 'success'">
                  {{ card.card_type === 'CRD' ? '신용카드' : '체크카드' }}
                </span>
                <span v-if="card.category" class="badge subtle">{{ card.category }}</span>
              </div>

              <h1 class="h1">{{ card.name }}</h1>
            </div>

            <!-- 주요 혜택 -->
            <div class="box mb">
              <div class="box-head">
                <div class="box-title">주요 혜택</div>
              </div>
              <div class="box-body">
                <p v-if="card.main_benefit" class="lead">{{ card.main_benefit }}</p>
                <p v-else class="muted">혜택 정보가 없습니다.</p>
              </div>
            </div>

            <!-- 혜택 요약 -->
            <div v-if="card.benefits_summary" class="box mb">
              <div class="box-head">
                <div class="box-title">혜택 요약</div>
              </div>
              <div class="box-body">
                <p class="pre-line">{{ formatBenefits(card.benefits_summary) }}</p>
              </div>
            </div>

            <!-- 상세 혜택 -->
            <div v-if="card.benefits_json && card.benefits_json.length" class="box mb">
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
            <div v-if="card.structured_benefit && card.structured_benefit.length" class="box">
              <div class="box-head">
                <div class="box-title">혜택 카테고리</div>
              </div>

              <div class="box-body">
                <div class="sb-grid">
                  <div v-for="(sb, index) in card.structured_benefit" :key="index" class="sb">
                    <div class="sb-top">
                      <span class="badge dark">{{ getCategoryName(sb.category) }}</span>
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
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useCardsStore } from '@/stores/cards'
import { storeToRefs } from 'pinia'

const route = useRoute()
const cardsStore = useCardsStore()
const { currentCard: card, isLoading, error } = storeToRefs(cardsStore)

const categoryMap = {
  'TRANS': '교통','COMM': '통신','SHOP': '쇼핑','COFFEE': '카페','FOOD': '외식','GAS': '주유',
  'UTIL': '공과금','SUB': '구독','PAY': '페이','MOVIE': '영화','TRAVEL': '여행','ONLINE': '온라인',
  'MART': '마트','BEAUTY': '뷰티','HEALTH': '건강','EDU': '교육','ETC': '기타'
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
  return decodeHtml(text).replace(/\s+\/\s+/g, '\n')
}

function decodeHtml(text) {
  if (!text) return ''
  const entities = {
    '&middot;': '·','&bull;': '•','&amp;': '&','&lt;': '<','&gt;': '>','&nbsp;': ' ',
    '&quot;': '"','&#39;': "'",'&apos;': "'",'&ndash;': '–','&mdash;': '—','&hellip;': '…',
    '&trade;': '™','&reg;': '®','&copy;': '©','&times;': '×','&divide;': '÷','&plusmn;': '±',
    '&rarr;': '→','&larr;': '←','&uarr;': '↑','&darr;': '↓',
  }
  return text.replace(/&[a-zA-Z0-9#]+;/g, m => entities[m] || m)
}

function getCategoryName(code) {
  return categoryMap[code] || code || '기타'
}

function handleImageError(event) {
  event.target.src = 'https://placehold.co/300x200/f8f9fa/999?text=No+Image'
}
</script>

<style scoped>
/* 배경 톤 통일 */
.page {
  background: linear-gradient(180deg, #fafafa 0%, #ffffff 100%);
  min-height: 100%;
}

/* 로딩/에러 상태 */
.state {
  text-align: center;
  padding: 48px 0;
}
.state-sub {
  margin-top: 12px;
  color: #777;
  font-size: 13px;
}

/* 미니멀 버튼 */
.btn-mini {
  height: 36px;
  padding: 0 12px;
  border-radius: 12px;
  border: 1px solid #111;
  background: #111;
  color: #fff;
  font-weight: 900;
  font-size: 13px;
  cursor: pointer;
}
.btn-mini:hover { background: #000; }
.btn-mini.ghost {
  background: #fff;
  color: #111;
  border-color: #e8e8e8;
}
.btn-mini.ghost:hover { background: #fafafa; }

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
  background: #fff;
  border: 1px solid #efefef;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 1px 2px rgba(0,0,0,0.08), 0 10px 24px rgba(0,0,0,0.06);
}
.box-head {
  padding: 14px 14px 10px;
  border-bottom: 1px solid #f0f0f0;
}
.box-title {
  font-weight: 900;
  letter-spacing: -0.2px;
  color: #111;
}
.box-body { padding: 14px; }

.mt { margin-top: 12px; }
.mb { margin-bottom: 12px; }

/* 이미지 영역 */
.img-area {
  padding: 18px;
  background: #fafafa;
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
.badge.success { background: #0f5132; border-color: #0f5132; color: #fff; }
.badge.subtle { background: #fff; }
.badge.dark { background: #111; border-color: #111; color: #fff; }

.h1 {
  margin: 0;
  font-size: 26px;
  font-weight: 950;
  letter-spacing: -0.4px;
  color: #111;
}

.lead {
  margin: 0;
  font-size: 14px;
  color: #222;
  line-height: 1.6;
}
.muted { color: #777; margin: 0; }
.pre-line { white-space: pre-line; }

/* Key-Value */
.kv { padding: 6px 14px 14px; }
.kv-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid #f2f2f2;
}
.kv-row:last-child { border-bottom: 0; }
.k { color: #777; font-size: 13px; }
.v { color: #111; font-size: 13px; font-weight: 900; }
.rank { color: #b7791f; }

/* accordion 미니멀 톤(부트스트랩 기본 유지, 컬러만 약하게) */
.accordion-button:not(.collapsed) {
  background-color: #f6f6f6;
  color: #111;
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
  border: 1px solid #efefef;
  border-radius: 14px;
  padding: 12px;
  background: #fff;
}
.sb-top {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}
.sb-name {
  font-size: 13px;
  color: #111;
  font-weight: 900;
}
.sb-rate {
  font-size: 13px;
  color: #111;
  font-weight: 900;
  margin-bottom: 6px;
}
.sb-cond {
  font-size: 12px;
  color: #777;
}
</style>
