<template>
  <div class="container py-4 detail" v-if="post">
    <div class="breadcrumb">
      <button class="link" @click="goList">← 목록으로</button>
      <span class="pill">{{ boardLabel }}</span>
    </div>

    <header class="head">
      <div>
        <h1 class="title serif-title">{{ post.title }}</h1>
        <div class="meta">
          <span>{{ post.author_name }}</span>
          <span>•</span>
          <span>{{ formatDate(post.created_at) }}</span>
        </div>
      </div>
      <div class="actions" v-if="post.is_author">
        <button class="ui-btn ui-btn-ghost" @click="goEdit">수정</button>
        <button class="ui-btn ui-btn-danger" @click="handleDelete">삭제</button>
      </div>
    </header>

    <article class="content card ui-card">
      <p class="body" v-text="post.content"></p>
      <div class="reactions">
        <button
          class="chip"
          :class="{ active: post.user_reaction === 'like' }"
          @click="reactPost('like')"
        >
          👍 좋아요 {{ post.like_count }}
        </button>
        <button
          class="chip"
          :class="{ active: post.user_reaction === 'dislike' }"
          @click="reactPost('dislike')"
        >
          👎 싫어요 {{ post.dislike_count }}
        </button>
      </div>
    </article>

    <section class="comments card ui-card">
      <div class="comment-head">
        <h3>댓글 {{ comments.length }}</h3>
        <p>의견을 남기고 다른 사람의 경험을 확인하세요.</p>
      </div>

      <div v-if="accountStore.isLogin" class="comment-form">
        <textarea
          v-model="newComment"
          rows="3"
          placeholder="댓글을 남겨보세요."
        />
        <div class="form-actions">
          <span class="hint">게시자는 본인 댓글만 수정/삭제할 수 있습니다.</span>
          <button class="ui-btn ui-btn-primary" @click="submitComment" :disabled="!newComment.trim()">
            등록
          </button>
        </div>
        <p v-if="commentError" class="ui-text-danger small mt-1">{{ commentError }}</p>
      </div>
      <div v-else class="empty">
        댓글을 작성하려면 로그인 해주세요.
        <RouterLink :to="{ name: 'login' }" class="link ms-1">로그인</RouterLink>
      </div>

      <div v-if="!comments.length" class="empty">첫 댓글을 남겨보세요.</div>
      <ul class="comment-list" v-else>
        <li v-for="comment in comments" :key="comment.id" class="comment-item">
          <div class="comment-meta">
            <div>
              <div class="author">{{ comment.author_name }}</div>
              <div class="date">{{ formatDate(comment.created_at) }}</div>
            </div>
            <div class="comment-actions" v-if="comment.is_author">
              <button class="link" @click="startEdit(comment)">수정</button>
              <button class="link ui-text-danger" @click="deleteComment(comment.id)">삭제</button>
            </div>
          </div>

          <div v-if="editingCommentId === comment.id" class="edit-box">
            <textarea v-model="editingContent" rows="3" />
            <div class="gap">
              <button class="ui-btn ui-btn-ghost" @click="cancelEdit">취소</button>
              <button class="ui-btn ui-btn-primary" @click="saveComment">저장</button>
            </div>
          </div>
          <p v-else class="comment-body">{{ comment.content }}</p>

          <div class="comment-reactions">
            <button
              class="chip"
              :class="{ active: comment.user_reaction === 'like' }"
              @click="reactComment(comment.id, 'like')"
            >
              👍 {{ comment.like_count }}
            </button>
            <button
              class="chip"
              :class="{ active: comment.user_reaction === 'dislike' }"
              @click="reactComment(comment.id, 'dislike')"
            >
              👎 {{ comment.dislike_count }}
            </button>
          </div>
        </li>
      </ul>
    </section>
  </div>

  <div v-else class="container py-5 text-center">
    <p>게시글을 불러오는 중입니다...</p>
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

const newComment = ref('')
const commentError = ref('')
const editingCommentId = ref(null)
const editingContent = ref('')

const post = computed(() => communityStore.currentPost)
const comments = computed(() => post.value?.comments || [])

const boardLabel = computed(() => {
  if (post.value?.board_type === 'card') return '카드 리뷰'
  return '금융 상품 리뷰'
})

const loadPost = async () => {
  try {
    await communityStore.fetchPostDetail(route.params.id)
  } catch (e) {
    commentError.value = e.message || '게시글을 불러오지 못했습니다.'
  }
}

onMounted(loadPost)

const formatDate = (value) => {
  if (!value) return ''
  return new Intl.DateTimeFormat('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value))
}

const goList = () => {
  router.push({ name: 'community' })
}

const goEdit = () => {
  if (!post.value) return
  router.push({ name: 'community-edit', params: { id: post.value.id } })
}

const handleDelete = async () => {
  if (!post.value) return
  if (!confirm('게시글을 삭제할까요?')) return
  try {
    await communityStore.deletePost(post.value.id)
    goList()
  } catch (e) {
    commentError.value = e.message || '삭제에 실패했습니다.'
  }
}

const submitComment = async () => {
  commentError.value = ''
  if (!newComment.value.trim()) {
    commentError.value = '내용을 입력해주세요.'
    return
  }
  try {
    await communityStore.createComment(post.value.id, newComment.value)
    newComment.value = ''
  } catch (e) {
    commentError.value = e.message || '댓글 작성에 실패했습니다.'
  }
}

const startEdit = (comment) => {
  editingCommentId.value = comment.id
  editingContent.value = comment.content
}

const cancelEdit = () => {
  editingCommentId.value = null
  editingContent.value = ''
}

const saveComment = async () => {
  if (!editingContent.value.trim()) return
  try {
    await communityStore.updateComment(editingCommentId.value, editingContent.value)
    cancelEdit()
  } catch (e) {
    commentError.value = e.message || '댓글 수정에 실패했습니다.'
  }
}

const deleteComment = async (commentId) => {
  if (!confirm('댓글을 삭제할까요?')) return
  try {
    await communityStore.deleteComment(commentId)
  } catch (e) {
    commentError.value = e.message || '댓글 삭제에 실패했습니다.'
  }
}

const reactPost = async (reaction) => {
  if (!accountStore.isLogin) {
    commentError.value = '반응을 남기려면 로그인 해주세요.'
    return
  }
  try {
    await communityStore.reactToPost(post.value.id, reaction)
  } catch (e) {
    commentError.value = e.message || '처리 중 오류가 발생했습니다.'
  }
}

const reactComment = async (commentId, reaction) => {
  if (!accountStore.isLogin) {
    commentError.value = '반응을 남기려면 로그인 해주세요.'
    return
  }
  try {
    await communityStore.reactToComment(commentId, reaction)
  } catch (e) {
    commentError.value = e.message || '처리 중 오류가 발생했습니다.'
  }
}
</script>

<style scoped>
.detail {
  max-width: 860px;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.link {
  background: none;
  border: none;
  padding: 0;
  color: var(--accent);
  text-decoration: none;
  font-weight: 700;
}

.pill {
  padding: 6px 10px;
  background: var(--bg-alt);
  border: 1px solid var(--border);
  border-radius: 999px;
  font-size: 12px;
  color: var(--ink-soft);
}

.head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 12px;
}

.title {
  margin: 0;
  font-size: clamp(20px, 2vw, 26px);
  font-weight: 700;
}

.meta {
  display: flex;
  gap: 6px;
  color: var(--muted);
  font-size: 13px;
  margin-top: 6px;
}

.actions {
  display: flex;
  gap: 8px;
}

.content {
  padding: 16px;
  margin-bottom: 16px;
  border-radius: 14px;
}

.body {
  white-space: pre-line;
  line-height: 1.6;
  color: var(--ink-soft);
  margin: 0 0 10px;
}

.reactions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.comments {
  border-radius: 14px;
  padding: 16px;
}

.comment-head h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
}

.comment-head p {
  margin: 2px 0 10px;
  color: var(--muted);
  font-size: 13px;
}

.comment-form textarea,
.edit-box textarea {
  width: 100%;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  padding: 10px;
  background: var(--bg-alt);
}

.form-actions {
  margin-top: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.hint {
  font-size: 12px;
  color: var(--muted);
}

.comment-list {
  list-style: none;
  padding: 0;
  margin: 12px 0 0;
  display: grid;
  gap: 12px;
}

.comment-item {
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 12px;
  background: var(--bg-alt);
}

.comment-meta {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.author {
  font-weight: 700;
  color: var(--ink);
}

.date {
  color: var(--muted);
  font-size: 12px;
}

.comment-body {
  margin: 8px 0;
  white-space: pre-line;
}

.comment-reactions {
  display: flex;
  gap: 6px;
}

.chip {
  border: 1px solid var(--border);
  background: var(--surface);
  border-radius: 999px;
  padding: 6px 10px;
  font-weight: 600;
  color: var(--ink-soft);
}

.chip.active {
  border-color: var(--accent);
  background: var(--accent);
  color: #fff;
}


.empty {
  background: var(--bg-alt);
  border: 1px dashed var(--border);
  border-radius: 12px;
  padding: 14px;
  color: var(--muted);
  text-align: center;
}

.gap {
  display: flex;
  gap: 8px;
  margin-top: 6px;
}

@media (max-width: 768px) {
  .head {
    flex-direction: column;
  }

  .actions {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>
