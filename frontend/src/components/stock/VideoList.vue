<template>
  <div class="page-shell">
    <div class="container py-4">
      <!-- ✅ 상단 툴바 (미니멀) -->
      <div class="toolbar ui-card">
        <div class="toolbar-left">
          <div class="title serif-title">관심 종목 영상</div>
          <div class="sub">검색하고, 관심 영상만 모아볼 수 있어요.</div>
        </div>

        <div class="toolbar-right">
          <SearchButton />

          <button
            class="btn-mini"
            :class="stockStore.showOnlyFavorite ? 'is-on' : ''"
            @click="stockStore.toggleFavoriteFilter"
          >
            <i :class="stockStore.showOnlyFavorite ? 'bi bi-star-fill' : 'bi bi-star'"></i>
            관심
          </button>
        </div>
      </div>

      <!-- ✅ 리스트 영역 -->
      <div class="grid">
        <div class="col" v-for="video in stockStore.filteredVideoList" :key="video.id?.videoId">
          <VideoListItem :video="video" />
        </div>
      </div>

      <!-- ✅ 비었을 때 -->
      <div v-if="!stockStore.filteredVideoList?.length" class="empty">
        <div class="empty-title">표시할 영상이 없어요</div>
        <div class="empty-sub">검색하거나, 관심(★) 필터를 해제해보세요.</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useStockStore } from '@/stores/stock'
import SearchButton from './SearchButton.vue'
import VideoListItem from './VideoListItem.vue'
import { onMounted } from 'vue'

const stockStore = useStockStore()

onMounted(() => {
  stockStore.load()
})
</script>

<style scoped>
/* 배경 톤: 미니멀 */
.page-shell {
  min-height: 100%;
  background:
    radial-gradient(900px 300px at 10% 0%, rgba(27, 95, 122, 0.10), transparent 60%),
    linear-gradient(180deg, var(--bg-alt) 0%, var(--bg) 100%);
}

/* 상단 툴바 */
.toolbar {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 12px;
  padding: 16px;
  margin-bottom: 14px;
}

.toolbar-left .title {
  font-weight: 700;
  letter-spacing: -0.3px;
  color: var(--ink);
  font-size: clamp(16px, 1.6vw, 20px);
  margin-bottom: 4px;
}

.toolbar-left .sub {
  font-size: 13px;
  color: var(--muted);
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

/* 관심 버튼 미니멀 */
.btn-mini {
  height: var(--btn-h);
  padding: 0 var(--btn-pad-x);
  border-radius: 999px;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--ink-soft);
  font-weight: 600;
  font-size: 13px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
}

.btn-mini:hover {
  background: var(--bg-alt);
  color: var(--ink);
}

.btn-mini.is-on {
  background: var(--accent);
  color: #fff;
  border-color: var(--accent);
}

/* 그리드: 기존 bootstrap 느낌 유지하되, 더 미니멀 */
.grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

/* 반응형 */
@media (max-width: 992px) {
  .grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .toolbar {
    align-items: flex-start;
  }
}

@media (max-width: 576px) {
  .grid {
    grid-template-columns: 1fr;
  }
  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }
  .toolbar-right {
    justify-content: flex-end;
  }
}

/* empty state */
.empty {
  margin-top: 14px;
  padding: 18px;
  border: 1px solid var(--border);
  border-radius: 16px;
  background: var(--surface);
  text-align: center;
  color: var(--muted);
}

.empty-title {
  font-weight: 700;
  color: var(--ink);
  margin-bottom: 6px;
}

.empty-sub {
  font-size: 13px;
  color: var(--muted);
}
</style>
