import { defineStore } from 'pinia'
import { ref } from 'vue'
import { http } from '@/api/http'

export const useChatRoomsStore = defineStore('chatRooms', () => {
  // 내 방(DM/참여방)
  const rooms = ref([])
  const loadingRooms = ref(false)

  // 공개방(전체 노출)
  const publicRooms = ref([])
  const loadingPublicRooms = ref(false)

  // 히스토리
  const history = ref([])
  const loadingHistory = ref(false)

  // username 검색(DM 생성용)
  const searching = ref(false)
  const userResults = ref([])

  const fetchRooms = async () => {
    loadingRooms.value = true
    try {
      const res = await http.get('/api/chat/rooms/')
      rooms.value = res.data
      return rooms.value
    } finally {
      loadingRooms.value = false
    }
  }

  const fetchPublicRooms = async () => {
    loadingPublicRooms.value = true
    try {
      const res = await http.get('/api/chat/rooms/public/')
      publicRooms.value = res.data
      return publicRooms.value
    } finally {
      loadingPublicRooms.value = false
    }
  }

  const joinRoom = async (roomId) => {
    await http.post(`/api/chat/rooms/${roomId}/join/`)
  }

  const fetchHistory = async (roomId, limit = 50) => {
    loadingHistory.value = true
    try {
      const res = await http.get(`/api/chat/rooms/${roomId}/messages/`, { params: { limit } })
      history.value = res.data.map((m) => ({
        id: m.id,
        sender: m.sender,
        text: m.content,
        created_at: m.created_at,
      }))
      return history.value
    } finally {
      loadingHistory.value = false
    }
  }

  const searchUsers = async (q) => {
    const keyword = (q || '').trim()
    if (!keyword) {
      userResults.value = []
      return []
    }
    searching.value = true
    try {
      // ⚠️ 너 프로젝트 URL에 맞춰 수정
      const res = await http.get('/api/accounts/users/search/', { params: { q: keyword } })
      userResults.value = res.data
      return userResults.value
    } finally {
      searching.value = false
    }
  }

  const ensureDM = async (username) => {
    const u = (username || '').trim()
    if (!u) throw new Error('username required')

    const res = await http.post('/api/chat/dm/ensure/', { username: u })
    const room = res.data

    // 내 방 목록에 없으면 추가
    if (!rooms.value.find((r) => r.id === room.id)) {
      rooms.value.unshift(room)
    }
    return room
  }

  const ensureLobby = async () => {
    // 로비를 공개방으로 만들고, 유저 가입 보장하는 API (있다고 가정)
    const res = await http.post('/api/chat/lobby/ensure/')
    return res.data
  }

  return {
    rooms, loadingRooms,
    publicRooms, loadingPublicRooms,
    history, loadingHistory,
    searching, userResults,
    fetchRooms, fetchPublicRooms,
    joinRoom, fetchHistory,
    searchUsers, ensureDM,
    ensureLobby,
  }
})
