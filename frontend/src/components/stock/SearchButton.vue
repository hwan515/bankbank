<template>
    <h2>검색창</h2>
    <div class="input-group mb-3">
        <input type="text" class="form-control" placeholder="검색어를 입력하세요." aria-label="Recipient’s username"
            aria-describedby="button-addon2" v-model="keyword">
        <button class="btn btn-outline-secondary" type="button" id="button-addon2" @click="search">Search</button>
    </div>
</template>

<script setup>
import { useStockStore } from '@/stores/stock';
import {ref} from 'vue'

    const stockStore = useStockStore()
    const keyword = ref('')

    const search = () => {
        // 결과 stockStore에 저장하고. 
        stockStore.search(keyword.value)

    }
</script>

<style scoped></style>