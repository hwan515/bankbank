<template>
    <div class="album py-5 bg-body-tertiary">
        <div class="container">
            <SearchButton />
            <button class="btn btn-sm me-2"
                :class="stockStore.showOnlyFavorite ? 'btn-warning' : 'btn-outline-secondary'"
                @click="stockStore.toggleFavoriteFilter">
                <i :class="stockStore.showOnlyFavorite ? 'bi bi-star-fill' : 'bi bi-star'"></i>
                관심
            </button>
            <div class="row row-cols-1 row-cols-sm-2 row-cols-md-3 g-3">
                <!-- col 단위로 -->
                <div class="col" v-for="video in stockStore.filteredVideoList" :key="video.id?.videoId">
                    <VideoListItem :video="video" />
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { useStockStore } from '@/stores/stock';
import SearchButton from './SearchButton.vue';
import VideoListItem from './VideoListItem.vue';
import { onMounted } from 'vue';

const stockStore = useStockStore()

onMounted(() => {
    stockStore.load()
})


</script>

<style lang="scss" scoped></style>