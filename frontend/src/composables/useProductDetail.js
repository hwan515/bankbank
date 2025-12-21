import { onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useProductsStore } from '@/stores/products'
import { useUserStore } from '@/stores/user'
import { storeToRefs } from 'pinia'

export function useProductDetail(productType) {
  const route = useRoute()
  const productsStore = useProductsStore()
  const userStore = useUserStore()

  const { currentProduct, loading, isSubscribed, subscribing, error } = storeToRefs(productsStore)
  const { isAuthenticated } = storeToRefs(userStore)

  const getJoinDenyText = (value) => {
    const map = { 1: '제한없음', 2: '서민전용', 3: '일부제한' }
    return map[value] || value
  }

  const fetchData = async () => {
    const productId = route.params.id
    await productsStore.fetchProductDetail(productType, productId)

    if (isAuthenticated.value) {
      await productsStore.checkSubscription(productType, productId)
    }
  }

  const toggleSubscription = async () => {
    const result = await productsStore.toggleSubscription(productType, route.params.id)
    if (result.success) {
      alert(result.message)
    } else {
      alert(result.message || '처리 중 오류가 발생했습니다.')
    }
  }

  onMounted(fetchData)

  onUnmounted(() => {
    productsStore.clearCurrentProduct()
  })

  return {
    product: currentProduct,
    loading,
    subscribed: isSubscribed,
    subscribing,
    isAuthenticated,
    error,
    getJoinDenyText,
    toggleSubscription
  }
}
