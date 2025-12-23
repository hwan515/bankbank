<template>
  <div class="community container py-4">
    <header class="hero">
      <div>
        <p class="eyebrow">커뮤니티</p>
        <h1 class="title">금융 경험을 나누세요</h1>
        <p class="sub">
          예적금 · 카드 사용 후기를 공유하고 궁금한 점을 질문해 보세요.
        </p>
      </div>
      <button
        v-if="accountStore.isLogin"
        class="btn-solid"
        @click="goWrite"
      >
        새 글쓰기
      </button>
      <RouterLink
        v-else
        :to="{ name: 'login' }"
        class="btn-ghost"
      >
        로그인하고 글쓰기
      </RouterLink>
    </header>

    <div class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        :class="['tab', { active: activeTab === tab.key }]"
        @click="activeTab = tab.key"
      >
        <span>{{ tab.label }}</span>
        <span class="pill">{{ tab.badge }}</span>
      </button>
    </div>

    <div class="board card">
      <div class="board-head">
        <div class="left">
          <h3 class="board-title">{{ currentTab.label }}</h3>
          <p class="board-sub">작성자 · 제목 · 작성일을 한눈에 확인하세요.</p>
        </div>
      </div>

      <div v-if="loading" class="empty">목록을 불러오는 중입니다...</div>
      <div v-else-if="error" class="empty text-danger">오류: {{ error }}</div>
      <div v-else-if="!posts.length" class="empty">아직 작성된 글이 없습니다.</div>

      <div v-else class="list">
        <div class="list-head">
          <span>제목</span>
          <span>작성자</span>
          <span>작성일</span>
        </div>
        <button
          v-for="post in posts"
          :key="post.id"
          class="list-row"
          @click="goDetail(post.id)"
        >
          <div class="title-wrap">
            <span class="title">{{ post.title }}</span>
            <span class="meta">댓글 {{ post.comment_count }}</span>
          </div>
          <span class="author">{{ post.author_name }}</span>
          <span class="date">{{ formatDate(post.created_at) }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { useCommunityStore } from '@/stores/community'
import { useAccountStore } from '@/stores/account'

const router = useRouter()
const communityStore = useCommunityStore()
const accountStore = useAccountStore()

const tabs = [
  { key: 'product', label: '금융 상품 리뷰', badge: '예·적금' },
  { key: 'card', label: '카드 리뷰', badge: '카드' },
]

const activeTab = ref('product')
const loading = computed(() => communityStore.loading)
const error = computed(() => communityStore.error)
const posts = computed(() => communityStore.posts)
const currentTab = computed(() => tabs.find((t) => t.key === activeTab.value) || tabs[0])

const loadPosts = async () => {
  try {
    await communityStore.fetchPosts(activeTab.value)
  } catch (e) {
    // 에러 상태는 store에서 관리
  }
}

onMounted(loadPosts)
watch(activeTab, loadPosts)

const goDetail = (id) => {
  router.push({ name: 'community-detail', params: { id } })
}

const goWrite = () => {
  router.push({
    name: 'community-new',
    query: { board: activeTab.value },
  })
}

const formatDate = (value) => {
  if (!value) return ''
  return new Intl.DateTimeFormat('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(new Date(value))
}
</script>

<style scoped>
.community {
  max-width: 980px;
}

.hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.eyebrow {
  font-size: 12px;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: #666;
  margin-bottom: 4px;
}

.title {
  font-size: 28px;
  font-weight: 900;
  margin: 0;
  color: #0e0e0e;
}

.sub {
  margin: 6px 0 0;
  color: #666;
  font-size: 14px;
}

.tabs {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin-bottom: 14px;
}

.tab {
  border: 1px solid #e8e8e8;
  background: #fff;
  border-radius: 12px;
  padding: 12px 14px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 800;
  color: #111;
  transition: all 0.15s ease;
}

.tab .pill {
  background: #f4f4f4;
  border-radius: 999px;
  padding: 6px 10px;
  font-size: 12px;
  color: #444;
}

.tab.active {
  border-color: #111;
  box-shadow: 0 8px 18px rgba(0, 0, 0, 0.06);
}

.board {
  border: 1px solid #eaeaea;
  background: #fff;
  border-radius: 14px;
  padding: 14px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08), 0 10px 24px rgba(0, 0, 0, 0.05);
}

.board-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid #f0f0f0;
  padding-bottom: 10px;
  margin-bottom: 8px;
}

.board-title {
  margin: 0;
  font-weight: 900;
  font-size: 18px;
}

.board-sub {
  margin: 2px 0 0;
  font-size: 13px;
  color: #777;
}

.list {
  display: grid;
  gap: 6px;
}

.list-head,
.list-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  align-items: center;
  gap: 8px;
}

.list-head {
  font-size: 12px;
  color: #777;
  padding: 4px 10px;
}

.list-row {
  background: #fafafa;
  border: 1px solid #efefef;
  border-radius: 12px;
  padding: 10px;
  transition: transform 0.1s ease, box-shadow 0.1s ease, border-color 0.1s ease;
  text-align: left;
}

.list-row:hover {
  transform: translateY(-2px);
  border-color: #e3e3e3;
  box-shadow: 0 8px 18px rgba(0, 0, 0, 0.06);
}

.title-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.title {
  font-weight: 800;
  font-size: 15px;
  margin: 0;
}

.meta {
  font-size: 12px;
  color: #666;
  background: #fff;
  border: 1px solid #ededed;
  border-radius: 999px;
  padding: 2px 8px;
}

.author,
.date {
  font-size: 13px;
  color: #444;
}

.empty {
  padding: 20px 10px;
  text-align: center;
  color: #666;
}

.btn-solid,
.btn-ghost,
.btn-line {
  border-radius: 12px;
  font-weight: 800;
  padding: 10px 14px;
  border: 1px solid #111;
  background: #111;
  color: #fff;
  text-decoration: none;
}

.btn-ghost {
  background: #fff;
  color: #111;
}

.btn-line {
  background: #fff;
}

@media (max-width: 768px) {
  .hero {
    flex-direction: column;
    align-items: flex-start;
  }

  .list-head,
  .list-row {
    grid-template-columns: 2fr 1fr;
  }

  .list-head span:last-child,
  .list-row .date {
    display: none;
  }
}
</style>
