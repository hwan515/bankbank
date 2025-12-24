<template>
  <div class="modal-backdrop" @click.self="emit('close')">
    <div class="modal-content rounded-4 shadow ui-card">
      <div class="modal-header p-4 pb-3 border-bottom-0">
        <h1 class="fw-bold mb-0 fs-4">개인정보 수정</h1>
        <button type="button" class="btn-close" aria-label="Close" @click="emit('close')"></button>
      </div>

      <div class="modal-body">
        <form @submit.prevent="submit" class="form">
          <div class="field">
            <label class="label" for="floatingUsername">닉네임</label>
            <input
              v-model.trim="form.username"
              type="text"
              class="input"
              id="floatingUsername"
              placeholder="username"
              disabled
            />
            <div class="help">닉네임은 변경할 수 없어요.</div>
          </div>

          <div class="field">
            <label class="label" for="floatingEmail">이메일</label>
            <input
              v-model.trim="form.email"
              type="email"
              class="input"
              id="floatingEmail"
              placeholder="name@example.com"
            />
          </div>

          <div class="field">
            <label class="label" for="floatingGreeting">인사말</label>
            <textarea
              v-model.trim="form.greeting"
              class="textarea"
              id="floatingGreeting"
              placeholder="간단한 한 줄 소개를 적어주세요."
              rows="4"
            ></textarea>
          </div>

          <div class="actions">
            <button class="btn solid" type="submit" :disabled="saving">
              {{ saving ? '저장 중...' : '저장' }}
            </button>
            <button class="btn ghost" type="button" @click="emit('close')">
              취소
            </button>
          </div>
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

// ESC로 닫기
const onKeydown = (e) => {
  if (e.key === 'Escape') emit('close')
}
onMounted(() => window.addEventListener('keydown', onKeydown))
onBeforeUnmount(() => window.removeEventListener('keydown', onKeydown))
</script>

<style scoped>
/* overlay */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: grid;
  place-items: center;
  z-index: 9999;
  padding: 24px;
}

/* panel */
.modal-panel {
  width: min(520px, 100%);
  background: var(--surface);
  border: 1px solid var(--border);
}
</style>
