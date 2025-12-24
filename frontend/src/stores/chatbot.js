// src/stores/chatbot.js
import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from './api'

export const useChatbotStore = defineStore('chatbot', () => {
  const messages = ref([
    { id: 1, role: 'bot', text: '안녕하세요! 예금/적금/카드 관련 질문을 해보세요 🙂' },
  ])
  const loading = ref(false)

  const sendMessage = async (text) => {
    const userText = text?.trim()
    if (!userText) return

    messages.value.push({ id: Date.now(), role: 'user', text: userText })

    loading.value = true
    try {
      const res = await api.post('/api/chatbot/', {
        message: userText,
      })

      const reply = res?.data?.reply ?? '응답이 비어있어요.'
      messages.value.push({ id: Date.now() + 1, role: 'bot', text: reply })
    } catch (e) {
      console.error(e)
      messages.value.push({
        id: Date.now() + 2,
        role: 'bot',
        text: '잠시 오류가 발생했어요. 다시 시도해 주세요.',
      })
    } finally {
      loading.value = false
    }
  }

  const clear = () => {
    messages.value = [{ id: 1, role: 'bot', text: '대화를 초기화했어요 🙂' }]
  }

  return { messages, loading, sendMessage, clear }
})
