<template>
  <div class="search-box ui-card">
    <div class="search-head">
      <div class="title">검색</div>
      <div class="sub">관심 종목·영상 키워드를 입력해보세요.</div>
    </div>

    <div class="search-row">
      <input
        type="text"
        class="search-input"
        placeholder="검색어를 입력하세요"
        v-model.trim="keyword"
        @keyup.enter="search"
      />

      <button class="ui-btn ui-btn-primary" @click="search">
        검색
      </button>
    </div>
  </div>
</template>

<script setup>
import { useStockStore } from '@/stores/stock'
import { ref } from 'vue'

const stockStore = useStockStore()
const keyword = ref('')

const search = () => {
  if (!keyword.value?.trim()) return
  stockStore.search(keyword.value)
}
</script>

<style scoped>
.search-box {
  padding: 14px;
}

/* 헤더 */
.search-head {
  margin-bottom: 10px;
}

.search-head .title {
  font-weight: 700;
  letter-spacing: -0.3px;
  color: var(--ink);
  font-size: 16px;
  margin-bottom: 4px;
}

.search-head .sub {
  font-size: 13px;
  color: var(--muted);
}

/* 입력 영역 */
.search-row {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 8px;
}

.search-input {
  height: 40px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  padding: 0 12px;
  font-size: 14px;
  outline: none;
}

.search-input:focus {
  border-color: rgba(27, 95, 122, 0.5);
  box-shadow: 0 0 0 0.2rem rgba(27, 95, 122, 0.15);
}

/* 버튼 */
</style>
