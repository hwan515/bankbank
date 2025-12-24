import { defineStore } from 'pinia'
import { ref } from 'vue'

let nextId = 1

export const useToastStore = defineStore('toast', () => {
  const toasts = ref([])

  const remove = (id) => {
    toasts.value = toasts.value.filter((toast) => toast.id !== id)
  }

  const push = (message, options = {}) => {
    const toast = {
      id: nextId++,
      message,
      type: options.type || 'info',
    }
    toasts.value.push(toast)

    const duration = options.duration ?? 2400
    if (duration > 0) {
      setTimeout(() => remove(toast.id), duration)
    }
  }

  return {
    toasts,
    push,
    remove,
  }
})
