<template>
  <div class="my-products ui-card">
    <div class="section-header">
      <h5 class="section-title">내 금융상품</h5>
      <button class="ui-btn ui-btn-ghost" @click="load" :disabled="loading">
        <span v-if="loading" class="spinner-border spinner-border-sm"></span>
        <span v-else>새로고침</span>
      </button>
    </div>

    <div v-if="error" class="alert alert-warning">{{ error }}</div>

    <div class="products-grid">
      <div class="product-card ui-card">
        <div class="card-head">
          <span class="ui-badge ui-badge-primary">정기예금</span>
          <span class="count">{{ subscriptions.deposit.length }}개</span>
        </div>
        <div v-if="!subscriptions.deposit.length" class="empty">가입한 예금이 없습니다.</div>
        <ul v-else class="list">
          <li
            v-for="item in subscriptions.deposit"
            :key="`d-${item.id}`"
            class="list-item"
            @click="goToDeposit(item.id)"
          >
            <div class="name">{{ item.fin_prdt_nm }}</div>
            <div class="bank ui-text-muted">{{ item.kor_co_nm }}</div>
          </li>
        </ul>
      </div>

      <div class="product-card ui-card">
        <div class="card-head">
          <span class="ui-badge ui-badge-success">적금</span>
          <span class="count">{{ subscriptions.saving.length }}개</span>
        </div>
        <div v-if="!subscriptions.saving.length" class="empty">가입한 적금이 없습니다.</div>
        <ul v-else class="list">
          <li
            v-for="item in subscriptions.saving"
            :key="`s-${item.id}`"
            class="list-item"
            @click="goToSaving(item.id)"
          >
            <div class="name">{{ item.fin_prdt_nm }}</div>
            <div class="bank ui-text-muted">{{ item.kor_co_nm }}</div>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useProductsStore } from '@/stores/products'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'

const productsStore = useProductsStore()
const router = useRouter()
const { mySubscriptions, error } = storeToRefs(productsStore)
const loading = ref(false)
const subscriptions = mySubscriptions

async function load() {
  loading.value = true
  try {
    await productsStore.fetchMySubscriptions()
  } catch (e) {
    // 에러는 store.error에 기록됨
  } finally {
    loading.value = false
  }
}

onMounted(load)

function goToDeposit(id) {
  router.push({ name: 'deposit-detail', params: { id } })
}

function goToSaving(id) {
  router.push({ name: 'saving-detail', params: { id } })
}
</script>

<style scoped>
.my-products {
  margin-top: 24px;
  padding: 16px;
  border-radius: 12px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section-title {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
  color: var(--ink);
}

.ui-btn {
  font-size: 12px;
}

.products-grid {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
}

.product-card {
  border-radius: 10px;
  padding: 12px;
}

.card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.count {
  font-size: 12px;
  color: var(--muted);
}

.list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 8px;
}

.list-item {
  padding: 8px 10px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface);
  cursor: pointer;
}

.name {
  font-weight: 700;
  font-size: 13px;
  color: var(--ink);
}

.bank {
  font-size: 12px;
}

.empty {
  font-size: 12px;
  color: var(--muted);
}
</style>
