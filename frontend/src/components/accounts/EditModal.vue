<template>
  <div class="modal-backdrop" @click.self="emit('close')">
    <div class="modal-content rounded-4 shadow ui-card">
      <div class="modal-header p-4 pb-3 border-bottom-0">
        <h1 class="fw-bold mb-0 fs-4">개인정보 수정</h1>
        <button type="button" class="btn-close" aria-label="Close" @click="emit('close')"></button>
      </div>

      <div class="modal-body p-4 pt-0">
        <form @submit.prevent="submit">
          <div class="form-floating mb-3">
            <input
              v-model.trim="form.username"
              type="text"
              class="form-control rounded-3"
              id="floatingUsername"
              placeholder="username"
              disabled="true"
            />
            <label for="floatingUsername">닉네임</label>
          </div>

          <div class="form-floating mb-3">
            <input
              v-model.trim="form.email"
              type="email"
              class="form-control rounded-3"
              id="floatingEmail"
              placeholder="name@example.com"
            />
            <label for="floatingEmail">이메일</label>
          </div>

          <div class="form-floating mb-3">
            <textarea
              v-model.trim="form.greeting"
              class="form-control rounded-3"
              id="floatingGreeting"
              placeholder="인사말"
              style="height: 110px"
            />
            <label for="floatingGreeting">인사말</label>
          </div>

          <button class="w-100 mb-2 btn btn-lg rounded-3 btn-primary" type="submit" :disabled="saving">
            {{ saving ? '저장 중...' : '저장' }}
          </button>

          <button class="w-100 btn btn-lg rounded-3 btn-outline-secondary" type="button" @click="emit('close')">
            취소
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, watch, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({
  initial: { type: Object, required: true },
  saving: { type: Boolean, default: false },
})

const emit = defineEmits(['close', 'save'])

const form = reactive({
  username: '',
  email: '',
  greeting: '',
})

watch(
  () => props.initial,
  (v) => {
    form.username = v?.username ?? ''
    form.email = v?.email ?? ''
    form.greeting = v?.greeting ?? ''
  },
  { immediate: true, deep: true }
)

const submit = () => {
  if (!form.username) return alert('닉네임은 비워둘 수 없어!')

  emit('save', {
    username: form.username,
    email: form.email,
    greeting: form.greeting,
  })
}

// ESC로 닫기 (모달만 영향)
const onKeydown = (e) => {
  if (e.key === 'Escape') emit('close')
}
onMounted(() => window.addEventListener('keydown', onKeydown))
onBeforeUnmount(() => window.removeEventListener('keydown', onKeydown))
</script>

<style scoped>
/* ✅ 프로필 레이아웃 건드리지 않게 모달만 fixed + 높은 z-index */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: grid;
  place-items: center;
  z-index: 9999;
  padding: 24px;
}

.modal-content {
  width: min(520px, 100%);
  background: var(--surface);
  border: 1px solid var(--border);
}
</style>
