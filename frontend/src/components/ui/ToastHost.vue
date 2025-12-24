<template>
  <div class="toast-host" aria-live="polite" aria-atomic="true">
    <div v-for="toast in toasts" :key="toast.id" class="toast" :class="`type-${toast.type}`">
      <span class="msg">{{ toast.message }}</span>
      <button class="close" type="button" aria-label="닫기" @click="remove(toast.id)">×</button>
    </div>
  </div>
</template>

<script setup>
import { storeToRefs } from 'pinia'
import { useToastStore } from '@/stores/toast'

const toastStore = useToastStore()
const { toasts } = storeToRefs(toastStore)
const { remove } = toastStore
</script>

<style scoped>
.toast-host {
  position: fixed;
  top: 72px;
  right: 18px;
  z-index: 10000;
  display: grid;
  gap: 8px;
  pointer-events: none;
}

.toast {
  min-width: 220px;
  max-width: 320px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  box-shadow: var(--shadow-2);
  padding: 10px 12px;
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 8px;
  align-items: center;
  color: var(--ink);
  pointer-events: auto;
}

.msg {
  font-size: 13px;
  color: var(--ink);
}

.close {
  border: none;
  background: transparent;
  color: var(--ink-soft);
  font-size: 16px;
  line-height: 1;
  cursor: pointer;
}

.type-info {
  border-left: 3px solid var(--accent);
}
.type-warning {
  border-left: 3px solid #e0a000;
}
.type-error {
  border-left: 3px solid #d00000;
}

@media (max-width: 576px) {
  .toast-host {
    right: 12px;
    left: 12px;
  }
  .toast {
    max-width: none;
  }
}
</style>
