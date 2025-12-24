<template>
  <div class="modal-backdrop" @click.self="emit('close')">
    <div class="modal-panel" role="dialog" aria-modal="true" aria-label="개인정보 수정">
      <header class="modal-header">
        <div>
          <h1 class="title">개인정보 수정</h1>
          <p class="subtitle">이메일과 인사말을 업데이트할 수 있어요.</p>
        </div>

        <button type="button" class="icon-btn" aria-label="Close" @click="emit('close')">✕</button>
      </header>

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
            />
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
  background: #fff;
  border: 1px solid #eee;
  border-radius: 14px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.18);
  overflow: hidden;
}

.modal-header {
  padding: 16px 18px 10px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.title {
  margin: 0;
  font-size: 16px;
  font-weight: 800;
  letter-spacing: -0.2px;
  color: #111;
}

.subtitle {
  margin: 6px 0 0;
  font-size: 12px;
  color: #777;
}

.icon-btn {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  border: 1px solid #eee;
  background: #fff;
  cursor: pointer;
  font-size: 14px;
  line-height: 1;
  color: #222;
}
.icon-btn:hover {
  background: #fafafa;
}

/* body */
.modal-body {
  padding: 16px 18px 18px;
}

.form {
  display: grid;
  gap: 12px;
}

.field {
  display: grid;
  gap: 6px;
}

.label {
  font-size: 12px;
  font-weight: 700;
  color: #111;
}

.input,
.textarea {
  width: 100%;
  border: 1px solid #e7e7e7;
  border-radius: 12px;
  padding: 10px 12px;
  font-size: 13px;
  outline: none;
  background: #fff;
  color: #111;
}

.textarea {
  resize: none;
  min-height: 110px;
}

.input:focus,
.textarea:focus {
  border-color: #cfcfcf;
  box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.06);
}

.input:disabled {
  background: #fafafa;
  color: #666;
}

.help {
  font-size: 11px;
  color: #888;
}

.actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-top: 4px;
}

/* buttons */
.btn {
  height: 40px;
  border-radius: 12px;
  border: 1px solid transparent;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
}

.btn.solid {
  background: #111;
  color: #fff;
}
.btn.solid:hover {
  background: #000;
}
.btn.solid:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn.ghost {
  background: #fff;
  border-color: #e7e7e7;
  color: #111;
}
.btn.ghost:hover {
  background: #fafafa;
}
</style>
