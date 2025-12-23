import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from './api'

export const useCardsStore = defineStore('cards', () => {
  // 상태
  const cards = ref([])
  const currentCard = ref(null)
  const recommendedCards = ref([])
  const personalizedRecommendations = ref([])
  const companies = ref([])
  const isLoading = ref(false)
  const error = ref(null)
  const lastQuery = ref('')
  const pagination = ref({
    count: 0,
    page: 1,
    pageSize: 20,
    totalPages: 0
  })

  // 마이페이지 관련 상태
  const likedCards = ref([])
  const recentCards = ref([])
  const recommendationHistory = ref([])
  const userProfile = ref(null)

  // 카드사 목록 조회
  async function fetchCompanies() {
    try {
      const response = await api.get('/cards/companies/')
      companies.value = response.data
      return response.data
    } catch (err) {
      console.error('카드사 목록 조회 실패:', err)
      return []
    }
  }

  // 카드 목록 조회 (검색, 필터링)
  async function fetchCards(params = {}) {
    isLoading.value = true
    error.value = null

    try {
      const response = await api.get('/cards/', { params })
      cards.value = response.data.results
      pagination.value = {
        count: response.data.count,
        page: response.data.page,
        pageSize: response.data.page_size,
        totalPages: response.data.total_pages
      }
      return response.data
    } catch (err) {
      error.value = err.message || '카드 목록을 가져오는 중 오류가 발생했습니다.'
      cards.value = []
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // 카드 상세 조회
  async function fetchCardDetail(id) {
    isLoading.value = true
    error.value = null

    try {
      const response = await api.get(`/cards/${id}/`)
      currentCard.value = response.data
      return response.data
    } catch (err) {
      error.value = err.message || '카드 정보를 가져오는 중 오류가 발생했습니다.'
      currentCard.value = null
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // AI 카드 추천
  async function getRecommendations(query, k = 5, filters = {}) {
    isLoading.value = true
    error.value = null
    lastQuery.value = query

    try {
      const response = await api.post('/cards/card-recommendation/', {
        query,
        k,
        ...filters
      })
      // 응답 형식에 따라 처리
      recommendedCards.value = response.data.results || response.data
      return response.data
    } catch (err) {
      error.value = err.message || '추천을 가져오는 중 오류가 발생했습니다.'
      recommendedCards.value = []
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // 선호도 기반 카드 추천 (로그인 사용자)
  async function getPersonalizedRecommendations(params = {}) {
    try {
      const response = await api.get('/cards/recommend/personalized/', { params })
      personalizedRecommendations.value = response.data.results || []
      return response.data
    } catch (err) {
      console.error('개인화 추천 조회 실패:', err)
      personalizedRecommendations.value = []
      throw err
    }
  }

  // 상태 초기화
  function clearRecommendations() {
    recommendedCards.value = []
    error.value = null
    lastQuery.value = ''
  }

  function clearCurrentCard() {
    currentCard.value = null
  }

  // ============ 마이페이지 관련 함수 ============

  // 이벤트 기록 (VIEW, CLICK 등)
  async function recordEvent(cardId, eventType, context = {}) {
    try {
      await api.post('/cards/events/', {
        card_id: cardId,
        event_type: eventType,
        context
      })
    } catch (err) {
      console.error('이벤트 기록 실패:', err)
    }
  }

  // 좋아요 토글
  async function toggleLike(cardId) {
    try {
      const response = await api.post(`/cards/${cardId}/like/`)
      // currentCard가 있으면 상태 업데이트
      if (currentCard.value && currentCard.value.id === cardId) {
        currentCard.value.is_liked = response.data.liked
        currentCard.value.like_count = response.data.like_count
      }
      return response.data
    } catch (err) {
      console.error('좋아요 토글 실패:', err)
      throw err
    }
  }

  // 좋아요 카드 목록
  async function fetchLikedCards() {
    try {
      const response = await api.get('/cards/my/liked/')
      likedCards.value = response.data
      return response.data
    } catch (err) {
      console.error('좋아요 카드 조회 실패:', err)
      return []
    }
  }

  // 최근 본 카드
  async function fetchRecentCards() {
    try {
      const response = await api.get('/cards/my/recent/')
      recentCards.value = response.data
      return response.data
    } catch (err) {
      console.error('최근 본 카드 조회 실패:', err)
      return []
    }
  }

  // 추천 이력
  async function fetchRecommendationHistory() {
    try {
      const response = await api.get('/cards/my/recommendations/')
      recommendationHistory.value = response.data
      return response.data
    } catch (err) {
      console.error('추천 이력 조회 실패:', err)
      return []
    }
  }

  // 사용자 카드 프로필 조회
  async function fetchUserProfile() {
    try {
      const response = await api.get('/cards/profile/')
      userProfile.value = response.data
      return response.data
    } catch (err) {
      console.error('프로필 조회 실패:', err)
      return null
    }
  }

  // 사용자 카드 프로필 수정
  async function updateUserProfile(data) {
    try {
      const response = await api.put('/cards/profile/', data)
      userProfile.value = response.data
      return response.data
    } catch (err) {
      console.error('프로필 수정 실패:', err)
      throw err
    }
  }

  return {
    // 기존 상태
    cards,
    currentCard,
    recommendedCards,
    companies,
    isLoading,
    error,
    lastQuery,
    pagination,
    personalizedRecommendations,
    // 마이페이지 상태
    likedCards,
    recentCards,
    recommendationHistory,
    userProfile,
    // 기존 함수
    fetchCompanies,
    fetchCards,
    fetchCardDetail,
    getRecommendations,
    getPersonalizedRecommendations,
    clearRecommendations,
    clearCurrentCard,
    // 마이페이지 함수
    recordEvent,
    toggleLike,
    fetchLikedCards,
    fetchRecentCards,
    fetchRecommendationHistory,
    fetchUserProfile,
    updateUserProfile
  }
})
