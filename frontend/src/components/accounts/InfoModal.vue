<template>
  <div class="modal-backdrop" @click.self="emit('close')">
    <div class="modal-content rounded-4 shadow">
      <div class="modal-header p-4 pb-3 border-bottom-0">
        <h1 class="fw-bold mb-0 fs-4">{{ isNew ? '정보 추가' : '정보 편집' }}</h1>
        <button type="button" class="btn-close" aria-label="Close" @click="emit('close')"></button>
      </div>

      <div class="modal-body p-4 pt-0">
        <form @submit.prevent="submit">
          <div class="form-floating mb-3">
            <input
              v-model.trim="form.title"
              type="text"
              class="form-control rounded-3"
              id="floatingInfoTitle"
              placeholder="제목(선택)"
            />
            <label for="floatingInfoTitle">제목 (선택)</label>
          </div>

          <div class="form-floating mb-3">
            <textarea
              v-model.trim="form.content"
              class="form-control rounded-3"
              id="floatingInfoText"
              placeholder="내용"
              style="height: 140px"
            ></textarea>
            <label for="floatingInfoText">내용</label>
          </div>

          <button class="w-100 mb-2 btn btn-lg rounded-3 btn-primary" type="submit" :disabled="saving">
            {{ saving ? '저장 중...' : '저장' }}
          </button>

          <button class="w-100 mb-2 btn btn-lg rounded-3 btn-outline-secondary" type="button" @click="emit('close')">
            취소
          </button>

          <button
            v-if="!isNew"
            class="w-100 btn btn-lg rounded-3 btn-outline-danger"
            type="button"
            @click="emit('remove')"
            :disabled="saving"
          >
            삭제
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAccountStore } from '@/stores/account'
import { reactive, watch, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({
  initial: { type: Object, required: true }, // { title, text }
  saving: { type: Boolean, default: false },
  isNew: { type: Boolean, default: false },
})

const emit = defineEmits(['close', 'save', 'remove'])

const form = reactive({
  title: '',
  content: '',
})

watch(
  () => props.initial,
  (v) => {
    form.title = v?.title ?? ''
    form.content = v?.content ?? ''
  },
  { immediate: true, deep: true }
)

const submit = () => {
  if (!form.content?.trim()) return alert('내용을 입력해줘!')
  emit('save', { title: form.title, content: form.content })
}

// ESC로 닫기
const onKeydown = (e) => {
  if (e.key === 'Escape') emit('close')
}
onMounted(() => window.addEventListener('keydown', onKeydown))
onBeforeUnmount(() => window.removeEventListener('keydown', onKeydown))
</script>

<style scoped>
/* ✅ 모달만 fixed overlay (프로필 레이아웃 건드리지 않음) */
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
  background: #fff;
  border: 1px solid #eee;
}
</style>
