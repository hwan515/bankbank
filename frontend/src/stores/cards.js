import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from './api'

export const useCardsStore = defineStore('cards', () => {
  // 상태
  const cards = ref([])
  const currentCard = ref(null)
  const recommendedCards = ref([])
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
  async function getRecommendations(query, k = 5) {
    isLoading.value = true
    error.value = null
    lastQuery.value = query

    try {
      const response = await api.post('/cards/card-recommendation/', {
        query,
        k
      })
      recommendedCards.value = response.data
      return response.data
    } catch (err) {
      error.value = err.message || '추천을 가져오는 중 오류가 발생했습니다.'
      recommendedCards.value = []
      throw err
    } finally {
      isLoading.value = false
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

  return {
    cards,
    currentCard,
    recommendedCards,
    companies,
    isLoading,
    error,
    lastQuery,
    pagination,
    fetchCompanies,
    fetchCards,
    fetchCardDetail,
    getRecommendations,
    clearRecommendations,
    clearCurrentCard
  }
})
