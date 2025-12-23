<template>
  <section class="sub-section">
    <div class="head">
      <div>
        <p class="eyebrow">가입한 상품</p>
        <h2 class="title">내 예·적금</h2>
        <p class="sub">가입한 금융 상품을 확인하고 해제할 수 있습니다.</p>
      </div>
      <button class="btn-line" @click="refresh" :disabled="loading">
        {{ loading ? '불러오는 중...' : '새로고침' }}
      </button>
    </div>

    <div v-if="error" class="alert alert-danger small mb-3">오류: {{ error }}</div>

    <div class="grid">
      <div class="card">
        <div class="card-head">
          <h3>정기예금</h3>
          <span class="pill">{{ deposits.length }}개</span>
        </div>
        <div v-if="!deposits.length" class="empty">가입한 예금이 없습니다.</div>
        <ul v-else class="list">
          <li v-for="item in deposits" :key="item.id" class="list-item">
            <div>
              <div class="name">{{ item.fin_prdt_nm }}</div>
              <div class="bank">{{ item.kor_co_nm }}</div>
            </div>
            <button class="btn-text" @click="toggle('deposit', item.id)" :disabled="loading">
              해제
            </button>
          </li>
        </ul>
      </div>

      <div class="card">
        <div class="card-head">
          <h3>적금</h3>
          <span class="pill">{{ savings.length }}개</span>
        </div>
        <div v-if="!savings.length" class="empty">가입한 적금이 없습니다.</div>
        <ul v-else class="list">
          <li v-for="item in savings" :key="item.id" class="list-item">
            <div>
              <div class="name">{{ item.fin_prdt_nm }}</div>
              <div class="bank">{{ item.kor_co_nm }}</div>
            </div>
            <button class="btn-text" @click="toggle('saving', item.id)" :disabled="loading">
              해제
            </button>
          </li>
        </ul>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useProductsStore } from '@/stores/products'

const productsStore = useProductsStore()

const deposits = computed(() => productsStore.subscribedDeposits)
const savings = computed(() => productsStore.subscribedSavings)
const loading = computed(() => productsStore.subscriptionsLoading || productsStore.subscribing)
const error = computed(() => productsStore.subscriptionsError)

const refresh = async () => {
  try {
    await productsStore.fetchSubscriptions()
  } catch (e) {
    // error는 store에서 관리
  }
}

const toggle = async (type, id) => {
  await productsStore.toggleSubscription(type, id)
  await productsStore.fetchSubscriptions()
}

onMounted(refresh)
</script>

<style scoped>
.sub-section {
  margin-top: 24px;
  border: 1px solid #ececec;
  border-radius: 14px;
  padding: 16px;
  background: #fff;
  box-shadow: 0 1px 2px rgba(0,0,0,0.08), 0 10px 24px rgba(0,0,0,0.05);
}

.head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.eyebrow {
  font-size: 12px;
  color: #666;
  margin: 0;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.title {
  margin: 4px 0;
  font-size: 20px;
  font-weight: 900;
}

.sub {
  margin: 0;
  color: #666;
  font-size: 13px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.card {
  border: 1px solid #efefef;
  border-radius: 12px;
  padding: 12px;
  background: #fafafa;
}

.card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.pill {
  background: #fff;
  border: 1px solid #e3e3e3;
  border-radius: 999px;
  padding: 4px 8px;
  font-size: 12px;
  color: #444;
}

.list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 8px;
}

.list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 10px;
  padding: 10px;
}

.name {
  font-weight: 800;
  color: #111;
}

.bank {
  font-size: 12px;
  color: #666;
}

.empty {
  text-align: center;
  color: #777;
  padding: 10px 0;
}

.btn-line {
  border-radius: 10px;
  border: 1px solid #111;
  background: #fff;
  color: #111;
  font-weight: 800;
  padding: 8px 12px;
}

.btn-text {
  border: none;
  background: transparent;
  color: #d00000;
  font-weight: 800;
}

@media (max-width: 768px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>
