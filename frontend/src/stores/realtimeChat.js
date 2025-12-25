import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useRealtimeChatStore = defineStore('realtimeChat', () => {
  const socket = ref(null)
  const connected = ref(false)
  const messages = ref([])
  const currentRoomId = ref(null)
  const httpBaseUrl =
    import.meta.env.VITE_API_BASE_URL ||
    import.meta.env.VITE_API_URL ||
    'http://localhost:8000'
  const wsBaseUrl =
    import.meta.env.VITE_WS_BASE_URL ||
    httpBaseUrl.replace(/^http:\/\//, 'ws://').replace(/^https:\/\//, 'wss://')

  const connect = (roomId) => {
    if (!roomId) throw new Error('roomId required')

    // 방 바뀌면 재연결
    if (socket.value && currentRoomId.value !== roomId) {
      socket.value.close()
      socket.value = null
      connected.value = false
    }
    if (socket.value) return

    currentRoomId.value = roomId
    const token = localStorage.getItem('token')
    const cleanBase = wsBaseUrl.replace(/\/$/, '')
    const wsUrl = `${cleanBase}/ws/chat/${roomId}/?token=${token}`

    socket.value = new WebSocket(wsUrl)

    socket.value.onopen = () => { connected.value = true }
    socket.value.onclose = () => { connected.value = false; socket.value = null }
    socket.value.onmessage = (e) => {
      const data = JSON.parse(e.data)
      messages.value.push({
        id: data.id ?? Date.now(),
        sender: data.sender,
        text: data.message,
        created_at: data.created_at,
      })
    }
  }

  const disconnect = () => socket.value?.close()

  const setInitial = (history) => {
    messages.value = [...(history || [])]
  }

  const send = (text) => {
    const msg = (text || '').trim()
    if (!msg) return
    if (!socket.value || socket.value.readyState !== WebSocket.OPEN) return
    socket.value.send(JSON.stringify({ message: msg }))
  }

  return { connected, messages, currentRoomId, connect, disconnect, setInitial, send }
})
