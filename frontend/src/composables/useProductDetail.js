import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useProductsStore } from '@/stores/products'
import { useAccountStore } from '@/stores/account'
import { useToastStore } from '@/stores/toast'
import { storeToRefs } from 'pinia'

export function useProductDetail(productType) {
  const route = useRoute()
  const productsStore = useProductsStore()
  const toastStore = useToastStore()
  const { currentProduct, loading, isSubscribed, subscribing, error } = storeToRefs(productsStore)
  const accountStore = useAccountStore()
  const { isLogin } = storeToRefs(accountStore)
  const isAuthenticated = isLogin

  const selectedTerm = ref('')
  const selectedSavingType = ref('')
  const monthlyAmount = ref(null)
  const subscriptionInfo = ref({ subscribed: false })

  const allowedTerms = [6, 12, 24, 36]

  const availableTerms = computed(() => {
    const product = currentProduct.value
    if (!product) return []
    const options = productType === 'deposit'
      ? product.options || []
      : product.saving_options || []
    const terms = options
      .map((option) => Number(option.save_trm))
      .filter((term) => Number.isFinite(term))
    const filtered = terms.filter((term) => allowedTerms.includes(term))
    return Array.from(new Set(filtered)).sort((a, b) => a - b)
  })

  const availableSavingTypes = computed(() => {
    if (productType !== 'saving') return []
    const product = currentProduct.value
    if (!product) return []
    const types = (product.saving_options || [])
      .map((option) => option.rsrv_type_nm)
      .filter((value) => value)
    return Array.from(new Set(types))
  })

  const getJoinDenyText = (value) => {
    const map = { 1: '제한없음', 2: '서민전용', 3: '일부제한' }
    return map[value] || value
  }

  const applyDefaultSelections = (subscriptionData = null) => {
    if (subscriptionData?.subscribed && subscriptionData.term_months) {
      selectedTerm.value = String(subscriptionData.term_months)
    }
    if (!selectedTerm.value) {
      const terms = availableTerms.value
      if (terms.includes(12)) {
        selectedTerm.value = '12'
      } else if (terms.length) {
        selectedTerm.value = String(terms[0])
      }
    }

    if (productType === 'saving') {
      if (subscriptionData?.subscribed && subscriptionData.rsrv_type) {
        selectedSavingType.value = subscriptionData.rsrv_type
      }
      if (subscriptionData?.subscribed && subscriptionData.monthly_amount != null) {
        monthlyAmount.value = subscriptionData.monthly_amount
      }

      if (!selectedSavingType.value && availableSavingTypes.value.length) {
        selectedSavingType.value = availableSavingTypes.value[0]
      }
    }
  }

  const fetchData = async () => {
    const productId = route.params.id
    await productsStore.fetchProductDetail(productType, productId)

    if (isAuthenticated.value) {
      const subscriptionData = await productsStore.checkSubscription(productType, productId)
      subscriptionInfo.value = subscriptionData || { subscribed: false }
      applyDefaultSelections(subscriptionData)
    } else {
      subscriptionInfo.value = { subscribed: false }
      applyDefaultSelections()
    }
  }

  const toggleSubscription = async () => {
    const termValue = Number(selectedTerm.value)
    if (!isSubscribed.value) {
      if (!Number.isFinite(termValue) || !allowedTerms.includes(termValue)) {
        alert('가입 기간을 선택해 주세요. (6, 12, 24, 36개월)')
        return
      }
    }
    const payload = {
      term_months: Number.isFinite(termValue) ? termValue : null,
    }
    if (productType === 'saving') {
      if (selectedSavingType.value) payload.rsrv_type = selectedSavingType.value
      if (monthlyAmount.value) payload.monthly_amount = monthlyAmount.value
    }

    const result = await productsStore.toggleSubscription(
      productType,
      route.params.id,
      payload
    )
    if (result.success) {
      alert(result.message)
      const subscriptionData = await productsStore.checkSubscription(productType, route.params.id)
      subscriptionInfo.value = subscriptionData || { subscribed: false }
    } else {
      alert(result.message || '처리 중 오류가 발생했습니다.')
    }
  }

  const currentTerm = computed(() => {
    const term = subscriptionInfo.value?.term_months
    return Number.isFinite(Number(term)) ? Number(term) : null
  })

  const canUpdateTerm = computed(() => {
    if (!isSubscribed.value) return false
    if (!selectedTerm.value) return false
    const selected = Number(selectedTerm.value)
    if (!Number.isFinite(selected)) return false
    if (!allowedTerms.includes(selected)) return false
    return true
  })

  const updateSubscriptionTerm = async () => {
    if (!canUpdateTerm.value) return
    const selected = Number(selectedTerm.value)
    const termChanged = Number.isFinite(selected) && selected !== currentTerm.value
    let typeChanged = false
    let amountChanged = false
    if (productType === 'saving') {
      const currentType = subscriptionInfo.value?.rsrv_type || ''
      typeChanged = (selectedSavingType.value || '') !== currentType
      const currentAmount = subscriptionInfo.value?.monthly_amount ?? null
      const selectedAmount = monthlyAmount.value == null ? null : Number(monthlyAmount.value)
      amountChanged = selectedAmount !== currentAmount
    }
    if (!termChanged && !typeChanged && !amountChanged) {
      toastStore.push('변경 필요 없음', { type: 'info' })
      return
    }
    if (!allowedTerms.includes(selected)) {
      alert('가입 기간은 6/12/24/36개월만 가능합니다.')
      return
    }
    const payload = { term_months: selected }
    if (productType === 'saving') {
      if (selectedSavingType.value) payload.rsrv_type = selectedSavingType.value
      if (monthlyAmount.value) payload.monthly_amount = monthlyAmount.value
    }
    const result = await productsStore.updateSubscription(
      productType,
      route.params.id,
      payload
    )
    if (result.success) {
      alert('기간이 변경되었습니다.')
      const subscriptionData = await productsStore.checkSubscription(productType, route.params.id)
      subscriptionInfo.value = subscriptionData || { subscribed: false }
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
    selectedTerm,
    selectedSavingType,
    monthlyAmount,
    availableTerms,
    availableSavingTypes,
    canUpdateTerm,
    getJoinDenyText,
    toggleSubscription,
    updateSubscriptionTerm
  }
}
