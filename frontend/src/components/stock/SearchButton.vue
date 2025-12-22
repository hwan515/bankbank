<template>
  <div class="search-box">
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

      <button class="search-btn" @click="search">
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
  border: 1px solid #efefef;
  border-radius: 16px;
  background: #fff;
  padding: 14px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.08), 0 10px 24px rgba(0,0,0,0.06);
}

/* 헤더 */
.search-head {
  margin-bottom: 10px;
}

.search-head .title {
  font-weight: 900;
  letter-spacing: -0.3px;
  color: #111;
  font-size: 16px;
  margin-bottom: 4px;
}

.search-head .sub {
  font-size: 13px;
  color: #777;
}

/* 입력 영역 */
.search-row {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 8px;
}

.search-input {
  height: 40px;
  border-radius: 12px;
  border: 1px solid #eaeaea;
  padding: 0 12px;
  font-size: 14px;
  outline: none;
}

.search-input:focus {
  border-color: #d8d8d8;
  box-shadow: 0 0 0 0.2rem rgba(0,0,0,0.06);
}

/* 버튼 */
.search-btn {
  height: 40px;
  border-radius: 12px;
  border: 1px solid #111;
  background: #111;
  color: #fff;
  font-weight: 900;
  font-size: 13px;
  padding: 0 14px;
  cursor: pointer;
}

.search-btn:hover {
  background: #000;
}
</style>
