<template>
  <div class="container py-4 form-page">
    <header class="head">
      <div>
        <p class="eyebrow">커뮤니티</p>
        <h1 class="title serif-title">{{ isEdit ? '게시글 수정' : '새 글 작성' }}</h1>
        <p class="sub">금융상품/카드 사용 경험을 공유해 주세요.</p>
      </div>
      <button class="link" @click="goBack">← 목록으로</button>
    </header>

    <div v-if="!accountStore.isLogin" class="empty">
      글을 작성하려면 로그인 해주세요.
      <RouterLink :to="{ name: 'login' }" class="link ms-1">로그인</RouterLink>
    </div>

    <form v-else class="card ui-card" @submit.prevent="handleSubmit">
      <div class="field">
        <label>게시판</label>
        <select v-model="boardType">
          <option value="product">금융 상품 리뷰</option>
          <option value="card">카드 리뷰</option>
        </select>
      </div>

      <div class="field">
        <label>제목</label>
        <input
          v-model="title"
          type="text"
          placeholder="제목을 입력하세요"
          required
        />
      </div>

      <div class="field">
        <label>내용</label>
        <textarea
          v-model="content"
          rows="8"
          placeholder="내용을 입력하세요"
          required
        />
      </div>

      <p v-if="errorMsg" class="ui-text-danger">{{ errorMsg }}</p>

      <div class="actions">
        <button class="ui-btn ui-btn-ghost" type="button" @click="goBack">취소</button>
        <button class="ui-btn ui-btn-primary" type="submit">
          {{ isEdit ? '수정하기' : '등록하기' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { useCommunityStore } from '@/stores/community'
import { useAccountStore } from '@/stores/account'

const route = useRoute()
const router = useRouter()
const communityStore = useCommunityStore()
const accountStore = useAccountStore()

const title = ref('')
const content = ref('')
const boardType = ref(route.query.board || 'product')
const errorMsg = ref('')

const isEdit = computed(() => route.name === 'community-edit')

const loadData = async () => {
  if (!isEdit.value) return
  try {
    const data = await communityStore.fetchPostDetail(route.params.id)
    if (!data.is_author) {
      errorMsg.value = '본인 글만 수정할 수 있습니다.'
      return
    }
    title.value = data.title
    content.value = data.content
    boardType.value = data.board_type
  } catch (e) {
    errorMsg.value = e.message || '게시글을 불러오지 못했습니다.'
  }
}

onMounted(loadData)

const handleSubmit = async () => {
  errorMsg.value = ''
  if (!title.value.trim() || !content.value.trim()) {
    errorMsg.value = '제목과 내용을 모두 입력해주세요.'
    return
  }

  const payload = {
    title: title.value,
    content: content.value,
    board_type: boardType.value,
  }

  try {
    if (isEdit.value) {
      await communityStore.updatePost(route.params.id, payload)
      router.push({ name: 'community-detail', params: { id: route.params.id } })
    } else {
      const created = await communityStore.createPost(payload)
      router.push({ name: 'community-detail', params: { id: created.id } })
    }
  } catch (e) {
    errorMsg.value = e.message || '저장 중 오류가 발생했습니다.'
  }
}

const goBack = () => {
  router.push({ name: 'community' })
}
</script>

<style scoped>
.form-page {
  max-width: 760px;
}

.head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 12px;
}

.eyebrow {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--muted);
  margin: 0;
}

.title {
  margin: 6px 0 4px;
  font-size: clamp(20px, 2vw, 26px);
  font-weight: 700;
}

.sub {
  margin: 0;
  color: var(--muted);
  font-size: 14px;
}

.card {
  border-radius: 14px;
  padding: 16px;
}

.field {
  display: grid;
  gap: 6px;
  margin-bottom: 12px;
}

label {
  font-weight: 700;
  color: var(--ink);
}

input,
textarea,
select {
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  padding: 10px 12px;
  background: var(--bg-alt);
}

textarea {
  resize: vertical;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}


.empty {
  background: var(--bg-alt);
  border: 1px dashed var(--border);
  border-radius: 12px;
  padding: 14px;
  color: var(--muted);
  margin-top: 12px;
}

.link {
  background: none;
  border: none;
  padding: 0;
  color: var(--accent);
  font-weight: 700;
  text-decoration: none;
}
</style>
