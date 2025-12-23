import { ref } from 'vue'
import { defineStore } from 'pinia'
import api from './api'

export const useProductsStore = defineStore('products', () => {
  // 캐시 TTL 설정 (5분)
  const CACHE_TTL = 5 * 60 * 1000

  // 목록 관련
  const depositProducts = ref([])
  const savingProducts = ref([])
  const allDepositProducts = ref([]) // 전체 예금 목록 캐시
  const allSavingProducts = ref([]) // 전체 적금 목록 캐시
  const banks = ref([])
  const subscribedDeposits = ref([])
  const subscribedSavings = ref([])

  // 캐시 타임스탬프
  const cacheTimestamps = ref({
    banks: null,
    deposit: null,
    saving: null
  })

  // 상세 관련
  const currentProduct = ref(null)
  const isSubscribed = ref(false)

  // UI 상태
  const loading = ref(false)
  const subscribing = ref(false)
  const error = ref(null)
  const subscriptionsLoading = ref(false)
  const subscriptionsError = ref(null)

  // 캐시 만료 여부 확인
  function isCacheExpired(key) {
    const timestamp = cacheTimestamps.value[key]
    if (!timestamp) return true
    return Date.now() - timestamp > CACHE_TTL
  }

  // 은행 목록 조회
  async function fetchBanks() {
    // 캐시가 유효하면 기존 데이터 반환
    if (banks.value.length > 0 && !isCacheExpired('banks')) {
      return banks.value
    }
    try {
      const response = await api.get('/products/banks/')
      banks.value = response.data
      cacheTimestamps.value.banks = Date.now()
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  // 상품 목록 조회 (캐싱 + TTL)
  async function fetchProducts(productType, filters = {}) {
    const hasFilters = !!(filters.bank || filters.search || filters.ordering)

    // 필터가 없고, 캐시가 유효한 경우 API 호출을 건너뜀
    if (!hasFilters && !isCacheExpired(productType)) {
      if (productType === 'deposit' && allDepositProducts.value.length > 0) {
        depositProducts.value = allDepositProducts.value
        return depositProducts.value
      }
      if (productType === 'saving' && allSavingProducts.value.length > 0) {
        savingProducts.value = allSavingProducts.value
        return savingProducts.value
      }
    }

    loading.value = true
    error.value = null

    try {
      const endpoint =
        productType === 'deposit'
          ? '/products/deposit-products/'
          : '/products/saving-products/'

      const params = new URLSearchParams()
      if (filters.bank) params.append('bank', filters.bank)
      if (filters.search) params.append('search', filters.search)
      if (filters.ordering) params.append('ordering', filters.ordering)

      const response = await api.get(`${endpoint}?${params.toString()}`)


      // 필터가 없으면 결과를 전체 목록 캐시에 저장 + 타임스탬프 갱신
      if (productType === 'deposit') {
        depositProducts.value = response.data
        if (!hasFilters) {
          allDepositProducts.value = response.data
          cacheTimestamps.value.deposit = Date.now()
        }
      } else {
        savingProducts.value = response.data
        if (!hasFilters) {
          allSavingProducts.value = response.data
          cacheTimestamps.value.saving = Date.now()
        }
      }

      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // 상품 상세 조회
  async function fetchProductDetail(productType, productId) {
    loading.value = true
    error.value = null
    currentProduct.value = null

    try {
      const endpoint =
        productType === 'deposit'
          ? `/products/deposit-products/${productId}/`
          : `/products/saving-products/${productId}/`

      const response = await api.get(endpoint)
      currentProduct.value = response.data
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // 가입 여부 확인
  async function checkSubscription(productType, productId) {
    try {
      const response = await api.get(
        `/products/check-subscription/${productType}/${productId}/`
      )
      isSubscribed.value = response.data.subscribed
      return response.data.subscribed
    } catch (err) {
      if (err.status !== 401) {
        error.value = err.message
      }
      isSubscribed.value = false
      return false
    }
  }

  // 가입/해제 토글
  async function toggleSubscription(productType, productId) {
    subscribing.value = true

    try {
      const endpoint =
        productType === 'deposit'
          ? `/products/deposit-products/${productId}/subscribe/`
          : `/products/saving-products/${productId}/subscribe/`

      const response = await api.post(endpoint)
      isSubscribed.value = response.data.subscribed

      // 가입 해제 시 가입 목록에서 제거
      if (!response.data.subscribed) {
        if (productType === 'deposit') {
          subscribedDeposits.value = subscribedDeposits.value.filter((p) => p.id !== productId)
        } else {
          subscribedSavings.value = subscribedSavings.value.filter((p) => p.id !== productId)
        }
      }

      return {
        success: true,
        subscribed: response.data.subscribed,
        message: response.data.message
      }
    } catch (err) {
      error.value = err.message
      return {
        success: false,
        message: err.message
      }
    } finally {
      subscribing.value = false
    }
  }

  // 상태 초기화
  function clearCurrentProduct() {
    currentProduct.value = null
    isSubscribed.value = false
    error.value = null
  }

  function clearError() {
    error.value = null
  }

  // 가입 목록 조회
  async function fetchSubscriptions() {
    subscriptionsLoading.value = true
    subscriptionsError.value = null
    try {
      const res = await api.get('/products/subscriptions/')
      subscribedDeposits.value = res.data.deposits || []
      subscribedSavings.value = res.data.savings || []
      return res.data
    } catch (e) {
      subscriptionsError.value = e.message
      throw e
    } finally {
      subscriptionsLoading.value = false
    }
  }

  return {
    // State
    depositProducts,
    savingProducts,
    banks,
    currentProduct,
    isSubscribed,
    loading,
    subscribing,
    error,
    subscribedDeposits,
    subscribedSavings,
    subscriptionsLoading,
    subscriptionsError,

    // Actions
    fetchBanks,
    fetchProducts,
    fetchProductDetail,
    checkSubscription,
    toggleSubscription,
    clearCurrentProduct,
    clearError,
    fetchSubscriptions
  }
})
