<template>
  <div class="video-card" @click="goDetail">
    <!-- 썸네일 -->
    <div class="thumb-wrap">
      <img
        class="thumb"
        :src="video?.snippet?.thumbnails?.medium?.url || video?.snippet?.thumbnails?.default?.url"
        alt="thumbnail"
      />

      <!-- 즐겨찾기 버튼 (썸네일 위) -->
      <button
        class="fav-btn"
        :class="{ on: isFavorite }"
        @click.stop="toggleFavorite"
        aria-label="favorite"
      >
        <i :class="isFavorite ? 'bi bi-star-fill' : 'bi bi-star'"></i>
      </button>
    </div>

    <!-- 내용 -->
    <div class="body">
      <div class="title" :title="video.snippet.title">
        {{ video.snippet.title }}
      </div>

      <div class="meta">
        <span class="channel">{{ video?.snippet?.channelTitle }}</span>
        <span class="view-btn">보기 →</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import 'bootstrap-icons/font/bootstrap-icons.css'
import { useRouter } from 'vue-router'
import { computed } from 'vue'
import { useStockStore } from '@/stores/stock'

const props = defineProps({
  video: Object,
})

const router = useRouter()
const stockStore = useStockStore()

const videoId = computed(() => props.video?.id?.videoId)

const isFavorite = computed(() =>
  stockStore.favoritedIds.has(videoId.value)
)

const goDetail = () => {
  if (!videoId.value) return
  router.push({ name: 'VideoDetail', params: { id: videoId.value } })
}

const toggleFavorite = () => {
  if (!videoId.value) return
  stockStore.toggleFavorite(videoId.value)
}
</script>

<style scoped>
/* 카드 전체 */
.video-card {
  background: #fff;
  border: 1px solid #efefef;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  transition:
    transform 0.15s ease,
    box-shadow 0.15s ease,
    border-color 0.15s ease;
  box-shadow:
    0 1px 2px rgba(0,0,0,0.08),
    0 8px 20px rgba(0,0,0,0.06);
}

.video-card:hover {
  transform: translateY(-2px);
  border-color: #e3e3e3;
  box-shadow:
    0 2px 6px rgba(0,0,0,0.10),
    0 14px 28px rgba(0,0,0,0.08);
}

/* 썸네일 */
.thumb-wrap {
  position: relative;
}

.thumb {
  width: 100%;
  height: 180px;
  object-fit: cover;
  display: block;
}

/* 즐겨찾기 버튼 */
.fav-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 34px;
  height: 34px;
  border-radius: 999px;
  border: 1px solid #e8e8e8;
  background: rgba(255,255,255,0.92);
  display: grid;
  place-items: center;
  cursor: pointer;
  color: #666;
  transition: all 0.15s ease;
}

.fav-btn:hover {
  background: #fff;
  color: #111;
}

.fav-btn.on {
  background: #111;
  color: #ffd43b;
  border-color: #111;
}

/* 본문 */
.body {
  padding: 12px;
  display: grid;
  gap: 8px;
}

/* 제목 */
.title {
  font-size: 14px;
  font-weight: 800;
  color: #111;
  line-height: 1.35;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 메타 */
.meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 12px;
}

.channel {
  color: #777;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 70%;
}

.view-btn {
  font-weight: 800;
  color: #111;
}
</style>
