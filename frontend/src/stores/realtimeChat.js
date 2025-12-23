// src/stores/realtimeChat.js
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useRealtimeChatStore = defineStore('realtimeChat', () => {
  const socket = ref(null)
  const connected = ref(false)
  const messages = ref([
    { id: 1, sender: 'system', text: '채팅방에 연결하면 메시지가 여기에 표시됩니다.' },
  ])

  const connect = (roomId) => {
    if (socket.value) return
    // ✅ 배포 시 wss:// 로 바꾸기
    const wsUrl = `ws://localhost:8000/ws/chat/${roomId}/`
    socket.value = new WebSocket(wsUrl)

    socket.value.onopen = () => {
      connected.value = true
      messages.value.push({ id: Date.now(), sender: 'system', text: '연결됨 ✅' })
    }

    socket.value.onclose = () => {
      connected.value = false
      socket.value = null
      messages.value.push({ id: Date.now(), sender: 'system', text: '연결 종료됨' })
    }

    socket.value.onerror = () => {
      connected.value = false
      messages.value.push({ id: Date.now(), sender: 'system', text: '연결 오류 발생' })
    }

    socket.value.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data)
        messages.value.push({
          id: Date.now(),
          sender: data.sender ?? 'unknown',
          text: data.message ?? '',
        })
      } catch {
        // 혹시 문자열로 올 경우
        messages.value.push({ id: Date.now(), sender: 'server', text: String(e.data) })
      }
    }
  }

  const send = (sender, text) => {
    const msg = text?.trim()
    if (!msg) return
    if (!socket.value || socket.value.readyState !== WebSocket.OPEN) return

    socket.value.send(JSON.stringify({ sender, message: msg }))
  }

  const disconnect = () => {
    socket.value?.close()
  }

  const reset = () => {
    messages.value = [{ id: 1, sender: 'system', text: '채팅을 초기화했어요.' }]
  }

  return { connected, messages, connect, send, disconnect, reset }
})
