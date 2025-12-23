<template>
  <div class="card-section">
    <div class="section-header">
      <h5 class="section-title">내 카드</h5>
    </div>

    <!-- 탭 -->
    <div class="tabs">
      <button
        class="tab"
        :class="{ active: activeTab === 'liked' }"
        @click="activeTab = 'liked'"
      >
        <i class="bi bi-heart-fill"></i>
        좋아요
      </button>
      <button
        class="tab"
        :class="{ active: activeTab === 'recent' }"
        @click="activeTab = 'recent'"
      >
        <i class="bi bi-clock-history"></i>
        최근 본
      </button>
      <button
        class="tab"
        :class="{ active: activeTab === 'history' }"
        @click="activeTab = 'history'"
      >
        <i class="bi bi-stars"></i>
        추천 이력
      </button>
      <button
        class="tab"
        :class="{ active: activeTab === 'preference' }"
        @click="activeTab = 'preference'"
      >
        <i class="bi bi-sliders"></i>
        선호도 설정
      </button>
    </div>

    <!-- 좋아요 카드 -->
    <div v-show="activeTab === 'liked'" class="tab-content">
      <div v-if="loading" class="loading">
        <div class="spinner-border spinner-border-sm"></div>
        <span>불러오는 중...</span>
      </div>
      <div v-else-if="likedCards.length === 0" class="empty">
        <i class="bi bi-heart"></i>
        <p>좋아요한 카드가 없습니다.</p>
        <router-link to="/cards" class="btn-link">카드 둘러보기</router-link>
      </div>
      <div v-else class="card-list">
        <CardMiniItem
          v-for="card in likedCards"
          :key="card.id"
          :card="card"
          @click="goToCard(card.id)"
        />
      </div>
    </div>

    <!-- 최근 본 카드 -->
    <div v-show="activeTab === 'recent'" class="tab-content">
      <div v-if="loading" class="loading">
        <div class="spinner-border spinner-border-sm"></div>
        <span>불러오는 중...</span>
      </div>
      <div v-else-if="recentCards.length === 0" class="empty">
        <i class="bi bi-clock"></i>
        <p>최근 본 카드가 없습니다.</p>
        <router-link to="/cards" class="btn-link">카드 둘러보기</router-link>
      </div>
      <div v-else class="card-list">
        <CardMiniItem
          v-for="card in recentCards"
          :key="card.id"
          :card="card"
          @click="goToCard(card.id)"
        />
      </div>
    </div>

    <!-- 추천 이력 -->
    <div v-show="activeTab === 'history'" class="tab-content">
      <div v-if="loading" class="loading">
        <div class="spinner-border spinner-border-sm"></div>
        <span>불러오는 중...</span>
      </div>
      <div v-else-if="recommendationHistory.length === 0" class="empty">
        <i class="bi bi-stars"></i>
        <p>추천 이력이 없습니다.</p>
        <router-link to="/cards?tab=recommend" class="btn-link">AI 추천 받기</router-link>
      </div>
      <div v-else class="history-list">
        <div
          v-for="log in recommendationHistory"
          :key="log.id"
          class="history-item"
        >
          <div class="history-header">
            <div class="history-query">"{{ log.query_text }}"</div>
            <div class="history-date">{{ formatDate(log.created_at) }}</div>
          </div>
          <div class="history-cards">
            <CardMiniItem
              v-for="result in log.result_cards"
              :key="result.card.id"
              :card="result.card"
              :score="result.score"
              @click="goToCard(result.card.id)"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- 선호도 설정 -->
    <div v-show="activeTab === 'preference'" class="tab-content">
      <div v-if="loading" class="loading">
        <div class="spinner-border spinner-border-sm"></div>
        <span>불러오는 중...</span>
      </div>
      <PreferenceForm
        v-else
        :profile="userProfile"
        @save="handleSavePreference"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCardsStore } from '@/stores/cards'
import { storeToRefs } from 'pinia'
import CardMiniItem from './CardMiniItem.vue'
import PreferenceForm from './PreferenceForm.vue'

const router = useRouter()
const cardsStore = useCardsStore()
const {
  likedCards,
  recentCards,
  recommendationHistory,
  userProfile
} = storeToRefs(cardsStore)

const activeTab = ref('liked')
const loading = ref(true)

onMounted(async () => {
  loading.value = true
  try {
    await Promise.all([
      cardsStore.fetchLikedCards(),
      cardsStore.fetchRecentCards(),
      cardsStore.fetchRecommendationHistory(),
      cardsStore.fetchUserProfile()
    ])
  } finally {
    loading.value = false
  }
})

function goToCard(id) {
  router.push({ name: 'card-detail', params: { id } })
}

function formatDate(dateStr) {
  const date = new Date(dateStr)
  return date.toLocaleDateString('ko-KR', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

async function handleSavePreference(data) {
  await cardsStore.updateUserProfile(data)
}
</script>

<style scoped>
.card-section {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #efefef;
}

.section-header {
  margin-bottom: 16px;
}

.section-title {
  font-weight: 800;
  color: #111;
  margin: 0;
}

/* 탭 */
.tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.tab {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 36px;
  padding: 0 14px;
  border-radius: 18px;
  border: 1px solid #e8e8e8;
  background: #fff;
  color: #555;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.tab:hover {
  border-color: #ccc;
}

.tab.active {
  background: #111;
  border-color: #111;
  color: #fff;
}

.tab i {
  font-size: 14px;
}

/* 탭 컨텐츠 */
.tab-content {
  min-height: 200px;
}

/* 로딩 */
.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 40px 0;
  color: #888;
  font-size: 13px;
}

/* 빈 상태 */
.empty {
  text-align: center;
  padding: 40px 20px;
  color: #888;
}

.empty i {
  font-size: 32px;
  margin-bottom: 12px;
  display: block;
}

.empty p {
  margin: 0 0 12px;
  font-size: 14px;
}

.btn-link {
  display: inline-block;
  padding: 8px 16px;
  border-radius: 8px;
  background: #111;
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  text-decoration: none;
}

.btn-link:hover {
  background: #000;
  color: #fff;
}

/* 카드 리스트 */
.card-list {
  display: grid;
  gap: 10px;
}

/* 추천 이력 */
.history-list {
  display: grid;
  gap: 16px;
}

.history-item {
  padding: 14px;
  border: 1px solid #efefef;
  border-radius: 12px;
  background: #fafafa;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.history-query {
  font-size: 14px;
  font-weight: 600;
  color: #111;
}

.history-date {
  font-size: 12px;
  color: #888;
}

.history-cards {
  display: grid;
  gap: 8px;
}
</style>
