<template>
    <!-- 보내줘야됨. -->
    <div class="col" @click="goDetail">
        <div class="card shadow-sm"> <img class="card-img-top"
                :src="video?.snippet?.thumbnails?.medium?.url || video?.snippet?.thumbnails?.default?.url"
                alt="thumbnail" style="height: 225px; object-fit: cover;" />
            <div class="card-body">
                <p class="card-text">{{ video.snippet.title }}</p>
                <div class="d-flex justify-content-between align-items-center">
                    <div class="btn-group">
                        <button type="button" class="btn btn-sm btn-outline-secondary">보기</button>
                        <button type="button" class="btn btn-sm"
                            :class="isFavorite ? 'btn-warning' : 'btn-outline-secondary'" @click.stop="toggleFavorite">
                            <i :class="isFavorite ? 'bi bi-star-fill' : 'bi bi-star'"></i>
                        </button>
                    </div>
                    <small class="text-body-secondary">{{ video?.snippet?.channelTitle }}</small>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
    
import 'bootstrap-icons/font/bootstrap-icons.css'
import { useRouter } from 'vue-router'
import {ref ,computed} from 'vue'
import { useStockStore } from '@/stores/stock'
const props = defineProps({
    video: Object
})
const videoId = computed(() => props.video?.id?.videoId)
const router = useRouter()
const stockStore = useStockStore()


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
    .card {
  cursor: pointer;
}
</style>