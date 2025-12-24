<template>
  <section class="sub-section ui-card">
    <div class="head">
      <div>
        <p class="eyebrow">가입한 상품</p>
        <h2 class="title serif-title">내 예·적금</h2>
        <p class="sub">가입한 금융 상품을 확인하고 해제할 수 있습니다.</p>
      </div>
      <button class="ui-btn ui-btn-ghost" @click="refresh" :disabled="loading">
        {{ loading ? '불러오는 중...' : '새로고침' }}
      </button>
    </div>

    <div class="filters">
      <div class="field">
        <label class="label">은행</label>
        <select v-model="filterBank" class="select">
          <option value="">전체</option>
          <option v-for="bank in bankOptions" :key="bank" :value="bank">{{ bank }}</option>
        </select>
      </div>
      <div class="field">
        <label class="label">기간</label>
        <select v-model="filterTerm" class="select">
          <option value="">전체</option>
          <option value="6">6개월</option>
          <option value="12">12개월</option>
          <option value="24">24개월</option>
          <option value="36">36개월</option>
        </select>
      </div>
      <div class="field">
        <label class="label">정렬</label>
        <select v-model="sortKey" class="select">
          <option value="created_desc">최신 가입</option>
          <option value="created_asc">가입 오래된 순</option>
          <option value="bank_asc">은행 A→Z</option>
          <option value="bank_desc">은행 Z→A</option>
          <option value="term_asc">기간 짧은 순</option>
          <option value="term_desc">기간 긴 순</option>
        </select>
      </div>
    </div>

    <div v-if="error" class="alert alert-danger small mb-3">오류: {{ error }}</div>

    <div class="grid">
      <div class="card ui-card">
        <div class="card-head">
          <h3>정기예금</h3>
          <span class="pill">{{ displayDeposits.length }}개</span>
        </div>
        <div v-if="!displayDeposits.length" class="empty">가입한 예금이 없습니다.</div>
        <ul v-else class="list">
          <li v-for="item in displayDeposits" :key="item.id" class="list-item">
            <div class="info">
              <div class="name">{{ item.fin_prdt_nm }}</div>
              <div class="bank">{{ item.kor_co_nm }}</div>
              <div class="meta">기간: {{ item.term_months ? item.term_months + '개월' : '미설정' }}</div>
            </div>
            <div class="actions">
              <select
                v-model="editTerms[termKey('deposit', item.id)]"
                class="mini-select"
              >
                <option value="">선택</option>
                <option value="6">6개월</option>
                <option value="12">12개월</option>
                <option value="24">24개월</option>
                <option value="36">36개월</option>
              </select>
              <button
                class="btn-text neutral"
                @click="updateTerm('deposit', item)"
                :disabled="loading || !canUpdateTerm('deposit', item)"
              >
                기간 변경
              </button>
              <button class="btn-text danger" @click="toggle('deposit', item.id)" :disabled="loading">
                해제
              </button>
            </div>
          </li>
        </ul>
      </div>

      <div class="card ui-card">
        <div class="card-head">
          <h3>적금</h3>
          <span class="pill">{{ displaySavings.length }}개</span>
        </div>
        <div v-if="!displaySavings.length" class="empty">가입한 적금이 없습니다.</div>
        <ul v-else class="list">
          <li v-for="item in displaySavings" :key="item.id" class="list-item">
            <div class="info">
              <div class="name">{{ item.fin_prdt_nm }}</div>
              <div class="bank">{{ item.kor_co_nm }}</div>
              <div class="meta">
                기간: {{ item.term_months ? item.term_months + '개월' : '미설정' }}
                <span v-if="item.rsrv_type"> · {{ item.rsrv_type }}</span>
                <span v-if="item.monthly_amount"> · 월 {{ Number(item.monthly_amount).toLocaleString() }}원</span>
              </div>
            </div>
            <div class="actions">
              <select
                v-model="editTerms[termKey('saving', item.id)]"
                class="mini-select"
              >
                <option value="">선택</option>
                <option value="6">6개월</option>
                <option value="12">12개월</option>
                <option value="24">24개월</option>
                <option value="36">36개월</option>
              </select>
              <button
                class="btn-text neutral"
                @click="updateTerm('saving', item)"
                :disabled="loading || !canUpdateTerm('saving', item)"
              >
                기간 변경
              </button>
              <button class="btn-text danger" @click="toggle('saving', item.id)" :disabled="loading">
                해제
              </button>
            </div>
          </li>
        </ul>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useProductsStore } from '@/stores/products'
import { useToastStore } from '@/stores/toast'

const productsStore = useProductsStore()
const toastStore = useToastStore()

const deposits = computed(() => productsStore.subscribedDeposits)
const savings = computed(() => productsStore.subscribedSavings)
const loading = computed(() => productsStore.subscriptionsLoading || productsStore.subscribing)
const error = computed(() => productsStore.subscriptionsError)

const filterBank = ref('')
const filterTerm = ref('')
const sortKey = ref('created_desc')
const editTerms = ref({})

const bankOptions = computed(() => {
  const values = new Set()
  deposits.value.forEach((item) => {
    if (item.kor_co_nm) values.add(item.kor_co_nm)
  })
  savings.value.forEach((item) => {
    if (item.kor_co_nm) values.add(item.kor_co_nm)
  })
  return Array.from(values).sort()
})

const displayDeposits = computed(() => {
  let items = deposits.value || []
  if (filterBank.value) {
    items = items.filter((item) => item.kor_co_nm === filterBank.value)
  }
  if (filterTerm.value) {
    items = items.filter((item) => String(item.term_months || '') === filterTerm.value)
  }
  return sortItems(items)
})

const displaySavings = computed(() => {
  let items = savings.value || []
  if (filterBank.value) {
    items = items.filter((item) => item.kor_co_nm === filterBank.value)
  }
  if (filterTerm.value) {
    items = items.filter((item) => String(item.term_months || '') === filterTerm.value)
  }
  return sortItems(items)
})

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

const termKey = (type, id) => `${type}-${id}`

const canUpdateTerm = (type, item) => {
  const key = termKey(type, item.id)
  const value = editTerms.value[key]
  if (!value) return false
  const next = Number(value)
  if (!Number.isFinite(next)) return false
  return true
}

const updateTerm = async (type, item) => {
  const key = termKey(type, item.id)
  const termValue = editTerms.value[key]
  if (!termValue) {
    alert('기간을 선택해 주세요.')
    return
  }
  const current = item.term_months ? Number(item.term_months) : null
  const next = Number(termValue)
  if (Number.isFinite(next) && next === current) {
    toastStore.push('변경 필요 없음', { type: 'info' })
    return
  }
  const result = await productsStore.updateSubscription(type, item.id, {
    term_months: termValue
  })
  if (result.success) {
    await productsStore.fetchSubscriptions()
  } else {
    alert(result.message || '처리 중 오류가 발생했습니다.')
  }
}

const sortItems = (items) => {
  const list = [...items]
  const byTerm = (a, b, dir) => {
    const termA = a.term_months ? Number(a.term_months) : null
    const termB = b.term_months ? Number(b.term_months) : null
    if (termA == null && termB == null) return 0
    if (termA == null) return 1
    if (termB == null) return -1
    return dir * (termA - termB)
  }
  const byBank = (a, b, dir) => {
    const nameA = a.kor_co_nm || ''
    const nameB = b.kor_co_nm || ''
    return dir * nameA.localeCompare(nameB)
  }
  const byCreated = (a, b, dir) => {
    const timeA = a.created_at ? new Date(a.created_at).getTime() : null
    const timeB = b.created_at ? new Date(b.created_at).getTime() : null
    if (timeA == null && timeB == null) return 0
    if (timeA == null) return 1
    if (timeB == null) return -1
    return dir * (timeA - timeB)
  }

  switch (sortKey.value) {
    case 'created_asc':
      return list.sort((a, b) => byCreated(a, b, 1))
    case 'created_desc':
      return list.sort((a, b) => byCreated(a, b, -1))
    case 'bank_asc':
      return list.sort((a, b) => byBank(a, b, 1))
    case 'bank_desc':
      return list.sort((a, b) => byBank(a, b, -1))
    case 'term_asc':
      return list.sort((a, b) => byTerm(a, b, 1))
    case 'term_desc':
      return list.sort((a, b) => byTerm(a, b, -1))
    default:
      return list
  }
}

watch([deposits, savings], () => {
  const next = { ...editTerms.value }
  deposits.value.forEach((item) => {
    const key = termKey('deposit', item.id)
    if (next[key] == null) {
      next[key] = item.term_months ? String(item.term_months) : ''
    }
  })
  savings.value.forEach((item) => {
    const key = termKey('saving', item.id)
    if (next[key] == null) {
      next[key] = item.term_months ? String(item.term_months) : ''
    }
  })
  editTerms.value = next
}, { immediate: true })

onMounted(refresh)
</script>

<style scoped>
.sub-section {
  margin-top: 24px;
  border-radius: 14px;
  padding: 16px;
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
  color: var(--muted);
  margin: 0;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.title {
  margin: 4px 0;
  font-size: 20px;
  font-weight: 700;
  color: var(--ink);
}

.sub {
  margin: 0;
  color: var(--muted);
  font-size: 13px;
}

.filters {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  margin-bottom: 12px;
}
.field { display: grid; gap: 6px; }
.label { font-size: 12px; font-weight: 700; color: var(--ink); }
.select {
  height: 34px;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: var(--surface);
  padding: 0 10px;
  font-size: 12px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.card {
  border-radius: 12px;
  padding: 12px;
  background: var(--bg-alt);
  box-shadow: none;
}

.card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.pill {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 4px 8px;
  font-size: 12px;
  color: var(--ink-soft);
}

.list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 8px;
}

.list-item {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 10px;
  align-items: center;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 10px;
}

.actions {
  display: grid;
  gap: 6px;
  justify-items: end;
}
.mini-select {
  height: 28px;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: var(--surface);
  padding: 0 8px;
  font-size: 12px;
}

.name {
  font-weight: 700;
  color: var(--ink);
}

.bank {
  font-size: 12px;
  color: var(--muted);
}
.meta {
  font-size: 12px;
  color: var(--muted);
}

.empty {
  text-align: center;
  color: var(--muted);
  padding: 10px 0;
}


.btn-text {
  border: none;
  background: transparent;
  font-weight: 800;
  height: var(--btn-h-sm);
  padding: 0 8px;
}
.btn-text.neutral { color: var(--ink-soft); }
.btn-text.danger { color: #d00000; }

@media (max-width: 768px) {
  .grid {
    grid-template-columns: 1fr;
  }
  .filters {
    grid-template-columns: 1fr;
  }
}
</style>
